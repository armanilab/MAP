/*
 * Code for the magnetometer.
 * Written by: Lexie Scholtz
 *             Vic Nunez
 * Created: 2022.09.29
 * Last Updated: 2022.10.04
*/

#include <Wire.h> // needed for open log
#include <Adafruit_Sensor.h>
#include "Adafruit_TSL2591.h" // light sensor library
#include "SparkFun_Qwiic_OpenLog_Arduino_Library.h" // open log library
// our libraries:
//#include "display.h" // our library to control the display @Vic however you want to set this up
#include "states.h"
#include "button.h" // use this as a wrapper for the sparkfun library; declare one button object for each red and green button

Adafruit_TSL2591 tsl = Adafruit_TSL2591(2591); // sensor object
OpenLog open_log; // datalogger object
Button red;
Button green;

States state;

/* IMPORTANT VARIABLES */
// name entry and file name
const uint8_t NAME_LEN = 6;
char file_entry[NAME_LEN + 1] = "******";
String file_name = "";
// run time
const uint8_t TIME_LEN = 4;
uint8_t run_time[TIME_LEN] = {0, 0, 0, 0}; // nums in the run_time variable [mm/ss]
unsigned long run_time_ms = 0; // run time converted to ms
// general use
uint8_t current_char = 0;
unsigned long start_time = 0;

bool updated = false; // DEBUG/TESTING VARIABLE ONLY

/* NEW FXNS */
char increment_char(char c);
char decrement_char(char c);
bool check_file(String file_name);

void setup() {
  /* HARDWARE SETUP */
  // set up openlog
  //Wire.begin();
  //open_log.begin();

  // set up serial communication
  Serial.begin(9600);
  while (!Serial) { // wait for Serial port to open
    delay(10);
  }
  delay(500);

  // set up i2C comms
  Wire.begin();

  // set up buttons
  red = Button();
  green = Button(0x60);

  // TODO: refactor these so if these get plugged in properly, then the program will continue
  // i.e. program should only stall if they're not connected, not totally stop
  if (green.init() == false) {
    Serial.println("Green button not connected! Reset when reconnected.");
    while(1);
  }

  if (red.init() == false) {
    Serial.println("Red button not connected! Reset when reconnected.");
    while(1);
  }

  Serial.println("Buttons connected successfully!");

  // set up open log - should this have a check to confirm it worked properly?
  open_log.begin();

  // confirm sensor is connected
  // TODO modify to use screen and not serial communications
  // maybe flash an LED if it's successful?
  /*
  if (tsl.begin()) {
    Serial.println("TSL2591 sensor connected successfully!");
  } else {
    Serial.println("No sensor found - connect and reset to continue.");
    while(1);
  } */

  // TODO; more setup lol

  // TODO: do we want to display some kind of welcome screen?

  Serial.println("Ready to go!");
  // initialize state to name entry
  state = ENTER_NAME;
  updated = true;
}

