/*
 * Code for the magnetophotometer (MAP).
 * Class Definition: Display
 * Written by: Lexie Scholtz
 *             Vic Nunez
 * Created: 2022.09.29
 * Last Updated: 2024.12.12
*/

#include "Display.h"

Display::Display() {
  meas_num = 0;
  meas_int = 0;
  last_meas = -1 * LONG_MIN;  // set arbitrary to be less than measurement interval

  // initialize measurement array
  for (int i = 0; i < NUM_MEAS; i++) {
    meas[i] = 0;
  }

  max_lux = 0;
}

void Display::begin() {
  Serial.println("in Display::begin()");
  tft.init(135, 240);  // Init ST7789 240x135
  tft.setRotation(3);
  tft.fillScreen(ST77XX_BLACK);
}

void Display::clear_screen() {
  tft.fillScreen(ST77XX_BLACK);
}

void Display::show_LED_stablization(unsigned long time_elapsed, float lux) {
  Serial.println("In LED Stabilization screen");
  tft.fillScreen(ST77XX_BLACK);  // clear the screen

  tft.setTextColor(ORANGE);
  tft.setCursor(40, 20);        // sets cursor for first line
  tft.setTextSize(2);           // sets text size for LED WARMING UP line
  tft.print("LED Warming Up");  // prints instructions

  tft.setTextSize(5);       // sets text size for file name input
  tft.setCursor(50, 60);    // sets cursor for file name input
  tft.setTextColor(WHITE);  // sets file name input color to white

  int min, sec;                      // variables needed to show individual mins and secs
  min = (time_elapsed / 1000) / 60;  // need these variables for display function
  sec = (time_elapsed / 1000) % 60;
  if (min < 10)  // if min value is below 10, it will add a placeholder 0
  {
    tft.print("0");
  }
  tft.print(min);
  tft.print(":");
  if (sec < 10)  // if sec value is below 10, it will add a placeholder 0
  {
    tft.print("0");
  }
  tft.println(sec);

  tft.setTextColor(DARKGREY);
  tft.setTextSize(2);
  tft.setCursor(35, 110);
  tft.print("Curr Lux: ");
  if (lux >= 1000) {
    tft.println(lux, 0);  // cuts off decimal values if current lux value is larger than 1000
  } else {
    tft.println(lux);  // prints out current lux
  }
}

void Display::set_max_lux(float lux) {
  max_lux = lux + 1000;
}

void Display::show_file_name(char file_entry[], int index) {
  Serial.println("IN NAME ENTRY");
  tft.fillScreen(ST77XX_BLACK);  // clear the screen

  tft.setCursor(25, 0);           // sets cursor for first line
  tft.setTextSize(2);             // sets text size for file name
  tft.setTextColor(DARKCYAN);     // file name will be DARKCYAN
  tft.print("Enter file name:");  // prints instructions
  tft.setTextSize(4);             // sets text size for file name input
  tft.setCursor(30, 40);          // sets cursor for file name input
  tft.setTextColor(WHITE);        // sets file name input color to white

  for (int i = 0; i < index; i++)  // for loop to print the characters user has already inputted
  {
    tft.print(file_entry[i]);
  }
  tft.setTextColor(ORANGE);
  tft.print(file_entry[index]);  // prints out current char in ORANGE that user needs to edit
  tft.setTextColor(WHITE);
  for (int i = index + 1; i < 8; i++)  // prints out remaining chars in WHITE that user still can change
  {
    tft.print(file_entry[i]);
  }
  tft.setCursor(30, 75);  // code for the carrot that follows the current char that can be changed
  tft.setTextColor(ORANGE);
  for (int i = 0; i < index; i++)  // prints out spaces unless the carrot needs to be printed
  {
    tft.print(" ");
  }
  tft.print("^");  // prints the carrot so that it is under the current char
  for (int i = index + 1; i < 8; i++) {
    tft.print(" ");
  }
  tft.setTextColor(RED);  // sets instructions for user to be in RED
  tft.setTextSize(2);     // changes text size to be smaller than important info about program
  tft.setCursor(20, 100);
  tft.println("Asterisks will be");  // prints instructions
  tft.setCursor(75, 115);
  tft.println("ignored.");
}

