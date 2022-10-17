#include <Adafruit_GFX.h> // Core graphics library
#include <Adafruit_ST7789.h> // Hardware-specific library for ST7789
#include <SPI.h>
// Use dedicated hardware SPI pins
//Adafruit_ST7789 tft = Adafruit_ST7789(TFT_CS, TFT_DC, TFT_RST);

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

void show_run_time(Adafruit_ST7789 tft , int run_time[], int index) // displays the screen to enter the run time wanted
{
    tft.fillScreen(ST77XX_BLACK); // clear the screen

    tft.setCursor(30, 0);           // sets cursor for first line
    tft.setTextSize(3);             // sets text size for file name
    tft.setTextColor(DARKCYAN);     // file name will be DARKCYAN
    tft.print("Enter time:");


    tft.setTextSize(5);             // sets text size for file name input       
    tft.setCursor(50,50);           // sets cursor for file name input
    tft.setTextColor(WHITE);        // sets file name input color to white

    for (int i = 0; i < index; i++) // for loop to print the characters user has already inputted
    {
        if (i == 2)
        {
            tft.print(":");
        }
        tft.print(run_time[i]);
    }

    if (index == 2)                 // makes sure the colon doesn't get skipped
    {
        tft.print(":");
    }

    tft.setTextColor(ORANGE);       
    tft.print(run_time[index]);   // prints out current char in ORANGE that user needs to edit
    tft.setTextColor(WHITE);
    for (int i = index + 1; i < 4; i++)     // prints out remaining chars in WHITE that user still can change
    {
        if (i == 2)
        {
            tft.print(":");
        }
        tft.print(run_time[i]);
    }
    tft.setCursor(50, 90);                  // code for the carrot that follows the current char that can be changed
    tft.setTextColor(ORANGE);
    for (int i = 0; i < index; i++)         // prints out spaces unless the carrot needs to be printed
    {
        if (i == 2)
        {
            tft.print(" ");
        }
        tft.print(" ");
    }
    if (index == 2)                         // adds an extra space to account for the colon
    {
      tft.print(" ");
    }
    tft.print("^");                         // prints the carrot so that it is under the current char
    for (int i = index + 1; i < 4; i++)
    {
        if (i == 2)
        {
            tft.print(" ");                 // adds an extra space to account for the colon
        }
        tft.print(" ");
    }
    tft.setTextSize(2);                // changes text size to be smaller than important info about program
    tft.setTextColor(LIGHTGREY);
    tft.setCursor(20,120);
    tft.println("minutes : seconds");   // descriptive info to show user what the numbers are
}


 
void show_test_ready(Adafruit_ST7789 tft ,char file_name[], int run_time[])
{
    tft.fillScreen(ST77XX_BLACK); // clear the screen

    // unsigned long min, sec;     // variables needed to show individual mins and secs
    tft.setCursor(0, 0);        // sets cursor for first line
    tft.setTextSize(4);         // sets text size for file name and run time
    tft.setTextColor(ORANGE);   // file name will be orange
    tft.print(file_name);       // prints file name to screen
    tft.println(".txt");        // adds ".txt" to end of inputted file name on the display screen
    tft.setCursor(70,55);       // sets cursor for run time
    tft.setTextColor(DARKCYAN); // sets run time color to DarkCyan
    
    for (int i = 0; i < 4; i++) // for loop prints out the run time that the user inputted
    {
        if (i == 2)
        {
            tft.print(":");
        }
        tft.print(run_time[i]);
    }
    
    tft.setTextColor(ST77XX_GREEN);    // sets instructions for user to be in green
    tft.setTextSize(2);                // changes text size to be smaller than important info about program
    tft.setCursor(10,110);
    tft.println("Hold green to START");
} 


