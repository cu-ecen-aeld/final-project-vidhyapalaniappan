##********************************************************************************************************************************************************
## File name        : fingerprint.py
## ​Description      : A basic numpad code to test the functionality of numpad
## File​ ​Author​ ​Name : Vidhya. PL & Ashwin Ravindra
## Date             : 12/03/2023
## Credits          : https://core-electronics.com.au/guides/fingerprint-scanner-raspberry-pi/
## **********************************************************************************************************************************************************


##Including necessary header files##
import time

from pyfingerprint.pyfingerprint import PyFingerprint

# import RPi.GPIO as gpio

#
try:
#initializes the sensor with specific parameters such as the device path, baud rate, and passwords
    f = PyFingerprint("/dev/ttyUSB0", 57600, 0xFFFFFFFF, 0x00000000)
# checks if the password verification for the fingerprint sensor fails
    if f.verifyPassword() == False:

        raise ValueError("The given fingerprint sensor password is wrong!")

#If an exception is raised, it will be caught
except Exception as e:

    print("Our Exception message: " + str(e))
    exit(1)

# function handles the process of enrolling a fingerprint
def enrollFinger():
    time.sleep(2)
    print("Waiting for finger...")
    while f.readImage() == False:
        pass
    f.convertImage(0x01)
    result = f.searchTemplate()    #searching if the fingerprint is already enrolled
    positionNumber = result[0]
    if positionNumber >= 0:
        print("Template already exists at position #" + str(positionNumber))
        time.sleep(2)
        return
    print("Remove finger...")
    time.sleep(2)
    print("Waiting for same finger again...")
    while f.readImage() == False:  #checking if the fingerprints match for enrolling
        pass
    f.convertImage(0x02)
    if f.compareCharacteristics() == 0:
        print("Fingers do not match")
        time.sleep(2)
        return
    f.createTemplate()
    positionNumber = f.storeTemplate()  #storing the fingerprint data in the database
    print("Finger enrolled successfully!")
    print("New template position #" + str(positionNumber))
    time.sleep(2)

# function handles the process of searching for a fingerprint
def searchFinger():
    try:
        print("Waiting for finger...")
        while f.readImage() == False:
            # pass
            time.sleep(0.5)
            return
        f.convertImage(0x01)
        result = f.searchTemplate()  #searching if the fingerprint exists
        positionNumber = result[0]
        accuracyScore = result[1]
        if positionNumber == -1:
            print("No match found!")
            time.sleep(2)
            return
        else:
            print("Found template at position #" + str(positionNumber))
            time.sleep(2)
    except Exception as e:
        print("Operation failed!")
        print("Exception message: " + str(e))
        exit(1)
        
# function handles the process of delete a fingerprint
def deleteFinger(pos):
    if f.deleteTemplate(pos) == True:   #delete the fingerprint data stored at position pos
        print("Template deleted!")
        time.sleep(2)


while 1:

#printing the menu options
    print("e) enroll print")
    print("s) find print")
    print("d) delete print")
    print("q) quit")
    print("----------------")
   
    c = input("> ")
    if c == "e":
        enrollFinger()

    if c == "s":
        searchFinger()

    if c == "d":
        print("enter the position of fingerprin")
        pos = input("> ")
        deleteFinger(pos)

    if c == "q":
        print("Exiting fingerprint example program")
        raise SystemExit

