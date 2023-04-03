/*
 * Code for the magnetophotometer (MAP).
 * Header class for display class
 * Written by: Lexie Scholtz
 *             Vic Nunez
 * Created: 2022.09.29
 * Last Updated: 2023.04.03
*/

#ifndef DISPLAY_H
#define DISPLAY_H

#include <Adafruit_GFX.h> // Core graphics library
#include <Adafruit_ST7789.h> // Hardware-specific library for ST7789
#include <SPI.h>

// colors defined
#define BLACK 0x0000
#define DARKGREEN 0x03E0
#define DARKCYAN 0x03EF
#define LIGHTGREY 0xC618
#define DARKGREY 0x7BEF
#define GREEN 0x07E0
#define CYAN 0x07FF
#define RED 0xF800
#define WHITE 0xFFFF
#define ORANGE 0xFD20

class Display
{
private:
    Adafruit_ST7789 tft = Adafruit_ST7789(TFT_CS, TFT_DC, TFT_RST);

public:
    // constructors
    Display(){};

    // functions
    void begin(); // initializes the screen
    void show_LED_stablization(unsigned long time_elapsed); // initial screen

    void show_file_name(char file_entry[], int index); // displays the screen to enter the file name
    void show_run_time(int run_time[], int index); // displays the screen to enter the run time wanted
    void show_test_ready(String file_name, int run_time[]); // screen tells user what info they inputted and tells them test is ready to start 
    void show_test_in_progress(int run_time[], unsigned long time_elapsed, float recent_val, String file_name, float avg_slope); // displays screen with time elapsed and active trendline
    void show_test_ended(String file_name, int min, int sec); // displays test ended screen w/ file name and actual time elapsed
    void show_error_logger();   // displays error
    void show_error_sensor();   // displays error
    void show_enter_name_overwrite(String file_name); // displays warnning screen if about to overwrite previous file name
    void show_error_button();   // displays error   
    void show_connection_re_established(char re_established[]);  // if user fixes error, this screen will appear to show them error has been fixed
};

#endif