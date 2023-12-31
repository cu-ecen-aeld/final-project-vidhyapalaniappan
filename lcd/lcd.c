/********************************************************************************************************************************************************
 File name        : lcd.c
 ​Description      : A basic lcd code to test the functionality of lcd.c
 File​ ​Author​ ​Name : Vidhya. PL & Ashwin Ravindra
 Date             : 11/28/2023
 Credits          : https://github.com/anuh7/final-project-assignment-anuh/blob/main/client/lcd.c
 **********************************************************************************************************************************************************
*/

/*Including necessary header files*/
#include <stdio.h>
#include <stdlib.h>
#include <syslog.h>
#include "wiringpi.h"
#include "lcd.h"

/*Defining MACROS*/
#define LCD_EN 24
#define LCD_RS 25
#define LCD_D4 4
#define LCD_D5 17
#define LCD_D6 27
#define LCD_D7 22

static int lcd_addr[] = {0x80, 0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88,0x89, 0x8A, 0x8B, 0x8C, 0x8D, 0x8E, 0x8F,
                       0xC0, 0xC1, 0xC2, 0xC3, 0xC4, 0xC5, 0xC6, 0xC7, 0xC8 ,0xC9, 0xCA, 0xCB, 0xCC, 0xCD, 0xCE, 0xCF,
	               0x90, 0x91, 0x92, 0x93, 0x94, 0x95, 0x96, 0X97, 0x98, 0x99, 0x9A, 0x9B, 0x9C ,0x9D, 0x9E, 0x9F,
	               0xD0, 0xD1, 0xD2, 0xD3, 0xD4, 0xD5, 0xD6, 0xD7, 0xD8, 0xD9, 0xDA, 0xDB, 0xDC ,0xDD, 0xDE, 0xDF};

//This function is responsible for generating a pulse on the enable pin of an LCD.
void Pulse_Enable()
{
   digitalWrite (LCD_EN, HIGH) ; 
   delay(0.5); //  1/2 microsecond pause - enable pulse must be > 450ns
   digitalWrite (LCD_EN, LOW) ; 
}

//This function is used to set the LCD into command mode. It achieves this by setting the RS (Register Select) pin of the LCD (LCD_RS) to LOW
void setcmd_mode()
{
  digitalWrite (LCD_RS, 0); // set for commands
}

//This function sets the LCD into character mode. It accomplishes this by setting the RS pin of the LCD (LCD_RS) to HIGH.
void setchar_mode()
{
  digitalWrite (LCD_RS, 1); // set for characters
}

//This function is responsible for sending a byte of data to an LCD display in 4-bit mode
void lcd_byte(char bits)
{
  digitalWrite (LCD_D4,(bits & 0x10)) ;
  digitalWrite (LCD_D5,(bits & 0x20)) ;
  digitalWrite (LCD_D6,(bits & 0x40)) ;
  digitalWrite (LCD_D7,(bits & 0x80)) ;
  Pulse_Enable();

  digitalWrite (LCD_D4,(bits & 0x1)) ;
  digitalWrite (LCD_D5,(bits & 0x2)) ;
  digitalWrite (LCD_D6,(bits & 0x4)) ;
  digitalWrite (LCD_D7,(bits & 0x8)) ;
  Pulse_Enable();
}

//This function is used to display a string of characters on the LCD.
void lcd_str(char *str)
{
  while(*str)
  {
   lcd_byte(*str++);
  }
}

//This function is designed to print a single character c at a specific address (addr) on the LCD display.
void printchar(char c, int addr)
{
   setcmd_mode();
   lcd_byte(addr);
   delay(3);
   setchar_mode();
   lcd_byte(c);
}

//This function initializes the LCD display. It first sets up the Raspberry Pi GPIO pins for output by using the wiringPiSetupGpio() function
void lcd_init()
{
   wiringPiSetupGpio () ; // use BCIM numbering
   // set up pi pins for output
   pinMode (LCD_EN,  OUTPUT);
   pinMode (LCD_RS, OUTPUT);
   pinMode (LCD_D4, OUTPUT);
   pinMode (LCD_D5, OUTPUT);
   pinMode (LCD_D6, OUTPUT);
   pinMode (LCD_D7, OUTPUT);

   // initialise LCD
   setcmd_mode();  // set for commands
   lcd_byte(0x33); // full init
   lcd_byte(0x32); // 4 bit mode
   lcd_byte(0x28); // 2 line mode
   lcd_byte(0x0C); // display on, cursor off
   lcd_byte(0x01); // clear screen
   delay(3);       // clear screen is slow!
   syslog(LOG_DEBUG,"LCD Initialization successful\n");
}


int main(int argc, char *argv [])
{
   openlog(NULL, LOG_CONS | LOG_PID | LOG_PERROR, LOG_USER);   //opening syslog
   lcd_init();            //initializing lcd
   setchar_mode();
   char *str = argv[1];
   for(int i=0; str[i] !='\0'; i++)       //this for loop iterates through the input string
   {
	   printchar(str[i],lcd_addr[i]);   //printing each character on lcd
	   if(i==63) 
	   {
		   i=0;
	   }
   }
   return 0 ;
}

