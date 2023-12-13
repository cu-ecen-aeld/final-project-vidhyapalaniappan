##********************************************************************************************************************************************************
## File name        : auth_system.py
## ​Description      : Code to integrate LCD, numpad and fingerprint sesnor 
## File​ ​Author​ ​Name : Vidhya. PL & Ashwin Ravindra
## Date             : 12/13/2023
## **********************************************************************************************************************************************************

##Importing the necessary header files
import RPi.GPIO as GPIO    #for numpad
import time                #for time sleeping
import subprocess          #to call a C function from python code

#TCP connection based client application in Python
import socket
import sys
from pyfingerprint.pyfingerprint import PyFingerprint   #for fingerprint

# Creating a TCP/IP socket
HOST = "169.254.59.104"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))                 #connecting to the host
    s.sendall(b"Hello from client")         #send back to client
    data = s.recv(1024)                     #recieve data from client
    
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
registration_key = "0"
delete_key = "1"
search_key = "2"
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

try:
    # initializes the sensor with specific parameters such as the device path, baud rate, and passwords
    f = PyFingerprint("/dev/ttyUSB0", 57600, 0xFFFFFFFF, 0x00000000)
    # checks if the password verification for the fingerprint sensor fails
    if f.verifyPassword() == False:

        raise ValueError("The given fingerprint sensor password is wrong!")

# If an exception is raised, it will be caught
except Exception as e:

    print("Our Exception message: " + str(e))


# Function definitions of finger print sensor:
# function handles the process of enrolling a fingerprint
def enrollFinger():
    time.sleep(2)
    print("Waiting for finger...")
    subprocess.run(["lcd", "Place finger on sensor"])  #printing on LCD
    while f.readImage() == False:
        pass
    f.convertImage(0x01)
    result = f.searchTemplate()     #checking if template already exists
    positionNumber = result[0]
    if positionNumber >= 0:
        print("Template already exists at position #" + str(positionNumber))
        subprocess.run(["lcd", "Finger already registered"])
        time.sleep(2)
        subprocess.run(["lcd", "0-reg; 1-delete; 2-search"])
        time.sleep(2)
        return
    print("Remove finger...")
    subprocess.run(["lcd", "plz remove finger now"])
    time.sleep(2)
    print("Waiting for same finger again...")
    subprocess.run(["lcd", "Place same finger again"])  
    while f.readImage() == False:
        pass
    f.convertImage(0x02)
    if f.compareCharacteristics() == 0:  #checking if the enroll of fingerprint match
        print("Fingers do not match")
        subprocess.run(["lcd", "Fingers do not match"])
        time.sleep(2)
        subprocess.run(["lcd", "0-reg; 1-delete; 2-search"])
        time.sleep(2)
        return
    f.createTemplate()
    positionNumber = f.storeTemplate()     #storing the new fingerprint in database
    print("Finger enrolled successfully!")
    subprocess.run(["lcd", "Finger enrolled succesfully"])
    time.sleep(2)
    subprocess.run(["lcd", "0-reg; 1-delete; 2-search"])
    print("New template position #" + str(positionNumber))
    time.sleep(2)


# function handles the process of searching for a fingerprint
def searchFinger():
    try:
        print("Waiting for finger...")
        subprocess.run(["lcd", "waiting for finger"])
        while f.readImage() == False:
            # pass
            time.sleep(0.5)
            return
        f.convertImage(0x01)
        result = f.searchTemplate()       #searching if the finger print already exsists
        positionNumber = result[0]
        accuracyScore = result[1] 
        if positionNumber == -1:          #fingerorint is not found
            print("No match found!")
            subprocess.run(["lcd", "Finger print not verified"])
            time.sleep(2)
            subprocess.run(["lcd", "Aunthentication failed"])
            #s.sendall(b"Aunthentication failed from client")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as a:
                a.connect((HOST, PORT))
                a.sendall(b"Aunthentication failed from client")
                data = a.recv(1024)
            time.sleep(2)
            subprocess.run(["lcd", "0-reg; 1-delete; 2-search"])
            time.sleep(2)
            return
        else:                              #fingerprint matches
            print("Found template at position #" + str(positionNumber))
            subprocess.run(["lcd", "Finger print verified"])
            time.sleep(2)
            subprocess.run(["lcd", "Aunthentication success"])
            time.sleep(2)
            #s.sendall(b"Aunthentication success from client")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
                c.connect((HOST, PORT))
                c.sendall(b"Aunthentication success from client")
                data = c.recv(1024)
            subprocess.run(["lcd", "0-reg; 1-delete; 2-search"])
            time.sleep(2)
    except Exception as e:       #Checking if any exception occured
        print("Operation failed!")
        print("Exception message: " + str(e))
        exit(1)


