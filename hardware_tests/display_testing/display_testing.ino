/*
 * A program to test the Adafruit ESP32-S2 TFT Feather display
 * with functions written for the MAP.

 * Written by: Vic Nunez
               Lexie Scholtz
 * Created: 2022.09.29
 * Last Updated: 2023.03.31
*/

#include "display_test.h"

Display screen = Display();

void setup() {
  /* HARDWARE SETUP */
  // set up serial communication
  Serial.begin(9600);
  while (!Serial) { // wait for Serial port to open
    delay(10);
  }
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
}

void loop()
{
}