void Display::show_run_time(int run_time[], int index) {
  tft.fillScreen(ST77XX_BLACK);  // clear the screen

  tft.setCursor(30, 0);        // sets cursor for first line
  tft.setTextSize(3);          // sets text size for file name
  tft.setTextColor(DARKCYAN);  // file name will be DARKCYAN
  tft.print("Enter time:");


  tft.setTextSize(5);       // sets text size for file name input
  tft.setCursor(50, 50);    // sets cursor for file name input
  tft.setTextColor(WHITE);  // sets file name input color to white

  for (int i = 0; i < index; i++)  // for loop to print the characters user has already inputted
  {
    if (i == 2) {
      tft.print(":");
    }
    tft.print(run_time[i]);
  }

  if (index == 2)  // makes sure the colon doesn't get skipped
  {
    tft.print(":");
  }

  tft.setTextColor(ORANGE);
  tft.print(run_time[index]);  // prints out current char in ORANGE that user needs to edit
  tft.setTextColor(WHITE);
  for (int i = index + 1; i < 4; i++)  // prints out remaining chars in WHITE that user still can change
  {
    if (i == 2) {
      tft.print(":");
    }
    tft.print(run_time[i]);
  }
  tft.setCursor(50, 90);  // code for the carrot that follows the current char that can be changed
  tft.setTextColor(ORANGE);
  for (int i = 0; i < index; i++)  // prints out spaces unless the carrot needs to be printed
  {
    if (i == 2) {
      tft.print(" ");
    }
    tft.print(" ");
  }
  if (index == 2)  // adds an extra space to account for the colon
  {
    tft.print(" ");
  }
  tft.print("^");  // prints the carrot so that it is under the current char
  for (int i = index + 1; i < 4; i++) {
    if (i == 2) {
      tft.print(" ");  // adds an extra space to account for the colon
    }
    tft.print(" ");
  }
  tft.setTextSize(2);  // changes text size to be smaller than important info about program
  tft.setTextColor(LIGHTGREY);
  tft.setCursor(20, 120);
  tft.println("minutes : seconds");  // descriptive info to show user what the numbers are
}

void Display::show_test_ready(String file_name, int run_time[]) {
  tft.fillScreen(ST77XX_BLACK);  // clear the screen

  tft.setCursor(15, 0);        // sets cursor for first line
  tft.setTextSize(3);          // sets text size for file name and run time
  tft.setTextColor(ORANGE);    // file name will be orange
  tft.print(file_name);        // prints file name to screen
  tft.setCursor(70, 55);       // sets cursor for run time
  tft.setTextColor(DARKCYAN);  // sets run time color to DarkCyan

  for (int i = 0; i < 4; i++)  // for loop prints out the run time that the user inputted
  {
    if (i == 2) {
      tft.print(":");
    }
    tft.print(run_time[i]);
  }

  // set measurement interval time
  meas_int = ((int(run_time[0]) * 10 + int(run_time[1])) * 60 + (int(run_time[2]) * 10 + int(run_time[3]))) * 1000 / NUM_MEAS;

  tft.setTextColor(ST77XX_GREEN);  // sets instructions for user to be in green
  tft.setTextSize(2);              // changes text size to be smaller than important info about program
  tft.setCursor(10, 110);
  tft.println("Hold green to START");
}

void Display::show_countdown() {
  tft.fillScreen(ST77XX_BLACK);  // clear the screen
  tft.setCursor(0, 0);
  tft.setTextSize(2);
  tft.setTextColor(WHITE);

  tft.println("Get ready to push");
  tft.println("magnet in...");

  delay(1500);

  tft.setTextColor(RED);
  tft.setTextSize(3);
  tft.setCursor(15, 50);
  tft.print("3");
  for (int i = 0; i < 3; i++) {
    tft.print(".");
    delay(333);
  }

  tft.print("2");
  for (int i = 0; i < 3; i++) {
    tft.print(".");
    delay(333);
  }

  tft.print("1");
  for (int i = 0; i < 3; i++) {
    tft.print(".");
    delay(333);
  }

  tft.setTextSize(5);
  tft.setTextColor(GREEN);
  tft.setCursor(80, 90);
  tft.print("GO!");
}