void show_test_in_progress(Adafruit_ST7789 tft, int run_time[], unsigned long time_elapsed, unsigned long recent_val, char file_name[]) // displays screen with time elapsed and active trendline
{
     tft.fillScreen(ST77XX_BLACK); // clear the screen

    tft.setCursor(0,0);             // changing cursor, text size, and color to display informational words
    tft.setTextSize(2);
    tft.setTextColor(ORANGE);
    tft.println("Time");
    tft.setCursor(0, 20);
    tft.println("Elapsed:");

    tft.setTextColor(WHITE);
    tft.setCursor(0, 40);
    unsigned long min, sec;         // variables needed to show individual mins and secs
    min = time_elapsed / 100;       // finds the values that will go in front of the colon (mins)
    if (min < 10)                   // if min value is below 10, it will add a placeholder 0
    {
        tft.print("0");
    }
    tft.print(min);   
    tft.print(":");             
    sec = time_elapsed % 100;       // operation to find seconds of elapsed-time
    if (sec < 10)                   // if sec value is below 10, it will add a placeholder 0
    {
        tft.print("0");
    }
    tft.println(sec);

    tft.setCursor(0, 70);           // displays words to tell user what value underneath is
    tft.setTextColor(ORANGE);
    tft.println("Cur lux:");        
    tft.setCursor(0,90);
    tft.setTextSize(3);
    tft.setTextColor(WHITE);
    tft.println(recent_val);        // prints out current lux

    tft.setTextColor(DARKGREY);     // prints out user inputted run time in bottom right corner
    tft.setCursor(210, 125);
    tft.setTextSize(1);
    for (int i = 0; i < 4; i++)
    {
        if (i == 2)
        {
            tft.print(":");
        }
        tft.print(run_time[i]);
    }

    tft.setCursor(0, 125);
    tft.print(file_name);           // prints out file name on bottom left corner

// area to test out trendline display

    int horizontal_end;
    int vertical_end;

    if (avg_slope > 1)                            // if slope is greater than one then it will be a much more vertical line and the starting horizontal point will change depending on slope value
    {
        vertical_end = 0;
        horizontal_end = (50/avg_slope) + 50;
    }
    else if (avg_slope == 1)
    {
        horizontal_end = 100;
        vertical_end = 0;
    }
    else if (avg_slope == 0)
    {
        horizontal_end = 100;
        vertical_end = 50;
    }
    else if (avg_slope == -1)
    {
        vertical_end = 0;
        horizontal_end = 0;
    }
    else if (avg_slope < 0 && avg_slope > -1)
    {
        horizontal_end = 0;
        vertical_end = (((-50 * avg_slope) - 50) * (-1));
        // vertical_end = vertical_end + 100;
    }
    else if (avg_slope < -1)
    {
        vertical_end = 0;
        horizontal_end = (50/avg_slope) + 50;
    }
    else if (avg_slope < 1)                                                    // this means the slope will be less than 1 and therefore a shallower line
    {
        horizontal_end = 100;
        vertical_end = (((-50 * avg_slope) - 50) * (-1));
        vertical_end = 100 - vertical_end;
    }

    int two_horizontal_end = horizontal_end - 50;
    two_horizontal_end = 50 - two_horizontal_end;

    int two_vertical_end = vertical_end - 50;
    two_vertical_end = 50 - two_vertical_end;
    

    int horizontal_shift = 120;
    int vertical_shift = 10;

    tft.drawLine(50 + horizontal_shift, 50 + vertical_shift, horizontal_end + horizontal_shift, vertical_end + vertical_shift, CYAN); // draws line
    tft.drawLine(50 + horizontal_shift, 50 + vertical_shift, two_horizontal_end + horizontal_shift, two_vertical_end + vertical_shift, CYAN); // draws line

    tft.drawRect(120 ,10 , 100 , 100, DARKGREY); 
// ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

}


void show_test_ended(Adafruit_ST7789 tft ,char file_name[], unsigned long min, unsigned long sec) // displays test ended screen w/ file name and actual time elapsed
{
    tft.fillScreen(ST77XX_BLACK); // clear the screen

    tft.setCursor(70, 0);        // sets cursor for first line
    tft.setTextSize(2);         // sets text size for displayed information
    tft.setTextColor(DARKGREY);   // text will be dark grey
    tft.println("Test Ended");      // prints out "Test Ended"

    tft.setTextColor(WHITE);    // changes text color, size, and location on screen
    tft.setTextSize(3);
    tft.setCursor(35, 25);
    tft.print(file_name);       // prints file name to screen
    tft.println(".txt");        // adds ".txt" to end of inputted file name on the display screen

    tft.setCursor(35,65);       // sets cursor for run time
    tft.setTextSize(2);
    tft.setTextColor(DARKCYAN); // sets run time color to DarkCyan
    tft.println("Actual Runtime:"); // prints out text
    tft.setTextSize(3);
    tft.setCursor(75, 85);          // changes text size, color, and location for the actual value of run time to be printed to screen
    tft.setTextColor(WHITE);


    if (min < 10)               // if min value is below 10, it will add a placeholder 0
    {
        tft.print("0");
    }
    tft.print(min);             // prints min value to screen
    tft.print(":");             // adds a colon to seperate min and sec value
    if (sec < 10)               // if sec value is below 10, it will add a placeholder 0
    {
        tft.print("0");
    }
    tft.println(sec);           // prints sec value to screen

    tft.setTextColor(ST77XX_GREEN);    // sets instructions for user to be in green
    tft.setTextSize(2);                // changes text size to be smaller than important info about program
    tft.setCursor(15,115);
    tft.println("[green] new test");
}

