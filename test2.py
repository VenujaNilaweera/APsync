import time
from arduino_connector import ArduinoConnector

def on_disconnect(port):
    """Callback when Arduino disconnection is detected"""
    print(f"🔌 Arduino disconnected from {port}! Waiting for it to be reconnected...")

def on_reconnect(port):
    """Callback when Arduino is successfully reconnected"""
    print(f"🔌 Arduino reconnected on {port}! Resuming normal operation.")

def main():
    # Create the connector
    connector = ArduinoConnector("Venus")
    
    # Set callbacks
    connector.set_disconnect_callback(on_disconnect)
    connector.set_reconnect_callback(on_reconnect)
    
    # Enable auto-reconnect (on by default)
    connector.enable_auto_reconnect(True)
    
    # Connect to Arduino
    port = connector.connect()
    
    if port:
        print(f"Successfully connected to Arduino on {port}")
        
        # Main program loop
        try:
            while True:
                # Try to send a command - will not show error messages if disconnected and reconnecting
                response = connector.send_command("PING")
                
                if response:
                    print(f"Response from Arduino: {response}")
                
                # If we're connected, we can do our normal work
                if connector.is_connected:
                    # Do something with the Arduino
                    pass
                else:
                    # We're disconnected but auto-reconnect is trying to handle it
                    # We can do something else while waiting
                    pass
                
                # Wait before next iteration
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\nProgram terminated by user.")
        finally:
            # Clean up
            connector.close()
    else:
        print("Failed to connect to Arduino. Make sure it's connected and has the correct sketch loaded.")

if __name__ == "__main__":
    main()