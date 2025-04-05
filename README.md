# 🔌 Arduino-Python Auto-Connector

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A robust, modular system for establishing and maintaining serial communication between a Python script and an Arduino microcontroller. This project features username-based authentication, automatic reconnection capabilities, command-response handling, and periodic data broadcasting.

## ✨ Features

* ✅ **Username-Based Authentication**: Securely authenticate the Arduino client before enabling full communication.
* 🔁 **Automatic Reconnection**: If the serial connection is lost, the Python script automatically attempts to reconnect, resuming communication seamlessly upon success.
* 🧠 **Command-Response Support**: Python can issue commands (e.g., `PING`, `SEND_RANDOM`), and the Arduino can process them and send back dynamic responses.
* 🎲 **Random Number Broadcasting**: After successful authentication, the Arduino periodically broadcasts random integer values to the connected Python script.
* 🧱 **Clean Modular Design**: Encapsulated C++ class (`ArduinoConnector`) for the Arduino side and a corresponding Python module (`arduino_connector.py`) for easy integration and maintenance.

## 📁 Project Structure

Arduino-Python-Connector/
├── Arduino/
│   ├── ArduinoConnector.h   # Arduino C++ class header file
│   ├── ArduinoConnector.cpp # Arduino C++ class implementation
│   └── test_arduino.ino     # Example Arduino sketch demonstrating usage
├── Python/
│   ├── arduino_connector.py # Python module for serial connection management
│   └── test_python.py       # Example Python script demonstrating usage
└── README.md                # This file


*(Note: The actual `ArduinoConnector.h`, `ArduinoConnector.cpp`, and `arduino_connector.py` files containing the class logic are assumed based on the structure but were not provided in the original prompt. The example code uses them.)*

## 🛠️ Prerequisites

* Arduino IDE installed.
* Python 3.x installed.
* An Arduino board (e.g., Uno, Nano, ESP32) compatible with the Arduino IDE.
* A USB cable to connect the Arduino to your computer.

## ⚙️ Setup & Configuration

1.  **Clone the Repository (if applicable):**
    ```bash
    git clone <your-repository-url>
    cd Arduino-Python-Connector
    ```

2.  **Configure Arduino Sketch:**
    * Open `Arduino/test_arduino.ino` in the Arduino IDE.
    * **Set the Username:** Modify the line `ArduinoConnector connector("Venus");` to use your desired username. This *must* match the username used in the Python script.
        ```cpp
        // Inside test_arduino.ino
        ArduinoConnector connector("YOUR_CHOSEN_USERNAME"); // <-- CHANGE THIS
        ```
    * Select your board and port in the Arduino IDE.
    * Upload the sketch to your Arduino board.

3.  **Configure Python Script:**
    * Open `Python/test_python.py`.
    * **Set the Username:** Ensure the username in the `ArduinoConnector` initialization matches the one set in the Arduino sketch.
        ```python
        # Inside test_python.py
        connector = ArduinoConnector("YOUR_CHOSEN_USERNAME") # <-- CHANGE THIS to match Arduino
        ```

4.  **Install Python Dependencies:**
    * It's recommended to use a virtual environment.
    * Install the required `pyserial` library:
        ```bash
        pip install pyserial
        # Or, if you create a requirements.txt:
        # pip install -r requirements.txt
        ```

## 🚀 How to Run

1.  **Ensure the Arduino is connected** to your computer via USB and running the uploaded `test_arduino.ino` sketch.
2.  **Close the Arduino IDE's Serial Monitor** or any other application that might be using the Arduino's serial port.
3.  **Run the Python script** from your terminal:
    ```bash
    python Python/test_python.py
    ```

You should see output indicating connection attempts, authentication status, received random numbers from the Arduino, and responses to commands sent from Python. The script will automatically try to reconnect if the connection is interrupted.

##  örnek Code Snippets

### Arduino (`Arduino/test_arduino.ino`)

