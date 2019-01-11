import time
import threading
import datetime
import RPi.GPIO as GPIO
from Adafruit_LED_Backpack import SevenSegment
from Adafruit_LED_Backpack import BicolorBargraph24
import math

##=====================================================================
# class ledsMeter
#----------------------------------------------------------------------
# This class is  used for the vumeter module:
# as there are 2 modules, this code has multiple parameters:
# @param addressI2C: define the i2c address of the module
# @param valuePeak: define the maximal value for the consumption/production
# @param isInConsumption: define if the module is a consumption one.
# if it is, the color will be display as this: green for a small consumption,
# orange for an average consumption and red for a high consumption. The
# determination of the consumption value is define with a certain reference,
# that's set at the beginning with the valuePeak. It's up to you to define
# what is the maximal value, you just have to know that the number of led
# turned on will be a linear adaptation of the given value and the maximal
# one.
#----------------------------------------------------------------------
# It contains 4 methods:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# __init__(self, addressI2C, isInConsumption, valuePeak):
# It's quite logical
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# changeDisplay(self, newValue):
# it will adapt the number of led turned on by a comparison of the
# inner maximal value and the given newValue.
#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#  turnNbLed(self, toDisplay):
#  it will adapt the number of led turned on to the number of "toDisplay"
#  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#  calcNbLedOn(self, value):
#  it will adapt the number of led to turn on by a mathematical comparison
#  of the given value and an array of values that came from a premade
#  calculation of logarithmus of the consumption and production entities
##=====================================================================
class ledsMeter:

    def __init__(self, addressI2C, isInConsumption, valuePeak):
        self.maxValue = valuePeak
        self.display1 = 0
        self.nbLeds = 24
        self.oldToDisplay = 0
        self.maxDB = math.log10(valuePeak)
        self.stepDB = self.maxDB/30
        self.arrayPower = []

        for i in range(0, 25):
            self.arrayPower.append((int)((math.pow(10, self.maxDB - i * self.stepDB))) + 1)

        if(isInConsumption == True):
            self.consumption = True
        else:
            self.consumption = False

        self.i2cAddress = addressI2C
        ## Define the i2c address of the component "segment"
        self.display1 = BicolorBargraph24.BicolorBargraph24(address=self.i2cAddress)
        ## end of definition
        ## Define the begining of the communication and set the brightness
        self.display1.begin()
        self.display1.clear()
        self.display1.set_brightness(7)
        self.display1.write_display()

    def changeDisplay(self, newValue):

        if(newValue > self.maxValue):
            newValue = self.maxValue

        ratio = float(float(newValue)/float(self.maxValue))
        toDisplay = int(self.nbLeds*ratio)

        if(self.oldToDisplay != toDisplay):
            self.oldToDisplay = toDisplay

            self.display1.clear()
            self.display1.write_display()

            if(self.consumption == False):
                for i in range(0,toDisplay+1):
                    invert = self.nbLeds-i-1
                    if(invert>18):
                        self.display1.set_bar(invert,BicolorBargraph24.YELLOW)
                    else:
                        if (invert > 10):
                            self.display1.set_bar(invert, BicolorBargraph24.YELLOW)

                        else:
                            if(invert >= 0):
                                self.display1.set_bar(invert, BicolorBargraph24.GREEN)
                    self.display1.write_display()
            else:
                for i in range(0, toDisplay + 1):
                    invert = self.nbLeds - i - 1
                    if (invert > 18):
                        self.display1.set_bar(invert, BicolorBargraph24.GREEN)
                    else:
                        if (invert > 10):
                            self.display1.set_bar(invert, BicolorBargraph24.YELLOW)

                        else:
                            if (invert >= 0):
                                self.display1.set_bar(invert, BicolorBargraph24.YELLOW)
                    self.display1.write_display()

    def turnNbLed(self, toDisplay):

        if(toDisplay > self.nbLeds):
            toDisplay = self.nbLeds


        if(self.oldToDisplay != toDisplay):
            self.oldToDisplay = toDisplay

            self.display1.clear()
            self.display1.write_display()

            if(self.consumption == False):
                for i in range(0,toDisplay+1):
                    invert = self.nbLeds-i-1
                    if(invert>18):
                        self.display1.set_bar(invert,BicolorBargraph24.YELLOW)
                    else:
                        if (invert > 10):
                            self.display1.set_bar(invert, BicolorBargraph24.YELLOW)

                        else:
                            if(invert >= 0):
                                self.display1.set_bar(invert, BicolorBargraph24.GREEN)
                    self.display1.write_display()
            else:
                for i in range(0, toDisplay + 1):
                    invert = self.nbLeds - i - 1
                    if (invert > 18):
                        self.display1.set_bar(invert, BicolorBargraph24.GREEN)
                    else:
                        if (invert > 10):
                            self.display1.set_bar(invert, BicolorBargraph24.YELLOW)

                        else:
                            if (invert >= 0):
                                self.display1.set_bar(invert, BicolorBargraph24.YELLOW)
                    self.display1.write_display()

    def calcNbLedOn(self, value):

        for i in self.arrayPower:
            if(value > i):
                self.turnNbLed(self.nbLeds - self.arrayPower.index(i) - 1)
                break
            if(self.arrayPower.index(i) == 24):
                self.turnNbLed(-1)
                break




##=====================================================================
# class servoMotor
#----------------------------------------------------------------------
# This class is  used for the servomotor (Tower Pro MG90S):
# It will change the angle of the oscillated platform.
#----------------------------------------------------------------------
# It contains 4 methods:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# __init__(self):
# define the pin as a PWM output with the good frequency and duty-cycle of 0.5
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# changeMaxDelta(self, newMaxDelta):
# It will adapt the maxDelta if it is in the range of the capability of the
# servomotor. WARNING! this is a delta between the 0 degrees and the maximal Value!
# Be aware that it isn't a delta between the minimal and maximal angle wanted!

