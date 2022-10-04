// test user interactions in the ENTER_TIME screen w/o display
// last update: 10.04.22 15:31

#include <Wire.h> 

#include "button.h"
#include "states.h"

Button red;
Button green;

States state;

const uint8_t TIME_LEN = 4;
uint8_t run_time[TIME_LEN] = {0, 0, 0, 0}; // nums in the run_time variable [mm/ss]
unsigned long run_time_ms = 0; // run time converted to ms

uint8_t current_char = 0;
unsigned long start_time = 0;
bool updated = false; // TESTING VARIABLE ONLY (to avoid continuously sending serial updates)

/* HELPER FXNS */
char increment_char(char c);
char decrement_char(char c);
bool check_file(String file_name);

void setup() {
  // set up serial communication
  Serial.begin(9600);
  Serial.println("Testing user interactions in ENTER_TIME w/o display");

  // set up I2C comms
  Wire.begin();

  // set up buttons - init fxns are needed
  red = Button();
  green = Button(0x60);

  if (green.init() == false) {
    Serial.println("Green button not connected! Reset when reconnected.");
    while(1);
  }

  if (red.init() == false) {
    Serial.println("Red button not connected! Reset when reconnected.");
    while(1);
  }

  Serial.println("Buttons connected successfully!");

  Serial.println("ready to go!");
  updated = true;
}

void loop() {
  int red_status = red.update_status();
  int green_status = green.update_status();

  // update "display" (serial for now)
  if (updated) { // only send updates if something has actually changed
    Serial.println("");
    Serial.print("min: ");
    Serial.print(run_time[0]);
    Serial.print(run_time[1]);
    Serial.print(" sec: ");
    Serial.print(run_time[2]);
    Serial.println(run_time[3]);
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

  // check both buttons
  // ignore long hold responses for now, since they would change state
  if (green_status > LONG_HOLD) {
    // convert run time to ms and save it
    unsigned long min = run_time[0] * 10 + run_time[1];
    unsigned long sec = run_time[2] * 10 + run_time[3];
    run_time_ms = min * 60000 + sec * 1000;
    
    Serial.print("Run time in ms: ");
    Serial.println(run_time_ms);

    Serial.println("moving to TEST_READY in full program...");

  } else if (green_status > SHORT_HOLD) {
    if (current_char < TIME_LEN - 1) {
      current_char++;
      Serial.print("going forward a char to ");
      Serial.println(current_char);
      updated = true;
    } else {
      // ignoring bc it's the last char
      // in the actual program, take out this else clause, just printing for troubleshooting
      Serial.println("NOT going forwards");
    }
    
  } else if (green_status > CLICK) {
    Serial.print("incrementing char ");
    Serial.println(current_char);
    if (current_char == 2) { // max sec = 60
      run_time[current_char] = (run_time[current_char] + 1) %  6;
    } else {
      run_time[current_char] = (run_time[current_char] + 1) % 10;
    }
    updated = true;
  } else if (red_status > LONG_HOLD) {
    Serial.println("moving to ENTER_NAME in full program...");
  } else if (red_status > SHORT_HOLD) {
    if (current_char > 0) {
      current_char--;      
      Serial.print("going back a char to ");
      Serial.println(current_char);
      updated = true;
    } else {
      // ignoring bc it's the first char
      // in the actual program, take out this else clause, just printing for troubleshooting
      Serial.println("NOT going backwards");
    }
  } else if (red_status > CLICK) {
    Serial.print("decrementing char ");
    Serial.println(current_char);
    if (current_char == 2) { // max sec = 60
      run_time[current_char] = (run_time[current_char] + 6 - 1) % 6;
    } else {
      run_time[current_char] = (run_time[current_char] + 10 -1) % 10;
    }
    updated = true;
  }
}

