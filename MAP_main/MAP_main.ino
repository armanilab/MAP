/*
 * Code for the magnetometer.
 * Written by: Lexie Scholtz
 *             Vic Nunez
 * Created: 2022.09.29
 * Last Updated: 2023.02.07
*/

#include "Arduino.h"
#include <Wire.h> // needed for open log
#include <Adafruit_Sensor.h>
#include "Adafruit_TSL2591.h" // light sensor library
#include "SparkFun_Qwiic_OpenLog_Arduino_Library.h" // open log library
#include <Adafruit_GFX.h>    // Core graphics library
#include <Adafruit_ST7789.h> // Hardware-specific library for ST7789
#include <SPI.h>
// our libraries:
// #include "display.h" // our library to control the display @Vic however you want to set this up
#include "Display.h"
#include "states.h"
#include "button.h" // use this as a wrapper for the sparkfun library; declare one button object for each red and green button

// Adafruit_ST7789 tft = Adafruit_ST7789(TFT_CS, TFT_DC, TFT_RST);
Adafruit_TSL2591 tsl = Adafruit_TSL2591(2591); // sensor object
OpenLog open_log; // datalogger object
Button red = Button();
Button green = Button(0x60);
Display tft = Display();

States state;

/* IMPORTANT VARIABLES */
// name entry and file name
const uint8_t NAME_LEN = 6;
char file_entry[NAME_LEN + 1] = "******";
String file_name = "";
uint8_t current_name_char = 0;
// run time
const uint8_t TIME_LEN = 4;
int run_time[TIME_LEN] = {0, 0, 0, 0}; // nums in the run_time variable [mm/ss]
unsigned long run_time_ms = 0; // run time converted to ms
uint8_t current_time_char = 0;
// test use
unsigned long start_time = 0;
unsigned long time_elapsed = 0;
const unsigned long UPDATE_INT = 1000; // [ms] refresh rate of display during test
unsigned long last_update = -UPDATE_INT;
bool ended_early = false;
// avg_slope 
int data_points = 40;
int slope_index = 0;
float prev_lux = 1;
bool array_full = false;
int slopes[39];                        // *IMPORTANT* If we change # of data points, we must change this number inside of brackets
float time_interval;    // *IMPORTANT* need to find the value this needs to be at
unsigned long prev_time_elapsed = 0;
float cur_slope;

bool updated = false; // indicates if data for display/serial has been updated

const int RECONNECTION_DELAY = 1000;
const int MSG_TIME = 2000;
const float LIGHT_THRESHOLD = 0.1;

/* NEW FXNS */
char increment_char(char c);
char decrement_char(char c);
bool check_file(String file_name);
bool check_open_log_connection();

void setup() {
  /* HARDWARE SETUP */
  // set up serial communication
  Serial.begin(9600);
  // while (!Serial) { // wait for Serial port to open
  //   delay(10);
  // }
  delay(500);

  // set up i2C comms
  Wire.begin();

  // Serial.println("Is Serial Working at all?");
  // turn on screen
  // turn on backlite
  pinMode(TFT_BACKLITE, OUTPUT);
  digitalWrite(TFT_BACKLITE, HIGH);

  // turn on the TFT / I2C power supply
  pinMode(TFT_I2C_POWER, OUTPUT);
  digitalWrite(TFT_I2C_POWER, HIGH);
  delay(10);

  // initialize tft
  // Serial.println("Before Tft start");
  tft.begin();
  // Serial.println("AFTER TFT start");

  // set up buttons
  // TODO: refactor these so if these get plugged in properly, then the program will continue
  // i.e. program should only stall if they're not connected, not totally stop
  if (green.init() == false) {
    button_error();
  }

  if (red.init() == false) {
    button_error();
  }

  // set up open log - should this have a check to confirm it worked properly?
  updated = true;
  open_log.begin();
  if (!check_open_log_connection()) {
    logger_error();
  }

  // set up sensor  - confirm connection
  if (!tsl.begin()) {
    sensor_error();
  }

  // configure sensor
  tsl.setGain(TSL2591_GAIN_LOW);
  tsl.setTiming(TSL2591_INTEGRATIONTIME_100MS);

  // Serial.println("Ready to go!");
  // initialize state to name entry
  state = ENTER_NAME;
  updated = true;
  // Serial.println("test");

  // open_log.searchDirectory("LOG*.TXT"); //Give me a list of just the logs
  // String LOG_name = open_log.getNextDirectoryItem(); //looking through the list of logs

  // while (LOG_name != "") //getNextDirectoryItem() will return "" when we've hit the end of the directory
  // {
  //   // Serial.println(LOG_name);
  //   open_log.removeFile(LOG_name);
  //   LOG_name = open_log.getNextDirectoryItem();
  // }
  // // Serial.println(F("Done!"));

}

