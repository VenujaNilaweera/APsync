#include "ArduinoConnector.h"

ArduinoConnector::ArduinoConnector(const String &validUsername) {
    username = validUsername;
    authenticated = false;
    incomingData = "";
    userCallback = NULL;
}

void ArduinoConnector::blinkLED() {
  // Blink the LED three times
  for (int i = 0; i < 3; i++) {
    digitalWrite(LED_BUILTIN, HIGH);  // Turn the LED on
    delay(100);  // Wait for 100 milliseconds
    digitalWrite(LED_BUILTIN, LOW);   // Turn the LED off
    delay(100);  // Wait for 100 milliseconds
  }
}

void ArduinoConnector::begin(long baudRate) {
   Serial.begin(baudRate);
   pinMode(LED_BUILTIN, OUTPUT);  // Initialize the default LED pin (pin 13) as output
   delay(100);  // Give serial time to initialize
}

void ArduinoConnector::update() {
   // Process any incoming serial data
   if (Serial.available() > 0) {
     incomingData = Serial.readStringUntil('\n');
     incomingData.trim();  // Clean up the incoming data to remove extra spaces or newline characters
     
     // Check for the authentication request message
     if (incomingData == "Send your username:") {
       Serial.println(username);  // Respond ONLY with the username, nothing else
       // Do not send random numbers here - wait until authenticated
     }
     
     // Check for authentication success message
     else if (incomingData == "AUTH_SUCCESS") {
       authenticated = true;  // Mark as authenticated
       blinkLED();  // Blink the LED upon receiving successful authentication acknowledgment
       Serial.println("Authentication confirmed");  // Send confirmation back to Python
       
       // Now that we're authenticated, we can start sending random numbers or other data
       // in a separate function or in loop(), but not mixed with the username response
     }
     
     // If already authenticated and we have a callback, pass other commands to it
     else if (authenticated && userCallback != NULL) {
       userCallback(incomingData); // Handle commands from Python
     }
   }
}

bool ArduinoConnector::isAuthenticated() {
   return authenticated;
}

void ArduinoConnector::sendData(const String &data) {
   if (authenticated) {
     Serial.println(data);  // Send data to Python only if authenticated
   }
}

void ArduinoConnector::setCommandCallback(CommandCallback callback) {
   userCallback = callback;
}