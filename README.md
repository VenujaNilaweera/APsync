🔌 Arduino-Python AutoConnect
Seamless Serial Communication Between Arduino and Python
A robust, auto-reconnecting connector with username-based authentication, command handling, and real-time data exchange.

🚀 Overview
This project enables smooth and secure communication between an Arduino and a Python script over serial. With built-in auto-reconnect, command parsing, and random data exchange, it's perfect for interactive sensor systems, serial-based control, or teaching embedded communication principles.

✨ Features
✅ Username-Based Authentication
Authenticate Arduino clients before communication begins.

🔁 Automatic Reconnection
Lost connection? No problem — auto-reconnect resumes communication seamlessly.

🧠 Command-Response Support
Python can issue commands like SEND_RANDOM, and Arduino responds dynamically.

🎲 Random Number Broadcasting
Arduino sends random values every 5 seconds after authentication.

🛠️ Clean Modular Design
Encapsulated C++ class for Arduino and Python-side connector module.

📁 Project Structure
bash
Copy
Edit
Arduino-Python-Connector/
├── Arduino/
│   ├── ArduinoConnector.h         # Arduino class header
│   ├── ArduinoConnector.cpp       # Arduino class logic
│   └── test_arduino.ino           # Arduino sketch using the connector
├── Python/
│   ├── arduino_connector.py       # Python connector module
│   └── test_python.py             # Test script for serial interaction
└── README.md                      # You’re reading it!
🔧 Arduino Setup
test_arduino.ino

---

## 🔧 Arduino Setup

### 📝 `test_arduino.ino`

```cpp
#include "ArduinoConnector.h"

ArduinoConnector connector("Venus");  // Username-based authentication

void handleCommand(String command) {
  if (command == "SEND_RANDOM") {
    int randomValue = random(1, 100);
    connector.sendData("Random: " + String(randomValue));
  }
}

void setup() {
  randomSeed(analogRead(0));           // Initialize random seed
  connector.begin(9600);               // Start serial comm
  connector.setCommandCallback(handleCommand);
  pinMode(LED_BUILTIN, OUTPUT);        // Optional LED indicator
}

void loop() {
  connector.update();                  // Handle communication
  if (connector.isAuthenticated()) {
    static unsigned long lastSendTime = 0;
    if (millis() - lastSendTime > 5000) {
      connector.sendData(String(random(1, 100)));  // Periodic random number
      lastSendTime = millis();
    }
  }
}


🐍 Python Script
test_python.py
python
Copy
Edit
import time
from arduino_connector import ArduinoConnector

def on_disconnect(port):
    print(f"🔌 Arduino disconnected from {port}. Reconnecting...")

def on_reconnect(port):
    print(f"✅ Reconnected to Arduino on {port}!")

def main():
    connector = ArduinoConnector("Venus")
    connector.set_disconnect_callback(on_disconnect)
    connector.set_reconnect_callback(on_reconnect)
    connector.enable_auto_reconnect(True)

    port = connector.connect()

    if port:
        print(f"✅ Connected to Arduino on {port}")
        try:
            while True:
                response = connector.send_command("PING")
                if response:
                    print(f"📨 Response: {response}")
                time.sleep(1)
        except KeyboardInterrupt:
            print("🛑 Program stopped by user.")
        finally:
            connector.close()
    else:
        print("❌ Connection failed. Check the Arduino and try again.")

if __name__ == "__main__":
    main()
▶️ How to Run
1. Upload Arduino Code
Open test_arduino.ino in the Arduino IDE.

Upload to your board.

2. Install Python Requirements
bash
Copy
Edit
pip install pyserial
3. Run Python Script
Make sure no other application (like the Arduino Serial Monitor) is using the COM port:

bash
Copy
Edit
python test_python.py
🧪 Behavior Summary
Authenticates using the username Venus.

Sends a random number every 5 seconds post-authentication.

Responds to Python-issued commands like SEND_RANDOM.

Automatically reconnects if the Arduino resets or disconnects.

🛠 Troubleshooting
PermissionError: Close Arduino Serial Monitor before running Python script.

No COM Response: Ensure correct port and sketch are loaded.

Slow Detection: Give the script a few seconds to auto-detect the Arduino on reconnect.

🤝 Contributing
Have ideas to improve this project?
Feel free to fork, open an issue, or submit a pull request!

📄 License
Licensed under the MIT License.
See the LICENSE file for more details.