void Display::show_test_in_progress(int run_time[], unsigned long time_elapsed, float recent_val, String file_name, float avg_slope)  // displays screen with time elapsed and active trendline
{
  //tft.fillScreen(ST77XX_BLACK); // clear the screen
  tft.fillRect(0, 0, X_START-2, 144, ST77XX_BLACK);

  tft.setTextColor(DARKGREY);  // prints out user inputted run time in bottom right corner
  tft.setCursor(180, 0);
  tft.setTextSize(2);
  for (int i = 0; i < 4; i++) {
    if (i == 2) {
      tft.print(":");
    }
    tft.print(run_time[i]);
  }

  tft.setCursor(0, 0);
  tft.print(file_name);  // prints out file name on bottom left corner

  tft.setCursor(0, 30);  // changing cursor, text size, and color to display informational words
  tft.setTextSize(2);
  tft.setTextColor(ORANGE);
  tft.println("Time");

  tft.setTextColor(WHITE);
  tft.setCursor(0, 50);
  int min, sec;                      // variables needed to show individual mins and secs
  min = (time_elapsed / 1000) / 60;  // need these variables for display function
  sec = (time_elapsed / 1000) % 60;
  if (min < 10)  // if min value is below 10, it will add a placeholder 0
  {
    tft.print("0");
  }
  tft.print(min);
  tft.print(":");
  if (sec < 10)  // if sec value is below 10, it will add a placeholder 0
  {
    tft.print("0");
  }
  tft.println(sec);

  tft.setCursor(0, 80);  // displays words to tell user what value underneath is
  tft.setTextColor(ORANGE);
  tft.println("Intensity:");
  tft.setCursor(0, 100);
  tft.setTextSize(3);
  tft.setTextColor(WHITE);


  if (recent_val >= 1000) {
    tft.println(recent_val, 0);  // cuts off decimal values if current lux value is larger than 1000
  } else {
    tft.println(recent_val);  // prints out current lux
  }

  tft.drawRect(X_START - 1, Y_START - 1, NUM_MEAS + 1, NUM_MEAS + 1, DARKGREY);  // draws grey rectangle to outline area where line can be displayed on the screen

  // add point to graph
  if (time_elapsed > meas_int * meas_num) {
    int y_pixel = Y_START + NUM_MEAS - int(recent_val / max_lux * NUM_MEAS) - 1;  // TODO THIS IS WRONG. NEEDS TO GO UP
    tft.fillRect(X_START + meas_num, y_pixel - 3, 3, 3, RED);
    meas_num++;
  }
}

void Display::show_test_ended(String file_name, int min, int sec) { // displays test ended screen w/ file name and actual time elapsed
  // clear only relevant parts of screen
  tft.fillRect(0, 0, X_START - 2, 144, ST77XX_BLACK);
  tft.fillRect(0, 0, 240, 15, ST77XX_BLACK);

  tft.setTextSize(2);

  tft.setTextColor(WHITE);
  tft.setCursor(0, 00);
  tft.print(file_name);

  // display test params for test that just ended
  tft.setCursor(0, 30);  
  tft.setTextSize(2);
  tft.setTextColor(GREEN);
  tft.println("TEST ENDED");



  tft.setCursor(0, 50); 
  tft.setTextColor(DARKGREY);
  tft.println("Runtime:");
  tft.setCursor(0, 70);
  tft.setTextSize(2);
  tft.setTextColor(WHITE);

  if (min < 10) {  // if min value is below 10, it will add a placeholder 0
    tft.print("0");
  }
  tft.print(min);  // prints min value to screen
  tft.print(":");  // adds a colon to seperate min and sec value
  if (sec < 10) {  // if sec value is below 10, it will add a placeholder 0
    tft.print("0");
  }
  tft.println(sec);  // prints sec value to screen

  tft.setTextColor(ST77XX_GREEN);  // sets instructions for user to be in green
  tft.setTextSize(2);              // changes text size to be smaller than important info about program
  tft.setCursor(0, 100);
  tft.println("[green]");
  tft.setCursor(0, 120);
  tft.println("new test");
}