#                   *      *
#               *               *
#            *                      *
#          *                          *                //=0     ----*
#        *                              *   //=======//                 *
#       *                        //=======//                               *  IT'S THE MAX DELTA
#      *                    /==//         *                                  *
#      *                 O====================================0       -------*
#      *                                  *
#       *                                *
#        *                              *
#          *                          *
#            *                      *
#               *               *
#                    *     *
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# changeAngle(self, newAngle):
# It will test if the new angle wanted is in the tolerance of the delta angle.
# If not, it will adapt to the biggest/lowest angle possible.
# Then, the angle will change only if the new angle has a biggest difference
# with the old one than the given tolerance, set at 0.2 degrees.
# If it is smaller than it, it will be the end of the method, elsewhere it
# it would call the adaptAngle method, described below:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# adaptAngle(self, angle):
# It will change the duty-cycle of the PWM with a calculation for the
# servomotor used. when the duty-cycle has been sent and the angle has
# been changed, the duty-cycle is set to 0, to avoid the correction of
# the servomotor, as it is very sensitive for the duty-cycle and the raspberry
# isn't really reliable.
##=====================================================================
class servoMotor:
    maxAngle = 180  # of the servomotor
    minAngle = 0  # of the servomotor
    maxDuty = 11.8  # of the servomotor
    minDuty = 2.4  # of the servomotor
    oldAngle = 10  # to do a comparison of the old and new value
    tolerance = 0.2  # angle tolerance


    def __init__(self):
        self.maxDelta = 20
        self.oldDuty = float(0 + (self.maxAngle - self.minAngle) / 2) / float(self.maxAngle)
        self.oldDuty = self.oldDuty * float(self.maxDuty - self.minDuty) * 0.9
        self.oldDuty = self.oldDuty + self.minDuty
        # Define the pin GPIO26 as a PWM output
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(18, GPIO.OUT)
        self.servoPin = GPIO.PWM(18, 50)
        self.servoPin.start(float(self.maxDuty+self.minDuty)/float(2))
        self.adaptAngle(0)

    def changeMaxDelta(self, newMaxDelta):
        # test if in acceptable delta angle
        if(newMaxDelta<((self.maxAngle+self.minAngle)/2)):
            self.maxDelta = newMaxDelta
            print(self.maxDelta)

    def changeAngle(self, newAngle):
        # test if acceptable
        if(newAngle>self.maxDelta):
            newAngle = 20

        if (newAngle < (-(self.maxDelta))):
            newAngle = -20

        # now do a rule for the command
        maxTolered = self.oldAngle+self.tolerance
        minTolered = self.oldAngle-self.tolerance

        if (newAngle > maxTolered or newAngle < minTolered):
            self.adaptAngle(newAngle)
            self.oldAngle = newAngle

    def adaptAngle(self, angle):

        tempAngle = self.oldAngle

        while(tempAngle<(angle-0.05) or tempAngle>(angle+0.05)):
            tempAngle = tempAngle + float((angle-tempAngle)/3)
            print(tempAngle)

            newDuty = float(tempAngle+(self.maxAngle-self.minAngle)/2)/float(self.maxAngle)
            newDuty = newDuty*float(self.maxDuty-self.minDuty)*0.9
            newDuty = newDuty+self.minDuty
            # say to the servo to change this angle
            self.servoPin.ChangeDutyCycle(newDuty)
            # let the time to itself to change it
            time.sleep(0.15)

        # say to the servo to stop all moves
        self.servoPin.ChangeDutyCycle(0)
        print("Angle changed")


##=====================================================================
# class sevenSegmentDigit
#----------------------------------------------------------------------
# This class is  used for the seven segment 4 digits module:
# it can do multiple things, described below.
#----------------------------------------------------------------------
# It contains 6 methods:
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# __init__(self):
# Define the basic parameters of the display, such as the i2c address or
# the brightness of itself.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# displayColon(self):
# set the colon without removing what's displayed.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# displayString(self, toDisplay):
# It will display the given STRING. Doing this will clear the display and
# then show the string.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# displayClear(self):
# As it's written, it clears the display.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# startThreadTime(self):
# DO NOT USE THIS, still in development, it should start a thread the will
# display the time, but it doesn't work actually.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# displayTime(self):
# It displays the real time.
##=====================================================================
class sevenSegmentDigit:
    segment = 0
    isThread = False
    thr = 0

    def __init__(self):
        self.segment = SevenSegment.SevenSegment(address=0x70)
        self.segment.begin()
        self.segment.set_brightness(7)
        self.segment.clear()
        self.segment.write_display()
        self.isThread = False
        #thr = threading.Thread(name='adaptTime', target=self.adaptTime())

    def displayColon(self):
        self.segment.set_colon(1)
        self.segment.write_display()

    def displayString(self, toDisplay):
        self.segment.clear()
        self.segment.print_number_str(toDisplay)
        self.segment.write_display()

    def displayClear(self):
        self.segment.clear()
        self.segment.write_display()

    def displayTime(self):

        now = datetime.datetime.now()
        hour = now.hour
        minute = now.minute
        second = now.second

        self.segment.clear()
        # Set hours
        self.segment.set_digit(0, int(hour / 10))     # Tens
        self.segment.set_digit(1, hour % 10)          # Ones
        # Set minutes
        self.segment.set_digit(2, int(minute / 10))   # Tens
        self.segment.set_digit(3, minute % 10)        # Ones
        # Toggle colon
        self.segment.set_colon(second % 2)              # Toggle colon at 1Hz

        # Write the display buffer to the hardware.  This must be called to
        # update the actual display LEDs.
        self.segment.write_display()