void loop() {

  // get updated button statuses
  int red_status = red.update_status();
  int green_status = green.update_status();

  // check for button disconnection:
  if (red_status == -1 || green_status == -1) {
    // Serial.println("button(s) disconnected");
    state = ERROR_BUTTON;
  }

  /* NAME ENTRY */
  if (state == ENTER_NAME) {
    // TODO: display stuff
    // update display
    // 2nd argument = index of char to highlight (if out of range i.e. -1, highlight none)
    //display.show_file_name(new_file_name, current_char);

    // update "display" (serial for now) - remove when done troubleshooting
    if (updated) { // only send updates if something has actually changed
      //tft.show_file_name(file_entry, current_name_char);
      tft.show_file_name(file_entry, current_name_char);  // call to display function
      // Serial.println("");
      // Serial.println(file_entry);
      //for (int i = 0; i < current_name_char; i++) {
        // Serial.print(" ");
      //}
      // Serial.println("^");
      updated = false;
    }

    // green button input
    if (green_status > LONG_HOLD) {
      if (strcmp(file_entry, "******") == 0)
      {
        // Serial.println(file_entry);
      }
      else {
      // post processing on entered name
      file_name = String(file_entry);
      file_name.replace("*", ""); // remove *'s from name
      file_name.concat(".txt"); // append .txt to make a text file
      // Serial.print("processed file name: ");
      // Serial.println(file_name);

      // check file name against existing files
      bool will_overwrite = check_file(file_name);
      if (will_overwrite) {
        // move to NAME_OVERWRITE
        // Serial.println("File found - change to OVERWRITE...");
        state = NAME_OVERWRITE;
      } else {
        // move to ENTER_TIME state
        // Serial.println("change to ENTER_TIME...");
        state = ENTER_TIME;
      }
      updated = true;
      }
    }
     else if (green_status > SHORT_HOLD) {
      // move forward one character
      if (current_name_char < NAME_LEN - 1) {
        current_name_char++;
        updated = true;
      }
    } else if (green_status > CLICK) {
      // increment current char
      file_entry[current_name_char] = increment_char(file_entry[current_name_char]);
      updated = true;
    } // otherwise, button was not pressed, do nothing

    // react to red button
    if (red_status > SHORT_HOLD) {
      // go back one character
      if (current_name_char > 0) {
        current_name_char--;
        updated = true;
      }
    } else if (red_status > CLICK) {
      // decrement current character
      file_entry[current_name_char] = decrement_char(file_entry[current_name_char]);
      updated = true;
    
    }
  }
  /* TIME ENTRY */
   else if (state == ENTER_TIME) {
    // remove this loop when done troubleshooting
    if (updated) { // only send updates if something has actually changed
      //tft.show_run_time(run_time, current_time_char);
      tft.show_run_time(run_time, current_time_char); // call to display function
      // Serial.println("");
      // Serial.print("min: ");
      // Serial.print(run_time[0]);
      // Serial.print(run_time[1]);
      // Serial.print(" sec: ");
      // Serial.print(run_time[2]);
      // Serial.println(run_time[3]);
      // use a cursor to indicate current char
      if (current_time_char == 0) {
        // Serial.println("     ^");
      } else if (current_time_char == 1) {
        // Serial.println("      ^");
      } else if (current_time_char == 2) {
        // Serial.println("             ^");
      } else if (current_time_char == 3) {
        // Serial.println("              ^");
      }
      updated = false;
    }

    if (green_status > LONG_HOLD) {
      // convert run time to ms and save it
      unsigned long min = run_time[0] * 10 + run_time[1];
      unsigned long sec = run_time[2] * 10 + run_time[3];
      run_time_ms = min * 60000 + sec * 1000;

      // Serial.print("Run time in ms: ");
      // Serial.println(run_time_ms);

      // Serial.println("moving to TEST_READY...");
      updated = true;
      state = TEST_READY;

    } else if (green_status > SHORT_HOLD) {
      if (current_time_char < TIME_LEN - 1) {
        current_time_char++;
        updated = true;
      }
    } else if (green_status > CLICK) {
      if (current_time_char == 2) { // max sec = 60
        run_time[current_time_char] = (run_time[current_time_char] + 1) %  6;
      } else {
        run_time[current_time_char] = (run_time[current_time_char] + 1) % 10;
      }
      updated = true;
    }

    if (red_status > LONG_HOLD) {
      // user long held red button to go back to name entry
      // Serial.println("moving to ENTER_NAME...");
      state = ENTER_NAME;

    } else if (red_status > SHORT_HOLD) {
      // user short held red button to go back 1 character
      if (current_time_char > 0) { // decrement the character index
        current_time_char--;
        updated = true;
      }
    } else if (red_status > CLICK) {
      if (current_time_char == 2) { // max sec = 60
        run_time[current_time_char] = (run_time[current_time_char] + 6 - 1) % 6;
      } else {
        run_time[current_time_char] = (run_time[current_time_char] + 10 -1) % 10;
      }
      updated = true;
    }
  } else if (state == TEST_READY) {
    if (updated)
    {
      tft.show_test_ready(file_name, run_time); // call to display function
      //tft.show_test_ready(file_name, run_time);
      /*
      tft.fillScreen(ST77XX_BLACK);
      tft.setCursor(0,0);
      tft.setTextSize(2); */
      // Serial.println("Test ready to start");
      // Serial.println("Hold green to confirm.");

      updated = false;
    }
    if (green_status > LONG_HOLD) {
      // if confirmed ready, prep & move on to actual test

      // TODO: add in try-catch statements + error handling
      // if file_name already exists in the directory, remove it
      open_log.removeFile(file_name);
      // create a new file file_name.txt
      open_log.append(file_name);
      // write header lines to the file

      int bytes_written = 0; // for error catching

      bytes_written += open_log.print("# ");
      bytes_written += open_log.println(file_name);
      bytes_written += open_log.print("# Run time: ");
      bytes_written += open_log.print(run_time[0]);
      bytes_written += open_log.print(run_time[1]);
      bytes_written += open_log.print(" min, ");
      bytes_written += open_log.print(run_time[2]);
      bytes_written += open_log.print(run_time[3]);
      bytes_written += open_log.println(" sec");
      bytes_written += open_log.println("###");

      if (bytes_written == 0) {
        // Serial.println("caught error in openlog");
        updated = true;
        state = ERROR_LOGGER;
      }

      // flush file - flush() command
      open_log.syncFile();
      // record start time
      start_time = millis();

      // move to test in progress state to start test
      state = TEST_IN_PROGRESS;
      // TODO: set green LED to blink (use led cycle fxn) ?
    }
    if (red_status > LONG_HOLD) {
      // user long held red button to go back to time entry
      // Serial.println("moving to ENTER_TIME...");
      state = ENTER_TIME;
      updated = true;
    }
  } else if (state == TEST_IN_PROGRESS) {
    // stuff that should be running during a test
    time_elapsed = millis() - start_time;

    // take a measurement
    uint32_t lum = tsl.getFullLuminosity();
    uint16_t ir = lum >> 16;
    uint16_t full = lum & 0xFFFF;
    float lux = tsl.calculateLux(full, ir);
    if (lux < LIGHT_THRESHOLD) { // sensor is not connected
      // Serial.println("caught sensor error");
      state = ERROR_SENSOR;
      updated = true;
    }

    // TODO: save a measurement to an array of recent values (for display of data)

    // write measurement to file, including time stamp, separated by tab
    int bytes_written = 0;
    float displayed_seconds = time_elapsed / (float)1000;
    bytes_written += open_log.print(displayed_seconds, 3);
    bytes_written += open_log.print("\t");
    bytes_written += open_log.println(lux);
    bytes_written += open_log.syncFile();

    if (bytes_written == 0) {
      // Serial.println("caught open log error");
      updated = true;
      state = ERROR_LOGGER;
    }


    // display stuff
    // finds avg_slope value
    time_interval = time_elapsed - prev_time_elapsed;
    Serial.print("First time_interval: ");
    Serial.println(time_interval);
    time_interval = time_interval / (float)1000;
    Serial.print("Post-division time_interval: ");
    Serial.println(time_interval);
    // if (!array_full && slope_index == 0)                // just a base case for the very first lux reading, so that a slope will still be displayed
    // {
    //   slopes[slope_index] = (lux / time_interval);
    // }
    // else                                                // finds slope between current lux value and previous lux value
    // {
      cur_slope = lux - prev_lux;     
      Serial.print("First current slope: ");
      Serial.println(cur_slope);     
      cur_slope = cur_slope / (float)time_interval;
      Serial.print("Post-division slope: ");
      Serial.println(cur_slope);
      slopes[slope_index] = cur_slope;                  // puts current slope value into an array holding the last 4 slope values
    // }
    prev_lux = lux;                                     // updates the previous lux value to equal the current lux value
    slope_index++;                                      // updates slope_index
    if (slope_index >= (data_points - 2))                     // makes sure we don't access array indices that don't exist // subtract by 2?
    {
      slope_index = 0;
      array_full = true;                                // makes sure we don't re-enter our base case
    }

    float avg_slope = 0;                                // initializes our avg_slope variable
    for (int i = 0; i < (data_points - 2); i++)
    {
      avg_slope = avg_slope + slopes[i];
    }
    avg_slope = avg_slope / (float)(data_points - 1);     // avg_slope value of last x lux values
    prev_time_elapsed = time_elapsed;

    if (time_elapsed - last_update > UPDATE_INT) { // in place of the if (updated) statement
      // Serial.print(time_elapsed);
      // Serial.print("\t");
      // Serial.println(lux);
      last_update = time_elapsed;
      tft.show_test_in_progress(run_time, time_elapsed, lux, file_name, avg_slope); // call to display function
      Serial.print("Avg slope: ");
      Serial.println(avg_slope);
    }

    if (red_status > LONG_HOLD || time_elapsed >= run_time_ms) { // user cancelled test
      open_log.syncFile();
      state = TEST_ENDED;
      if (time_elapsed < run_time_ms) {
        ended_early = true;
      }
      updated = true;
    }

    // TODO: add red/green button click toggle btwn current vals and the file details screens

  } else if (state == TEST_ENDED) {
    // TODO: dipslay recap stuff
    if (updated) {
      int min = (time_elapsed / 1000) / 60; // need these variables for display function
      int sec = (time_elapsed / 1000) % 60;
      tft.show_test_ended(file_name, min, sec); // call to display function
      // red.blink_LED();
      green.blink_LED();
      // indicate test is done and why
      if (ended_early) {
        // Serial.println("Test ended");
      } else {
        // Serial.println("Test completed");
      }

      // print the run time
      // Serial.print("Actual run time: ");
      // convert elapsed_time to mm:ss
      /*
      int min = (time_elapsed / 1000) / 60;
      int sec = (time_elapsed / 1000) % 60;
      */
      // Serial.print(min);
      // Serial.print(":");
      // Serial.println(sec);

      // Serial.println("Hold GREEN to start new test");
      updated = false;
    }

    if (green_status > LONG_HOLD) {
      // if long hold on green button, start new test - go to name entry
      state = ENTER_NAME;
      current_name_char = NAME_LEN - 1;
      current_time_char = 0;
      updated = true;
    }

  } else if (state == ERROR_LOGGER) {
    logger_error();
  } else if (state == ERROR_SENSOR) {
    sensor_error();
    // arguably worse stuff?
  } else if (state == ERROR_BUTTON) {
    button_error();
  } else if (state == NAME_OVERWRITE) {
    // warning of bad stuff

    if (updated) {
      tft.show_enter_name_overwrite(file_name); // call to display function
      // TODO: update the display
      // note this will only run once when we enter this state, it's not dynamic
      // like the entry states

      // Serial.println("WARNING: Overwrite file?");
      // Serial.println(file_name);
      // Serial.println("[GREEN] confirm [RED] back");
      updated = false;
    }

    if (green_status > LONG_HOLD) {
      // user long held green to confirm file name
      state = ENTER_TIME;
      updated = true;
    }
    if (red_status > SHORT_HOLD) {
      // user held red to go back to re-enter file name
      state = ENTER_NAME;
      updated = true;
    }

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
    return '*';
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
      // Serial.print(file_name);
      // Serial.println(" found!");
      return true;
    }
    next_file = open_log.getNextDirectoryItem();
  }
  return false;
}

