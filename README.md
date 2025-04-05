# 🔌 Arduino-Python Auto-Connector with Auto Reconnection

A robust, modular system that allows a Python script to communicate with an Arduino over Serial with:

- ✅ **Username-based authentication**
- 🔁 **Automatic reconnection**
- 🧠 **Command-response support**
- 🎲 **Random number broadcasting**
- 🧱 **Modular C++ and Python class design**

---

## ✨ Features

- ✅ **Username-Based Authentication**  
  Authenticate Arduino clients before communication begins.

- 🔁 **Automatic Reconnection**  
  Lost connection? No problem — auto-reconnect resumes communication seamlessly.

- 🧠 **Command-Response Support**  
  Python can issue commands like `SEND_RANDOM`, and Arduino responds dynamically.

- 🎲 **Random Number Broadcasting**  
  Arduino sends random values every 5 seconds after authentication.

- 🧱 **Clean Modular Design**  
  Encapsulated C++ class for Arduino and Python-side connector module.

---

## 📁 Project Structure

Arduino-Python-Connector/ ├── Arduino/ │ ├── ArduinoConnector.h # Arduino class header │ ├── ArduinoConnector.cpp # Arduino class logic │ └── test_arduino.ino # Arduino sketch using the connector ├── Python/ │ ├── arduino_connector.py # Python connector module │ └── test_python.py # Test script for serial interaction └── README.md # You’re reading it!

arduino
Copy
Edit

---

## 🛠️ Arduino Setup

### `test_arduino.ino`

```cpp
#include "ArduinoConnector.h"

ArduinoConnector connector("Venus");  // Set the username for authentication

void handleCommand(String command) {
  if (command == "SEND_RANDOM") {
    int randomValue = random(1, 100);
    connector.sendData("Random: " + String(randomValue));
  }
}

void setup() {
  randomSeed(analogRead(0));
  connector.begin(9600);
  connector.setCommandCallback(handleCommand);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  connector.update();
  if (connector.isAuthenticated()) {
    static unsigned long lastSendTime = 0;
    if (millis() - lastSendTime > 5000) {
      int randomNum = random(1, 100);
      connector.sendData(String(randomNum));
      lastSendTime = millis();
    }
  }
}
🐍 Python Setup
test_python.py
python
Copy
Edit
import time
from arduino_connector import ArduinoConnector

def on_disconnect(port):
    print(f"❌ Arduino disconnected from {port}! Reconnecting...")

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
                    print(f"📨 Response from Arduino: {response}")
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Program terminated by user.")
        finally:
            connector.close()
    else:
        print("⚠️ Failed to connect to Arduino. Make sure it’s plugged in and running the sketch.")

if __name__ == "__main__":
    main()
🚀 How to Run
1. Upload the Arduino Sketch
Open test_arduino.ino in the Arduino IDE.

Connect your board and upload the sketch.

2. Install Python Dependencies
bash
Copy
Edit
pip install pyserial
3. Run the Python Script
Make sure the Arduino IDE's Serial Monitor is closed, then run:

bash
Copy
Edit
python test_python.py
🧰 Troubleshooting
PermissionError:
Ensure the Arduino Serial Monitor is closed and no other app is using the port.

No response from COM port:
Check that the correct COM port is used and the Arduino sketch is running properly.

🤝 Contributing
Feel free to fork this repo, open issues, or submit pull requests to improve functionality!

📄 License
This project is licensed under the MIT License. See the LICENSE file for details.

yaml
Copy
Edit

---

Let me know if you'd like:

- A badge section (e.g. for license, Python version, etc.)
- GIF or image demo support
- Optional `requirements.txt` generator
- Auto port detection description for non-Windows systems

Happy committing! 💻🛠️