void Display::show_error_logger() {
  tft.fillScreen(ST77XX_BLACK);  // clear the screen

  tft.setCursor(0, 0);  // writes text to the screen to tell user that an error has occured
  tft.setTextSize(3);
  tft.setTextColor(RED);
  tft.print("ERROR:");
  tft.setTextSize(2);
  tft.println(" file write");

  tft.setCursor(0, 45);
  tft.println("Check micro SD card");
  tft.setCursor(0, 65);
  tft.println("and open log");
  tft.setCursor(0, 85);
  tft.println("connection. Reset");
  tft.setCursor(0, 105);
  tft.println("system when done.");
}

void Display::show_error_sensor() {
  tft.fillScreen(ST77XX_BLACK);  // clear the screen

  tft.setCursor(0, 0);  // writes text to the screen to tell user that an error has occured
  tft.setTextSize(3);
  tft.setTextColor(RED);
  tft.print("ERROR:");
  tft.setTextSize(2);
  tft.println(" light");
  tft.setCursor(0, 25);
  tft.println("sensor");

  tft.setCursor(65, 55);
  tft.println("Check sensor");
  tft.setCursor(68, 75);
  tft.println("connection.");
  tft.setTextColor(DARKGREEN);
  tft.setCursor(0, 115);
  tft.println("Press GREEN to reset");
}

void Display::show_enter_name_overwrite(String file_name)  // displays warnning screen if about to overwrite previous file name
{
  tft.fillScreen(ST77XX_BLACK);  // clear the screen

  tft.setCursor(45, 0);  // warns user about potential name overwrite
  tft.setTextSize(3);
  tft.setTextColor(RED);
  tft.print("WARNING:");
  tft.setCursor(20, 25);
  tft.setTextSize(2);
  tft.println(" overwrite file?");

  tft.setTextColor(ORANGE);
  tft.setTextSize(3);
  tft.setCursor(15, 60);
  tft.print(file_name);  // prints file name to screen
  tft.setCursor(0, 100);
  tft.setTextSize(2);
  tft.setTextColor(GREEN);
  tft.print("[green] confirm");  // tells user to press green to overwrite and confirm
  tft.setCursor(0, 120);
  tft.setTextColor(RED);
  tft.print("[red] go back");  // tells user to press red to go back and change file name
}

void Display::show_error_button() {
  tft.fillScreen(ST77XX_BLACK);  // clear the screen

  tft.setCursor(0, 0);  // writes text to the screen to tell user that an error has occured
  tft.setTextSize(3);
  tft.setTextColor(RED);
  tft.print("ERROR:");
  tft.setTextSize(2);
  tft.println(" button(s)");
  tft.setCursor(0, 25);
  tft.println("disconnected");

  tft.setCursor(55, 55);
  tft.println("Check button(s)");
  tft.setCursor(55, 75);
  tft.println("connection.");
  tft.setTextColor(DARKGREEN);
  tft.setCursor(0, 115);
}

void Display::show_connection_re_established(char re_established[])  // displays warnning screen if about to overwrite previous file name
{
  tft.fillScreen(ST77XX_BLACK);  // clear the screen

  tft.setCursor(45, 0);  // prints test to screen to let user know connection is re-established and test is resetting
  tft.setTextSize(3);
  tft.setTextColor(DARKGREEN);
  tft.print(re_established);
  tft.setCursor(35, 25);
  tft.setTextSize(2);
  tft.println("connection");
  tft.setCursor(25, 45);
  tft.println("re-established");


  tft.setTextColor(DARKGREY);
  tft.setTextSize(2);
  tft.setCursor(10, 100);
  tft.println("Test resetting...");
}