void show_error_logger(Adafruit_ST7789 tft)
{
    tft.fillScreen(ST77XX_BLACK); // clear the screen

    tft.setCursor(0,0);         // writes text to the screen to tell user that an error has occured
    tft.setTextSize(3);
    tft.setTextColor(RED);
    tft.print("ERROR:");
    tft.setTextSize(2);
    tft.println(" file write");    

    tft.setCursor(0, 45);
    tft.println("Check micro SD card");
    tft.setCursor(0, 65);
    tft.println("and open log");
    tft.setCursor(0,85);
    tft.println("connection.");
    tft.setTextColor(DARKGREEN);
    tft.setCursor(0, 115);
    tft.println("Press GREEN to reset");
}

void show_error_sensor(Adafruit_ST7789 tft)
{
    tft.fillScreen(ST77XX_BLACK);   // clear the screen

    tft.setCursor(0,0);             // writes text to the screen to tell user that an error has occured
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

void show_enter_name_overwrite(Adafruit_ST7789 tft, char file_name[]) // displays warnning screen if about to overwrite previous file name
{
    tft.fillScreen(ST77XX_BLACK); // clear the screen

    tft.setCursor(55,0);            // warns user about warning
    tft.setTextSize(3);
    tft.setTextColor(RED);
    tft.print("WARNING:"); 
    tft.setCursor(20    , 25);
    tft.setTextSize(2);
    tft.println(" overwrite file?");

    tft.setTextColor(ORANGE);
    tft.setTextSize(3);
    tft.setCursor(25, 60);
    tft.print(file_name);       // prints file name to screen
    tft.println(".txt");        // adds ".txt" to end of inputted file name on the display screen

    tft.setCursor(0,100);
    tft.setTextSize(2);
    tft.setTextColor(GREEN);
    tft.print("[green] confirm");       // tells user to press green to overwrite and confirm
    tft.setCursor(0, 120);
    tft.setTextColor(RED);
    tft.print("[red] go back");         // tells user to press red to go back and change file name

}   


void show_error_button(Adafruit_ST7789 tft)
{
    tft.fillScreen(ST77XX_BLACK);   // clear the screen

    tft.setCursor(0,0);             // writes text to the screen to tell user that an error has occured
    tft.setTextSize(3);
    tft.setTextColor(RED);
    tft.print("ERROR:"); 
    tft.setTextSize(2);
    tft.println(" button");
    tft.setCursor(0, 25);
    tft.println("disconnected");

    tft.setCursor(65, 55);
    tft.println("Check button");
    tft.setCursor(68, 75);
    tft.println("connection.");
    tft.setTextColor(DARKGREEN);
    tft.setCursor(0, 115);
    tft.println("Press GREEN to reset");

}


void show_connection_re_established(Adafruit_ST7789 tft, char re_established[]) // displays warnning screen if about to overwrite previous file name
{
    tft.fillScreen(ST77XX_BLACK); // clear the screen

    tft.setCursor(45,0);            // warns user about warning
    tft.setTextSize(3);
    tft.setTextColor(DARKGREEN);
    tft.print(re_established); 
    tft.setCursor(0, 25);
    tft.setTextSize(2);
    tft.println("connection re-established");

    tft.setTextColor(DARKGREY);
    tft.setTextSize(2);
    tft.setCursor(10, 60);
    tft.println("Test resetting...");     

/*
    tft.setCursor(0,100);
    tft.setTextSize(2);
    tft.setTextColor(GREEN);
    tft.print("[green] confirm");       // tells user to press green to overwrite and confirm
    tft.setCursor(0, 120);
    tft.setTextColor(RED);
    tft.print("[red] go back");         // tells user to press red to go back and change file name
*/
}   