/*
 * Code for MAP hardware tests.
 * A program to test the Button Class Files
 * 
 * Written by: Lexie Scholtz
 * Created: 2022.10.02
 * Last Updated: 2023.04.03
*/

#include "Button.h"

Button red = Button();
Button green = Button(0x60);

void setup() {
  Serial.begin(9600);
  // TODO: add wait statement to allow Serial time to begin
  while (!Serial) { // wait for Serial port to open
    delay(10);
  }
  delay(500);

  Serial.println("Testing Button class");

  Wire.begin(); // MUST call this before using any i2c devices (including Button)

  if (green.init() == false) {
    Serial.println("Green button not connected! Reset when reconnected.");
    while(1);
  }

  if (red.init() == false) {
    Serial.println("Red button not connected! Reset when reconnected.");
    while(1);
  }

  Serial.println("Buttons connected successfully!");
}

void loop() {
  int red_status = red.update_status();
  int green_status = green.update_status();
  if (red_status > -1) { // button either clicked or pressed
    if (red_status > LONG_HOLD_THRESHOLD) {
      Serial.println("red long hold!");
    } else if (red_status > SHORT_HOLD_THRESHOLD) {
      Serial.println("red short hold");
    } else if (red_status > CLICK_THRESHOLD) {
      Serial.println("red click");
    }
  }
  if (green_status > -1) { // button either clicked or pressed
    if (green_status > LONG_HOLD_THRESHOLD) {
      Serial.println("green long hold!");
    } else if (green_status > SHORT_HOLD_THRESHOLD) {
      Serial.println("green short hold");
    } else if (green_status > CLICK_THRESHOLD) {
      Serial.println("green click");
    }
  }
}
