// test user interactions in the ENTER_NAME screen w/o display
// last update: 10.04.22 14:17

#include <Wire.h> 
#include "SparkFun_Qwiic_OpenLog_Arduino_Library.h"

#include "button.h"
#include "states.h"

Button red;
Button green;
OpenLog open_log;

States state;

const uint8_t NAME_LEN = 6;
char file_entry[NAME_LEN] = "******";
char new_file_entry[NAME_LEN] = "******";
String file_name = "";
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
  Serial.println("Testing user interactions in ENTER_NAME w/o display");

  // set up I2C comms
  Wire.begin();

  // set up openlog
  open_log.begin();

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
    Serial.println(new_file_entry);
    Serial.print("current_char: ");
    Serial.println(new_file_entry[current_char]);
    Serial.println("");
    updated = false;
  }

  // check both buttons
  // ignore long hold responses for now, since they would change state
  if (green_status > LONG_HOLD) {
    // check file name
    // remove *'s from name:
    //String file_ent = file_entry;
    file_name = String(file_entry);
    file_name.replace("*", "");
    file_name.concat(".txt");
    Serial.print("processed file name: ");
    Serial.println(file_name);
    
    bool will_overwrite = check_file(file_name);
    if (will_overwrite) {
      Serial.println("File found - change to OVERWRITE in full program...");
    } else {
      Serial.println("change to ENTER_TIME in full program...");
    }    
    updated = true;

  } else if (green_status > SHORT_HOLD) {
    if (current_char < NAME_LEN - 1) {
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
    new_file_entry[current_char] = increment_char(new_file_entry[current_char]);
    updated = true;
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
    new_file_entry[current_char] = decrement_char(new_file_entry[current_char]);
    updated = true;
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