# function handles the process of deleting a fingerprint
def deleteFinger():
    while True:                           #this while loop gets the position input from numpad 
        pos = checkLine(L1, ["1", "2", "3"])
        if not pos == -1:
            break; 
        pos = checkLine(L2, ["4", "5", "6"])
        if not pos == -1:
            break; 
        pos = checkLine(L3, ["7", "8", "9"])
        if not pos == -1:
            break; 
    if f.deleteTemplate(pos) == True:          #deleting the fingerprint at pos number
        print("Template deleted!")
        subprocess.run(["lcd", "Finger data deleted"])
        time.sleep(2)
        subprocess.run(["lcd", "0-reg; 1-delete; 2-search"])
        time.sleep(2)


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

    if GPIO.input(C3) == 1:
        print("Input reset!")
        subprocess.run(["lcd", "input reset!"])
        time.sleep(2)
        subprocess.run(["lcd", "0-reg; 1-delete; 2-search"])
        pressed = True

    GPIO.output(L4, GPIO.LOW)
    GPIO.output(L4, GPIO.HIGH)

    if not pressed and GPIO.input(C1) == 1:
        if input == registration_key:      #if 0 is pressed, a new fingerprint can be registered
            enrollFinger()
        elif input == delete_key:          #if 1 is pressed, an existing fingerprint can be deleted
            subprocess.run(["lcd", "enter the position of fingerprint"])
            deleteFinger()
        elif input == search_key:
            searchFinger()
        elif input == secretCode:          #if input from numpad is entered, it will compare with secret code
            print("Code correct!")
            subprocess.run(["lcd", "Code correct!"])
            time.sleep(2)
            subprocess.run(["lcd", "Aunthentication success!!"])
            #s.sendall(b"Aunthentication success from client")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as d:
                d.connect((HOST, PORT))
                d.sendall(b"Aunthentication success from client")
                data = d.recv(1024)
            time.sleep(2)
            subprocess.run(["lcd", "0-reg; 1-delete; 2-search"])
            # c_lib.display_lcd("Code correct!")
            # TODO: Display a message on the LCD screen, possibly send the data to a server
        else:
            subprocess.run(["lcd", "Incorrect code!"])
            time.sleep(2)
            subprocess.run(["lcd", "Aunthentication failed!!"])
            #s.sendall(b"Aunthentication failed from client")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as e:
                e.connect((HOST, PORT))
                e.sendall(b"Aunthentication Failed from client")
                data = e.recv(1024)
            time.sleep(2)
            print("Incorrect code!")
            subprocess.run(["lcd", "0-reg; 1-delete; 2-search"])
            # TODO: Display a message on the LCD screen, possibly send the data to a server
        pressed = True

    GPIO.output(L4, GPIO.LOW)

    if pressed:
        input = ""

    return pressed


# Function which reads multiple digit input from the keypad.
def readLine(line, characters):
    global input

    GPIO.output(line, GPIO.HIGH)

    if GPIO.input(C1) == 1:
        input = input + characters[0]
        print(characters[0])
    if GPIO.input(C2) == 1:
        input = input + characters[1]
        print(characters[1])
    if GPIO.input(C3) == 1:
        print(characters[2])
        input = input + characters[2]

    GPIO.output(line, GPIO.LOW)

# Function which reads the one digit input from the keypad 
def checkLine(line, characters):
    position = -1
    GPIO.output(line, GPIO.HIGH)

    if(GPIO.input(C1) == 1):
        position = characters[0]
    if(GPIO.input(C2) == 1):
        position = characters[1]
    if(GPIO.input(C3) == 1):
        print(characters[2])
        position = characters[2]

    GPIO.output(line, GPIO.LOW)
    return int(position)

# Main function which runs the program infinitely until the user presses Ctrl+Z.
try:
    subprocess.run(["lcd", "Welcome!"])
    time.sleep(2)
    subprocess.run(["lcd", "0-reg; 1-delete; 2-search"])

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
