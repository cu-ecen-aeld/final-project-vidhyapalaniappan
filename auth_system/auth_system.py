import RPi.GPIO as GPIO
import time
import subprocess
import time
from pyfingerprint.pyfingerprint import PyFingerprint

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
    subprocess.run(["lcd", "Place finger on sensor"])
    while f.readImage() == False:
        pass
    f.convertImage(0x01)
    result = f.searchTemplate()
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
    if f.compareCharacteristics() == 0:
        print("Fingers do not match")
        subprocess.run(["lcd", "Fingers do not match"])
        time.sleep(2)
        subprocess.run(["lcd", "0-reg; 1-delete; 2-search"])
        time.sleep(2)
        return
    f.createTemplate()
    positionNumber = f.storeTemplate()
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
        result = f.searchTemplate()
        positionNumber = result[0]
        accuracyScore = result[1]
        if positionNumber == -1:
            print("No match found!")
            subprocess.run(["lcd", "Finger print not verified"])
            time.sleep(2)
            subprocess.run(["lcd", "Aunthentication failed"])
            time.sleep(2)
            subprocess.run(["lcd", "0-reg; 1-delete; 2-search"])
            time.sleep(2)
            return
        else:
            print("Found template at position #" + str(positionNumber))
            subprocess.run(["lcd", "Finger print verified"])
            time.sleep(2)
            subprocess.run(["lcd", "Aunthentication success"])
            time.sleep(2)
            subprocess.run(["lcd", "0-reg; 1-delete; 2-search"])
            time.sleep(2)
    except Exception as e:
        print("Operation failed!")
        print("Exception message: " + str(e))
        exit(1)


# function handles the process of delete a fingerprint
def deleteFinger(pos):
    if f.deleteTemplate(pos) == True:
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
        if input == registration_key:
            enrollFinger()
        elif input == delete_key:
            subprocess.run(["lcd", "enter the position of fingerprint"])
            while True:
                pos = checkLine(L1, ["1", "2", "3"])
                pos = checkLine(L2, ["4", "5", "6"])
                pos = checkLine(L3, ["7", "8", "9"])
                pos = checkLine(L4, ["*", "0", "#"])
                if not pos == -1:
                    break; 
            deleteFinger(pos)
        elif input == search_key:
            searchFinger()
        elif input == secretCode:
            print("Code correct!")
            subprocess.run(["lcd", "Code correct!"])
            time.sleep(2)
            subprocess.run(["lcd", "Aunthentication success!!"])
            time.sleep(2)
            subprocess.run(["lcd", "0-reg; 1-delete; 2-search"])
            # c_lib.display_lcd("Code correct!")
            # TODO: Display a message on the LCD screen, possibly send the data to a server
        else:
            subprocess.run(["lcd", "Incorrect code!"])
            time.sleep(2)
            subprocess.run(["lcd", "Aunthentication failed!!"])
            time.sleep(2)
            print("Incorrect code!")
            subprocess.run(["lcd", "0-reg; 1-delete; 2-search"])
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

# Function which reads the input from the keypad.
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
