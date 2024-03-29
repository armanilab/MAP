/*
 * Code for MAP hardware tests.
 * Header class for Button class
 * [a wrapper class for the SparkFun Qwiic button]
 * Written by: Lexie Scholtz
 *             Vic Nunez
 * Created: 2022.09.29
 * Last Updated: 2023.04.03
*/

#ifndef BUTTON_H
#define BUTTON_H

#include <SparkFun_Qwiic_Button.h>

const int CLICK_THRESHOLD = 20;
const int SHORT_HOLD_THRESHOLD = 1000;
const int LONG_HOLD_THRESHOLD = 3000;

class Button
{
private:
  QwiicButton qbutton;
  bool was_pressed; // indicates if the button was previously in pressed state
  unsigned long time_of_initial_press; // millis() time stamp of when press was initiated
  int i2c_address; // i2c address
  // TODO: some fxn to update LED brightness based on the length of press
  // (called by update_status). or maybe this should be public?
  uint8_t determine_brightness(unsigned long press_length);

public:
  Button();
  Button(int nondefault_i2c_address);

  void set_brightness(uint8_t brightness_level);
  bool init(); // initialize the Button. returns true if successful
  int update_status();
};

#endif
