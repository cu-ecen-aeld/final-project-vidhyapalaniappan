import time
from pyfingerprint.pyfingerprint import PyFingerprint
#import RPi.GPIO as gpio

try:
    f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
    if ( f.verifyPassword() == False ):
        raise ValueError('The given fingerprint sensor password is wrong!')

except Exception as e:
    print('Exception message: ' + str(e))
    exit(1)

def enrollFinger():
    time.sleep(2)
    print('Waiting for finger...')
    while ( f.readImage() == False ):
        pass
    f.convertImage(0x01)
    result = f.searchTemplate()
    positionNumber = result[0]
    if ( positionNumber >= 0 ):
        print('Template already exists at position #' + str(positionNumber))
        time.sleep(2)
        return
    print('Remove finger...')
    time.sleep(2)
    print('Waiting for same finger again...')

    while ( f.readImage() == False ):
        pass
    f.convertImage(0x02)
    if ( f.compareCharacteristics() == 0 ):
        print ("Fingers do not match")
        time.sleep(2)
        return

    f.createTemplate()
    positionNumber = f.storeTemplate()
    print('Finger enrolled successfully!')
    print('New template position #' + str(positionNumber))
    time.sleep(2)

def searchFinger():
    try:
        print('Waiting for finger...')
        while( f.readImage() == False ):
            #pass
            time.sleep(.5)
            return
        f.convertImage(0x01)
        result = f.searchTemplate()
        positionNumber = result[0]
        accuracyScore = result[1]
        if positionNumber == -1 :
            print('No match found!')
            time.sleep(2)
            return
        else:
            print('Found template at position #' + str(positionNumber))
            time.sleep(2)

    except Exception as e:
        print('Operation failed!')
        print('Exception message: ' + str(e))
        exit(1)
 
def deleteFinger(pos):
    if f.deleteTemplate(pos) == True :
        print('Template deleted!')
        time.sleep(2)

while 1:
    print("e) enroll print")
    print("s) find print")
    print("d) delete print")
    print("q) quit")
    print("----------------")s
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

