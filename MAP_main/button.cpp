/* class definition: Button */
#include "Button.h"

// TODO: comment file

Button::Button()
{
  // TODO: add try-catch statement
  qbutton = QwiicButton(); // is this how i do it? i think so?
  was_pressed = false;
  time_of_initial_press = 0;
  i2c_address = 0x6F;
}

Button::Button(int nondefault_i2c_address)
{
  qbutton = QwiicButton();
  was_pressed = false;
  time_of_initial_press = 0;
  i2c_address = nondefault_i2c_address;
}

bool Button::init() {
  return qbutton.begin(i2c_address);
}

bool Button::check_connection() {
  return qbutton.isConnected();
}

int Button::update_status()
{
  if (!qbutton.isConnected()) {
    return -1;
  }
  if (qbutton.isPressed()) {
    if (!was_pressed) {
      was_pressed = true;
      time_of_initial_press = millis();
    }
    unsigned long press_length = millis() - time_of_initial_press;
    set_brightness(determine_brightness(press_length));
  } else { // button not pressed
    if (was_pressed) {
      unsigned long press_length = millis() - time_of_initial_press;
      was_pressed = false;
      return press_length;
    }
    qbutton.LEDoff();
  }
  return 0; // if button was either not clicked or clicked and not released
}

uint8_t Button::determine_brightness(unsigned long press_length) {
  uint8_t brightness = 0;
  if (press_length > LONG_HOLD) {
    brightness = 250;
  } else if (press_length > SHORT_HOLD) {
    brightness = 100;
  } else if (press_length > CLICK) {
    brightness = 10;
  }
  return brightness;
}

void Button::set_brightness(uint8_t brightness_level) {
  qbutton.LEDon(brightness_level);
}

void Button::blink_LED() {
  qbutton.LEDconfig(255, 1000, 1000);
}
