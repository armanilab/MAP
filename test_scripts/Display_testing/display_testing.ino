#include <Wire.h> // needed for open log
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

  screen.begin();
  delay(500);

  screen.show_test_ready("display", [9, 9, 9, 9]);
}



void loop()
{
}
