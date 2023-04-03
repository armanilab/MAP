/*
 * Code for MAP hardware tests.
 * A program to test the Adafruit TSL2591 Light-to-Digital Converter (Light Sensor)
 * 
 * Written by: Lexie Scholtz
 * Created: 2022.09.29
 * Last Updated: 2023.04.03
*/

#include <Wire.h> // needed for open log
#include <Adafruit_Sensor.h>
#include "Adafruit_TSL2591.h" // light sensor library

Adafruit_TSL2591 tsl = Adafruit_TSL2591(2591); // sensor object

const int RECONNECTION_DELAY = 1000;
const int MSG_TIME = 2000;

void setup() {
  /* HARDWARE SETUP */
  // set up serial communication
  Serial.begin(9600);
  while (!Serial) { // wait for Serial port to open
    delay(10);
  }
  delay(500);

  // set up i2C comms
  Wire.begin();

  // turn on screen
  // turn on backlite
  pinMode(TFT_BACKLITE, OUTPUT);
  digitalWrite(TFT_BACKLITE, HIGH);

  // turn on the TFT / I2C power supply
  pinMode(TFT_I2C_POWER, OUTPUT);
  digitalWrite(TFT_I2C_POWER, HIGH);
  delay(10);

    // set up sensor  - confirm connection
  if (!tsl.begin()) {
    Serial.println("no sensor");

    while(!check_sensor_connection()) {
      delay(RECONNECTION_DELAY);
    }

    Serial.println("sensor connection restablished");
    delay(MSG_TIME);
  }

  Serial.println("ready to test");

}

bool check_sensor_connection() {
  bool status = tsl.begin();
  Serial.println(status);
  if (status == 0) {
    return false;
  } else {
    return true;
  }
}

void loop() {
  uint32_t lum = tsl.getFullLuminosity();

  uint16_t ir = lum >> 16;
  uint16_t full = lum & 0xFFFF;
  float lux = tsl.calculateLux(full, ir);
  if (lux < 0.1) { // sensor is not connected
    Serial.println("caught sensor error");

    while(!check_sensor_connection()) {
      delay(RECONNECTION_DELAY);
    }

    Serial.println("sensor connection restablished");
    delay(MSG_TIME);
  }
  Serial.println(lux);

}