void loop() {
  // get updated button statuses
  int red_status = red.update_status();
  int green_status = green.update_status();

  /* NAME ENTRY */
  if (state == ENTER_NAME) {
    // TODO: display stuff
    // update display
    // 2nd argument = index of char to highlight (if out of range i.e. -1, highlight none)
    //display.show_file_name(new_file_name, current_char);

    // update "display" (serial for now) - remove when done troubleshooting
    if (updated) { // only send updates if something has actually changed
      Serial.println("");
      Serial.println(file_entry);
      for (int i = 0; i < current_char; i++) {
        Serial.print(" ");
      }
      Serial.println("^");
      Serial.println("");
      updated = false;
    }

    // green button input
    if (green_status > LONG_HOLD) {
      // post processing on entered name
      file_name = String(file_entry);
      file_name.replace("*", ""); // remove *'s from name
      file_name.concat(".txt"); // append .txt to make a text file
      Serial.print("processed file name: ");
      Serial.println(file_name);

      // check file name against existing files
      bool will_overwrite = check_file(file_name);
      if (will_overwrite) {
        // move to ENTER_NAME_OVERWRITE
        Serial.println("File found - change to OVERWRITE...");
      } else {
        // move to ENTER_TIME state
        Serial.println("change to ENTER_TIME...");
        state = ENTER_TIME;
      }
      updated = true;

    } else if (green_status > SHORT_HOLD) {
      // move forward one character
      if (current_char < NAME_LEN - 1) {
        current_char++;
        updated = true;
      }
    } else if (green_status > CLICK) {
      // increment current char
      file_entry[current_char] = increment_char(file_entry[current_char]);
      updated = true;
    } // otherwise, button was not pressed, do nothing

    // react to red button
    if (red_status > SHORT_HOLD) {
      // go back one character
      if (current_char > 0) {
        current_char--;
        updated = true;
      }
    } else if (red_status > CLICK) {
      // decrement current character
      file_entry[current_char] = decrement_char(file_entry[current_char]);
      updated = true;
    }

  /* TIME ENTRY */
  } else if (state == ENTER_TIME) {
    // remove this loop when done troubleshooting
    if (updated) { // only send updates if something has actually changed
      Serial.println("");
      Serial.print("min: ");
      Serial.print(run_time[0]);
      Serial.print(run_time[1]);
      Serial.print(" sec: ");
      Serial.print(run_time[2]);
      Serial.println(run_time[3]);
      // use a cursor to indicate current char
      if (current_char == 0) {
        Serial.println("     ^");
      } else if (current_char == 1) {
        Serial.println("      ^");
      } else if (current_char == 2) {
        Serial.println("             ^");
      } else if (current_char == 3) {
        Serial.println("              ^");
      }
      Serial.println("");
      updated = false;
    }

    if (green_status > LONG_HOLD) {
      // convert run time to ms and save it
      unsigned long min = run_time[0] * 10 + run_time[1];
      unsigned long sec = run_time[2] * 10 + run_time[3];
      run_time_ms = min * 60000 + sec * 1000;

      Serial.print("Run time in ms: ");
      Serial.println(run_time_ms);

      Serial.println("moving to TEST_READY...");

    } else if (green_status > SHORT_HOLD) {
      if (current_char < TIME_LEN - 1) {
        current_char++;
        updated = true;
      }
    } else if (green_status > CLICK) {
      if (current_char == 2) { // max sec = 60
        run_time[current_char] = (run_time[current_char] + 1) %  6;
      } else {
        run_time[current_char] = (run_time[current_char] + 1) % 10;
      }
      updated = true;
    }

    if (red_status > LONG_HOLD) {
      // user long held red button to go back to name entry
      Serial.println("moving to ENTER_NAME...");
      state = ENTER_NAME;

    } else if (red_status > SHORT_HOLD) {
      // user short held red button to go back 1 character
      if (current_char > 0) { // decrement the character index
        current_char--;
        updated = true;
      }
    } else if (red_status > CLICK) {
      if (current_char == 2) { // max sec = 60
        run_time[current_char] = (run_time[current_char] + 6 - 1) % 6;
      } else {
        run_time[current_char] = (run_time[current_char] + 10 -1) % 10;
      }
      updated = true;
    }
  } else if (state == TEST_READY) {
    if (green_status > LONG_HOLD) {
      // if confirmed ready, prep & move on to actual test

      // if file_name already exists in the directory, remove it
      open_log.removeFile(file_name);
      // create a new file file_name.txt
      open_log.append(file_name);
      // write header lines to the file
      open_log.print("# ");
      open_log.println(file_name);
      open_log.print("# Run time: ");
      open_log.print(run_time[0]);
      open_log.print(run_time[1]);
      open_log.print(" min, ");
      open_log.print(run_time[2]);
      open_log.print(run_time[3]);
      open_log.println(" sec");
      open_log.print("###");

      // flush file - flush() command
      open_log.syncFile();
      // record start time
      start_time = millis();

      // move to test in progress state to start test
      state = TEST_IN_PROGRESS;
    }
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

char increment_char(char c) {
  if (c == '*') {
    return 'a';
  } else if (c >= 'a' && c < 'z') {
    return ++c;
  } else if (c == 'z') {
    return '0';
  } else if (c >= '0' && c < '9') {
    return ++c;
  } else if (c == '9') {
    return '_';
  } else { // c == '_'
    return '*'; // asterisks will be ignored in file name
  }
}

char decrement_char(char c) {
  if (c == '*') {
    return '_';
  } else if (c == '_') {
    return '9';
  } else if (c > '0' && c <= '9') {
    return --c;
  } else if (c == '0') {
    return 'z';
  } else if (c > 'a' && c <= 'z') {
    return --c;
  } else { // c == 'a'
    return '*';
  }
}

bool check_file(String file_name) {
  open_log.searchDirectory("*.*");
  String next_file = open_log.getNextDirectoryItem();
  while (next_file != "") {
    if (next_file == file_name) {
      Serial.print(file_name);
      Serial.println(" found!");
      return true;
    }
    next_file = open_log.getNextDirectoryItem();
  }
  return false;
}
