/*
 * Code for MAP hardware tests.
 * TFT Screen Display Test
 * A program to test the Adafruit ESP32-S2 TFT Feather display
 * with functions written for the MAP.
 * 
 * Written by: Lexie Scholtz
 *             Vic Nunez
 * Created: 2022.09.29
 * Last Updated: 2023.04.03
*/

#include "Arduino.h"
#include <Adafruit_GFX.h>    // Core graphics library
#include <Adafruit_ST7789.h> // Hardware-specific library for ST7789
#include "display_test.h"

Display screen = Display();

void setup() {
  /* HARDWARE SETUP */
  // set up serial communication
  Serial.begin(9600);
  // while (!Serial) { // wait for Serial port to open
  //   delay(10);
  // }
  delay(500);

  // turn on screen
  // turn on backlite
  pinMode(TFT_BACKLITE, OUTPUT);
  digitalWrite(TFT_BACKLITE, HIGH);

  // turn on the TFT / I2C power supply
  pinMode(TFT_I2C_POWER, OUTPUT);
  digitalWrite(TFT_I2C_POWER, HIGH);
  delay(10);

  screen.begin();
  delay(500);

  // write a test to the TFT
  // screen should display the following 3 lines:
  //      display.txt
  //         99:99
  // Hold GREEN to start
  int test_time[4] = {9, 9, 9, 9};
  screen.show_test_ready("display", test_time);

  // Serial.println("We made it to here.");
  // screen.show_error_logger();
}

void loop()
{
}
