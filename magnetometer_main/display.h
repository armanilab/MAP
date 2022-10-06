#include <Adafruit_GFX.h> // Core graphics library
#include <Adafruit_ST7789.h> // Hardware-specific library for ST7789
#include <SPI.h>
// Use dedicated hardware SPI pins
//Adafruit_ST7789 tft = Adafruit_ST7789(TFT_CS, TFT_DC, TFT_RST);

// colors defined
#define BLACK 0x0000
#define NAVY 0x000F
#define DARKGREEN 0x03E0
#define DARKCYAN 0x03EF
#define MAROON 0x7800
#define PURPLE 0x780F
#define OLIVE 0x7BE0
#define LIGHTGREY 0xC618
#define DARKGREY 0x7BEF
#define BLUE 0x001F
#define GREEN 0x07E0
#define CYAN 0x07FF
#define RED 0xF800
#define MAGENTA 0xF81F
#define YELLOW 0xFFE0
#define WHITE 0xFFFF
#define ORANGE 0xFD20
#define GREENYELLOW 0xAFE5
#define PINK 0xF81F


/*
void show_file_name(char file_entry[], int index); // displays the screen to enter the file name

void show_run_time(run_time); // displays the screen to enter the run time wanted

void show_test_ready(char file_name[6], unsigned long run_time); // displays ready to start screen

void show_test_in_progress(run_time, time_elapsed, recent_val); // displays screen with time elapsed and active trendline

void show_test_ended(file_name, time_elapsed); // displays test ended screen w/ file name and actual time elapsed

void show_error_logger();

void show_error_sensor();

void show_enter_name_overwrite(); // displays waring screen if about to overwrite previous file name
*/


void show_file_name(Adafruit_ST7789 tft, char file_entry[], int index) // displays the screen to enter the file name
{
    tft.fillScreen(ST77XX_BLACK); // clear the screen
    
    tft.setCursor(30, 0);           // sets cursor for first line
    tft.setTextSize(2);             // sets text size for file name
    tft.setTextColor(DARKCYAN);     // file name will be DARKCYAN
    tft.print("Enter file name:");  // prints instructions
    tft.setTextSize(4);             // sets text size for file name input       
    tft.setCursor(50,40);           // sets cursor for file name input
    tft.setTextColor(WHITE);        // sets file name input color to white

    for (int i = 0; i < index; i++) // for loop to print the characters user has already inputted
    {
      tft.print(file_entry[i]);     
    }
    tft.setTextColor(ORANGE);       
    tft.print(file_entry[index]);   // prints out current char in ORANGE that user needs to edit
    tft.setTextColor(WHITE);
    for (int i = index + 1; i < 6; i++)     // prints out remaining chars in WHITE that user still can change
    {
      tft.print(file_entry[i]);
    }
    tft.setCursor(50, 75);                  // code for the carrot that follows the current char that can be changed
    tft.setTextColor(ORANGE);
    for (int i = 0; i < index; i++)         // prints out spaces unless the carrot needs to be printed
    {
      tft.print(" ");
    }
    tft.print("^");                         // prints the carrot so that it is under the current char
    for (int i = index + 1; i < 6; i++)
    {
      tft.print(" ");
    }
    tft.setTextColor(RED);                  // sets instructions for user to be in RED
    tft.setTextSize(2);                     // changes text size to be smaller than important info about program
    tft.setCursor(20,100);
    tft.println("Asterisks will be");       // prints instructions
    tft.setCursor(75, 115);
    tft.println("ignored.");
}
 /*
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
} */