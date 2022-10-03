#include <Adafruit_GFX.h> // Core graphics library
#include <Adafruit_ST7789.h> // Hardware-specific library for ST7789
#include <SPI.h>
// Use dedicated hardware SPI pins
Adafruit_ST7789 tft = Adafruit_ST7789(TFT_CS, TFT_DC, TFT_RST);

// colors defined
#define ORANGE 0xFD20
#define NAVY 0x000F
#define DARKCYAN 0x03EF



void show_file_name(file_name); // displays the screen to enter the file name

void show_run_time(run_time); // displays the screen to enter the run time wanted

void show_test_ready(char file_name[6], unsigned long run_time); // displays ready to start screen

void show_test_in_progress(run_time, time_elapsed, recent_val); // displays screen with time elapsed and active trendline

void show_test_ended(file_name, time_elapsed); // displays test ended screen w/ file name and actual time elapsed

void show_error_logger();

void show_error_sensor();

void show_enter_name_overwrite(); // displays waring screen if about to overwrite previous file name



void show_test_ready(char file_name[6], unsigned long run_time)
{
    unsigned long min, sec;     // variables needed to show individual mins and secs
    tft.setCursor(0, 0);        // sets cursor for first line
    tft.setTextSize(4);         // sets text size for file name and run time
    tft.setTextColor(ORANGE);   // file name will be orange
    tft.print(file_name);       // prints file name to screen
    tft.println(".txt");        // adds ".txt" to end of inputted file name on the display screen
    tft.setCursor(70,55);       // sets cursor for run time
    tft.setTextColor(DARKCYAN); // sets run time color to DarkCyan
    min = run_time / 100;       // finds the values that will go in front of the colon
    if (min < 10)               // if min value is below 10, it will add a placeholder 0
    {
        tft.print("0");
    }
    tft.print(min);   
    tft.print(":");             
    sec = run_time % 100;       // operation to find seconds of user-inputted run-time
    if (sec < 10)               // if sec value is below 10, it will add a placeholder 0
    {
        tft.print("0");
    }
    tft.println(sec);
    tft.setTextColor(ST77XX_GREEN);    // sets instructions for user to be in green
    tft.setTextSize(2);                // changes text size to be smaller than important info about program
    tft.setCursor(10,110);
    tft.println("Hold green to START");
}