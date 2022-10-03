/*
 * Code for the magnetometer.
 * Written by: Lexie Scholtz
 *             Vic Nunez
 * Created: 2022.09.29
 * Last Updated: 2022.09.29
*/

#include <Wire.h> // needed for open log
#include <Adafruit_Sensor.h>
#include "Adafruit_TSL2591.h" // light sensor library
#include "SparkFun_Qwiic_OpenLog_Arduino_Library.h" // open log library
// our libraries:
#include "tft_display.h" // our library to control the display @Vic however you want to set this up
#include "states.h"
#include "button.h" // use this as a wrapper for the sparkfun library; declare one button object for each red and green button

Adafruit_TSL2591 tsl = Adafruit_TSL2591(2591); // sensor object
OpenLog open_log; // datalogger object

States state;

/* IMPORTANT VARIABLES */
String file_name = "";
String new_file_name = "";
int current_char = 0;

/* NEW FXNS */
void change_state(State new_state);

void setup() {
  /* HARDWARE SETUP */
  // set up openlog
  Wire.begin();
  open_log.begin();

  // set up serial communication
  Serial.begin(9600);
  while (!Serial) { // wait for Serial port to open
    delay(10);
  }
  delay(500);

  // confirm sensor is connected
  // TODO modify to use screen and not serial communications
  // maybe flash an LED if it's successful?
  if (tsl.begin()) {
    Serial.println("TSL2591 sensor connected successfully!");
  } else {
    Serial.println("No sensor found - connect and reset to continue.");
  }

  // TODO; more setup lol

  // TODO: do we want to display some kind of welcome screen?

  // initialize state to name entry
  state = ENTER_NAME;
}

void loop() {
  // TODO: update buttons
  //red_status = red_button.update_status();
  //green_status = green_button.update_status();

  if (state == ENTER_NAME) {
    display.show_file_name(new_file_name);
    // TODO: blink current char
    display.highlight_char(current_char);

    // react based on buttons
    // TODO: check syntax
    if (green_status > Button.LONG_HOLD) {
      // long hold stuff
    } else if (green_status > Button.SHORT_HOLD) {
      // short hold stuff
    } else if (green_status > Button.CLICKED) {
      // click
    } // otherwise, button was not pressed, do nothing
    // do stuff
  } else if (state == ENTER_TIME) {
    // do more stuff
  } else if (state == TEST_READY) {
    // even more stuff!
  } else if (state == TEST_IN_PROGRESS) {
    // stuff to run a test
  } else if (state == TEST_ENDED) {
    // recap stuff
  } else if (state == ERROR_LOGGER) {
    // not good stuff
  } else if (state == ERROR_SENSOR) {
    // arguably worse stuff?
  } else if (state == ENTER_NAME_OVERWRITE) {
    // warning of bad stuff
  }

}

void change_state(State new_state) {
  if (new_state == ENTER_NAME) {
    new_file_name = file_name;
    current_char = 0;
    display.highlight_char(current_char);
  }
}
