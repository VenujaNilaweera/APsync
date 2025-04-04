#ifndef ARDUINO_CONNECTOR_H
#define ARDUINO_CONNECTOR_H

#include <Arduino.h>

class ArduinoConnector {
  private:
    String username;
    String incomingData;
    bool authenticated;
    
  public:
    /**
     * Constructor for ArduinoConnector.
     * @param validUsername The username to respond with when authentication is requested
     */
    ArduinoConnector(const String &validUsername);
    
    /**
     * Begin serial communication.
     * @param baudRate The baud rate for serial communication (default: 9600)
     */
    void begin(long baudRate = 9600);
    
    /**
     * Update method to process incoming serial data. Call this in loop().
     */
    void update();
    
    /**
     * Check if authentication is successful.
     * @return True if authenticated, false otherwise
     */
    bool isAuthenticated();
    
    /**
     * Send data to the Python host.
     * @param data The data to send
     */
    void sendData(const String &data);
    
    /**
     * Function pointer type for command callbacks.
     */
    typedef void (*CommandCallback)(String);
    
    /**
     * Set callback function for received commands.
     * @param callback The function to call when a command is received
     */
    void setCommandCallback(CommandCallback callback);
    
  private:
    CommandCallback userCallback;
    
    /**
     * Blink the default LED to signal successful connection or authentication.
     */
    void blinkLED();
};

#endif