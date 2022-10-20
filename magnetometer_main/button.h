// header class for Button class
// [a wrapper class for the SparkFun Qwiic button]

#ifndef BUTTON_H
#define BUTTON_H

#include <SparkFun_Qwiic_Button.h>

// constants
const int CLICK = 20;
const int SHORT_HOLD = 1000;
const int LONG_HOLD = 2000;

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
  void set_brightness(uint8_t brightness_level);

public:
  // constructors
  Button();
  Button(int nondefault_i2c_address);

  // functions
  bool init(); // initialize the Button. returns true if successful
  bool check_connection();
  int update_status();
};

#endif
