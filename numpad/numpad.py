#@Author: Ashwin Ravindra, Vidhya Palaniappan
#Date: 12/03/2023

#Credits to Daniel Hertz @ https://maker.pro/raspberry-pi/tutorial/how-to-use-a-keypad-with-a-raspberry-pi-4

#RPi.GPIO is a library that allows you to access the GPIO pins on Raspberry Pi.
import RPi.GPIO as GPIO
import time
import subprocess
#import ctypes
#import pathlib2

#libname = pathlib2.Path().absolute() / "libcmult.so"
#c_lib = ctypes.CDLL(libname)

# L corresponds to the rows of the keypad which are connected to respective GPIO pins on the Raspberry Pi.
L1 = 5
L2 = 6
L3 = 13
L4 = 19

# C corresponds to the columns of the keypad which are connected to respective GPIO pins on the Raspberry Pi.
C1 = 12
C2 = 16
C3 = 20

keypadPressed = -1

# Secret code to be entered by the user to be authorized successfully.
secretCode = "4789"
input = ""

# Initialize the GPIO pins.
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(L1, GPIO.OUT)
GPIO.setup(L2, GPIO.OUT)
GPIO.setup(L3, GPIO.OUT)
GPIO.setup(L4, GPIO.OUT)

GPIO.setup(C1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def keypadCallback(channel):
    global keypadPressed
    if keypadPressed == -1:
        keypadPressed = channel

# Add event detection to the GPIO pins.
GPIO.add_event_detect(C1, GPIO.RISING, callback=keypadCallback)
GPIO.add_event_detect(C2, GPIO.RISING, callback=keypadCallback)
GPIO.add_event_detect(C3, GPIO.RISING, callback=keypadCallback)

# Set all the rows based on the state.
def setAllLines(state):
    GPIO.output(L1, state)
    GPIO.output(L2, state)
    GPIO.output(L3, state)
    GPIO.output(L4, state)

# Function which checks whether the rights keys are pressed.
def checkSpecialKeys():
    global input
    pressed = False

    GPIO.output(L4, GPIO.HIGH)

    if (GPIO.input(C3) == 1):
        print("Input reset!")
        subprocess.run(["lcd", "input reset!"])
        pressed = True

    GPIO.output(L4, GPIO.LOW)
    GPIO.output(L4, GPIO.HIGH)

    if (not pressed and GPIO.input(C1) == 1):
        if input == secretCode:
            print("Code correct!")
            subprocess.run(["lcd", "Code correct!"])
            #c_lib.display_lcd("Code correct!")
            # TODO: Display a message on the LCD screen, possibly send the data to a server
        else:
            subprocess.run(["lcd", "Incorrect code!"])
            print("Incorrect code!")
            # TODO: Display a message on the LCD screen, possibly send the data to a server
        pressed = True

    GPIO.output(L4, GPIO.LOW)

    if pressed:
        input = ""

    return pressed

# Function which reads the input from the keypad.
def readLine(line, characters):
    global input

    GPIO.output(line, GPIO.HIGH)

    if(GPIO.input(C1) == 1):
        input = input + characters[0]
        print(characters[0])
    if(GPIO.input(C2) == 1):
        input = input + characters[1]
        print(characters[1])
    if(GPIO.input(C3) == 1):
        print(characters[2])
        input = input + characters[2]

    GPIO.output(line, GPIO.LOW)

# Main function which runs the program infinitely until the user presses Ctrl+Z.
try:
    while True:
        if keypadPressed != -1:
            setAllLines(GPIO.HIGH)
            if GPIO.input(keypadPressed) == 0:
                keypadPressed = -1
            else:
                time.sleep(0.1)
        else:
            if not checkSpecialKeys():
                readLine(L1, ["1", "2", "3"])
                readLine(L2, ["4", "5", "6"])
                readLine(L3, ["7", "8", "9"])
                readLine(L4, ["*", "0", "#"])
                time.sleep(0.1)
            else:
                time.sleep(0.1)
except KeyboardInterrupt:
    print("\nApplication stopped!")