```cpp
#include "ArduinoConnector.h"

// IMPORTANT: Set the username for authentication (must match Python script)
ArduinoConnector connector("Venus");

// Callback function to handle commands received from Python
void handleCommand(String command) {
  if (command == "SEND_RANDOM") {
    int randomValue = random(1, 100);
    connector.sendData("Random: " + String(randomValue)); // Send response back
  }
  // Add more command handling logic here
}

void setup() {
  randomSeed(analogRead(0)); // Seed random number generator
  connector.begin(9600); // Initialize Serial communication at 9600 baud
  connector.setCommandCallback(handleCommand); // Register the command handler
  pinMode(LED_BUILTIN, OUTPUT); // Optional: Use built-in LED for status
}

void loop() {
  connector.update(); // Handles receiving data, authentication, and commands

  // Only broadcast random numbers if authenticated
  if (connector.isAuthenticated()) {
    static unsigned long lastSendTime = 0;
    unsigned long currentTime = millis();

    // Send a random number every 5 seconds
    if (currentTime - lastSendTime > 5000) {
      int randomNum = random(1, 100);
      connector.sendData(String(randomNum)); // Send data (non-command)
      lastSendTime = currentTime;
      digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN)); // Toggle LED
    }
  } else {
    digitalWrite(LED_BUILTIN, LOW); // Turn LED off if not authenticated
  }
}
Python (Python/test_python.py)
Python

import time
from arduino_connector import ArduinoConnector # Assumes this module exists

# Callback for when the Arduino disconnects
def on_disconnect(port):
    print(f"❌ Arduino disconnected from {port}! Reconnecting...")

# Callback for when the Arduino successfully reconnects
def on_reconnect(port):
    print(f"✅ Reconnected to Arduino on {port}!")

def main():
    # IMPORTANT: Initialize with the same username as in the Arduino sketch
    connector = ArduinoConnector("Venus")

    # Register callbacks for connection events
    connector.set_disconnect_callback(on_disconnect)
    connector.set_reconnect_callback(on_reconnect)

    # Enable the auto-reconnect feature
    connector.enable_auto_reconnect(True)

    # Attempt to connect (will automatically find the port if implemented)
    port = connector.connect()

    if port:
        print(f"✅ Connected to Arduino on {port}")
        try:
            # Example loop: Send PING command periodically
            while True:
                if connector.is_connected(): # Check if still connected
                    # Example: Send a command and wait for a response
                    response = connector.send_command("PING", timeout=2) # Send PING, wait 2s
                    if response:
                        print(f"📨 Response from Arduino: {response}")
                    else:
                        print("⏳ No response received for PING (or command not implemented on Arduino).")

                    # Read any broadcasted data (like the random numbers)
                    data = connector.read_data()
                    if data:
                        print(f"📡 Data from Arduino: {data}")

                time.sleep(1) # Wait before next interaction

        except KeyboardInterrupt:
            print("\n🛑 Program terminated by user.")
        finally:
            print("🔌 Closing connection...")
            connector.close()
    else:
        print("⚠️ Failed to connect to Arduino. Make sure it’s plugged in, running the sketch, and the correct username is set.")
        print("   Ensure no other application (like Arduino Serial Monitor) is using the port.")

if __name__ == "__main__":
    main()
🧰 Troubleshooting
PermissionError: [Errno 13] Permission denied: '/dev/tty...' (Linux/Mac) or Access is denied. (Windows):
Ensure the Arduino IDE's Serial Monitor is closed.
Check that no other application is using the serial port.
On Linux, you might need to add your user to the dialout group: sudo usermod -a -G dialout $USER (log out and back in afterward).
SerialException: Could not configure port or No response from COM port:
Verify the Arduino board is plugged in correctly.
Confirm the test_arduino.ino sketch (with the correct username) is successfully uploaded and running.
If the script doesn't auto-detect the port, you may need to specify it manually in the ArduinoConnector initialization (if the class supports it). Check the arduino_connector.py implementation.
Authentication Fails:
Double-check that the username string in test_arduino.ino EXACTLY matches the username string in test_python.py. They are case-sensitive.
Connection Drops Frequently:
Check the USB cable and connections.
Ensure the Arduino has sufficient power.
Look for potential blocking code or long delays in the Arduino loop().
🤝 Contributing
Contributions are welcome! Feel free to fork this repository, open issues for bugs or feature requests, or submit pull requests to improve the functionality.

Some ideas for improvement:

Implement automatic port detection for different operating systems.
Add more robust error handling and logging.
Include a requirements.txt file.
Add more examples or advanced use cases.
Create unit tests.
