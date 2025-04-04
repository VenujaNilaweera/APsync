#include "ArduinoConnector.h"

ArduinoConnector connector("Venus");  // Create connector with username "Venus"

// Callback function for handling commands
void handleCommand(String command) {
  // Process commands from Python here
  if (command == "SEND_RANDOM") {
    int randomValue = random(1, 100);  // Generate a random number between 1 and 100
    connector.sendData("Random: " + String(randomValue));  // Send the random value to Python
  }
}

void setup() {
  randomSeed(analogRead(0));  // Initialize random number generator from an unconnected pin
  connector.begin(9600);      // Start serial communication at 9600 baud
  connector.setCommandCallback(handleCommand);  // Set the callback function to handle commands from Python
  
  pinMode(LED_BUILTIN, OUTPUT);  // Initialize the LED pin as output
}

void loop() {
  connector.update();  // Process serial communications (authentication & commands)
  
  // Only send random numbers periodically when authenticated
  if (connector.isAuthenticated()) {
    // Send a random number every 5 seconds
    static unsigned long lastSendTime = 0;
    if (millis() - lastSendTime > 5000) {  // 5 seconds interval
      int randomNum = random(1, 100);  // Generate a random number between 1 and 100
      connector.sendData(String(randomNum));  // Send the random number to Python
      lastSendTime = millis();  // Reset the timer
    }
  }
}