bool check_open_log_connection() {
  return open_log.getStatus() != 0xFF;
  /*byte status = open_log.getStatus();
  if (status == 0xFF) {
    return false;
  } else {
    return true;
  } */
}

bool check_sensor_connection() {
  return tsl.begin();
}

bool check_button_connection() {
  return red.check_connection() && green.check_connection();
}

void logger_error() {
  // TODO: add display messages
  // Serial.println("Error with open log");
  tft.show_error_logger();  // call to display function
   
  // TODO; add test to check for openlog connection
  while (!check_open_log_connection()) {
    delay(RECONNECTION_DELAY);
  }

  // Serial.println("open log connection restablished.");
  tft.show_connection_re_established("Logger");
  delay(MSG_TIME);

  updated = true;
  state = ENTER_NAME;
}

void sensor_error() {
  // TODO: add display messages  
  // Serial.println("ERROR: sensor not connected");
  tft.show_error_sensor();  // call to display function

  while(!check_sensor_connection()) {
    delay(RECONNECTION_DELAY);
  }

  // Serial.println("sensor connection restablished");
  tft.show_connection_re_established("Sensor");
  delay(MSG_TIME);

  updated = true;
  state = ENTER_NAME;
}

void button_error() {
  // TODO: add display messages
  // Serial.println("ERROR: button(s) not connected");
  tft.show_error_button();

  while(!check_button_connection()) {
    delay(RECONNECTION_DELAY);
  }

  // Serial.println("button(s) connection restablished");
  tft.show_connection_re_established("Button(s)");
  delay(MSG_TIME);

  updated = true;
  state = ENTER_NAME;
}
