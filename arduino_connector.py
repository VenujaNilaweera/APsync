import serial
import time
import serial.tools.list_ports
import threading
from collections import deque

class ArduinoConnector:
    def __init__(self, valid_username, baudrate=9600, timeout=1.0, max_retries=3, retry_delay=3):
        self.valid_username = valid_username
        self.baudrate = baudrate
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.port = None
        self.connection = None
        self.is_connected = False
        self.disconnect_callback = None
        self.reconnect_callback = None
        self.auto_reconnect = True
        self.reconnect_thread = None
        self.reconnecting = False
        self.running = True
        self.response_queue = deque(maxlen=20)  # Store last 20 responses
        
        # Start the background monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_connection)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def set_disconnect_callback(self, callback):
        """
        Set a callback function to be called when disconnection is detected.
        
        Args:
            callback: Function to call on disconnection (will receive port as parameter)
        """
        self.disconnect_callback = callback
    
    def set_reconnect_callback(self, callback):
        """
        Set a callback function to be called when reconnection is successful.
        
        Args:
            callback: Function to call on reconnection (will receive port as parameter)
        """
        self.reconnect_callback = callback
    
    def enable_auto_reconnect(self, enable=True):
        """Enable or disable auto-reconnect feature"""
        self.auto_reconnect = enable
    
    def _monitor_connection(self):
        """Background thread to monitor connection and attempt reconnection"""
        check_interval = 2  # Check connection every 2 seconds
        
        while self.running:
            if self.is_connected:
                # Only check if we think we're connected and not already reconnecting
                if not self.reconnecting and not self.check_connection(silent=True):
                    # Connection lost, attempt reconnection if enabled
                    if self.auto_reconnect:
                        self._attempt_reconnect()
            
            # Wait before next check
            time.sleep(check_interval)
    
    def _attempt_reconnect(self):
        """Attempt to reconnect to the Arduino in a separate thread"""
        if self.reconnecting:
            return  # Already trying to reconnect
            
        self.reconnecting = True
        
        # Start reconnection in a new thread
        if self.reconnect_thread is None or not self.reconnect_thread.is_alive():
            self.reconnect_thread = threading.Thread(target=self._reconnect_worker)
            self.reconnect_thread.daemon = True
            self.reconnect_thread.start()
    
    def _reconnect_worker(self):
        """Worker thread for reconnection attempts"""
        print("🔄 Attempting to reconnect to Arduino...")
        try:
            # Try to reconnect
            result = self.connect(silent=True)
            
            if result:
                print(f"✅ Successfully reconnected to Arduino on {result}")
                if self.reconnect_callback:
                    self.reconnect_callback(result)
            else:
                print("❌ Reconnection failed. Will try again later.")
        finally:
            self.reconnecting = False
    
    def connect(self, skip_bluetooth=True, silent=False):
        """
        Try to connect to Arduino on available COM ports.
        
        Args:
            skip_bluetooth (bool): Whether to skip Bluetooth ports
            silent (bool): Whether to suppress most console output
            
        Returns:
            str or None: COM port path if connection successful, None otherwise
        """
        retries = 0
        while retries < self.max_retries and self.running:
            ports = serial.tools.list_ports.comports()
            
            for port in ports:
                if skip_bluetooth and ('Bluetooth' in port.description or 'BT' in port.device):
                    if not silent:
                        print(f"Skipping Bluetooth port {port.device}...")
                    continue
                
                try:
                    # Attempt to connect to the COM port
                    ser = serial.Serial(port.device, self.baudrate, timeout=self.timeout)
                    if not silent:
                        print(f"Trying to connect to {port.device}...")
                    
                    # Clear any existing data
                    ser.reset_input_buffer()
                    ser.reset_output_buffer()
                    time.sleep(0.1)  # Short delay to ensure buffers are cleared
                    
                    # Send the username request command
                    ser.write(b"Send your username:\n")
                    
                    # Wait for a response (up to the specified timeout)
                    start_time = time.time()
                    while time.time() - start_time < self.timeout:
                        if ser.in_waiting > 0:
                            raw_data = ser.read(ser.in_waiting)
                            
                            try:
                                response = raw_data.decode('utf-8').strip()
                                if not silent:
                                    print(f"Received response: '{response}'")
                                
                                # Check if the valid username is in the response
                                if self.valid_username in response:
                                    if not silent:
                                        print(f"Board connected with username: {self.valid_username}")
                                        print(f"Connected to COM port: {port.device}")
                                    
                                    # Send authentication success acknowledgment to Arduino
                                    ser.write(b"AUTH_SUCCESS\n")
                                    if not silent:
                                        print("Sent authentication success message to Arduino")
                                    
                                    # Give Arduino time to process the message and blink LED
                                    time.sleep(0.5)
                                    
                                    self.port = port.device
                                    self.connection = ser
                                    self.is_connected = True
                                    return port.device
                                else:
                                    if not silent:
                                        print(f"Invalid username: {response}")
                                    break
                            except Exception as e:
                                if not silent:
                                    print(f"Error decoding data: {e}")
                                break
                    
                    # Timeout after checking port
                    if not silent:
                        print(f"No valid response from {port.device}. Moving to next port.")
                    ser.close()
                    
                except serial.SerialException as e:
                    if not silent:
                        print(f"Port {port.device} is already in use or unavailable: {e}")
                    continue
            
            # If no board was found, retry after a delay
            retries += 1
            if retries < self.max_retries:
                if not silent:
                    print(f"Attempt {retries}/{self.max_retries} failed. Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
        
        if not silent:
            print("Board not connected. Please ensure the Arduino is connected properly.")
        return None
    
    def check_connection(self, silent=False):
        """
        Check if the Arduino is still connected.
        
        Args:
            silent (bool): Whether to suppress console output
            
        Returns:
            bool: True if connected, False otherwise
        """
        if not self.connection:
            return False
            
        try:
            # Check if port is still available
            ports = [port.device for port in serial.tools.list_ports.comports()]
            if self.port not in ports:
                self._handle_disconnection("Port no longer available", silent)
                return False
                
            # Try to write a small ping to test connection
            self.connection.write(b"\n")
            return True
        except (serial.SerialException, IOError, OSError, PermissionError) as e:
            self._handle_disconnection(str(e), silent)
            return False
    
    def _handle_disconnection(self, reason, silent=False):
        """Handle Arduino disconnection internally"""
        if self.is_connected:
            if not silent:
                print(f"Arduino disconnected: {reason}")
            self.is_connected = False
            
            try:
                self.connection.close()
            except:
                pass  # Ignore errors while closing
                
            self.connection = None
            
            # Call user-provided callback if available
            if self.disconnect_callback:
                self.disconnect_callback(self.port)
    
    def send_command(self, command):
        """
        Send a command to the connected Arduino.
        
        Args:
            command (str): Command to send
            
        Returns:
            str or None: Response from Arduino or None if not connected/error
        """
        if not self.is_connected or not self.connection:
            # Don't print message if we're currently reconnecting
            if not self.reconnecting:
                print("Not connected to any Arduino board. Waiting for auto-reconnect...")
            return None
        
        try:
            self.connection.write(f"{command}\n".encode('utf-8'))
            time.sleep(0.1)  # Give Arduino time to process
            
            # Wait for response with timeout
            start_time = time.time()
            while time.time() - start_time < self.timeout:
                if self.connection.in_waiting > 0:
                    response = self.connection.read(self.connection.in_waiting).decode('utf-8').strip()
                    self.response_queue.append(response)  # Store response in queue
                    return response
                time.sleep(0.01)
            
            return None
        except (serial.SerialException, IOError, OSError, PermissionError) as e:
            self._handle_disconnection(str(e))
            return None
    
    def read_latest_responses(self, count=1):
        """
        Get the latest responses from the Arduino.
        
        Args:
            count (int): Number of latest responses to retrieve
            
        Returns:
            list: List of latest responses (newest first)
        """
        return list(self.response_queue)[-count:]
    
    def close(self):
        """Close the serial connection and stop background threads."""
        self.running = False  # Signal threads to stop
        
        # Wait for threads to complete
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1.0)
            
        if self.reconnect_thread and self.reconnect_thread.is_alive():
            self.reconnect_thread.join(timeout=1.0)
        
        # Close connection
        if self.connection:
            try:
                self.connection.close()
            except Exception as e:
                print(f"Error closing connection: {e}")
            finally:
                self.connection = None
                self.port = None
                self.is_connected = False
                print("Connection closed")