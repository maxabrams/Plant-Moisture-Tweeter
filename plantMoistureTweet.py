#!/usr/bin/env python
# Maxwell Abrams 2019
#-----------------------------------------------------
#
#		ADC Pin Diagram
#		ADC code comes from: https://github.com/sunfounder/Sunfounder_SensorKit_Python_code_for_RaspberryPi
#
#		  ACD1302				  Pi
#			CS ---------------- Pin 11
#			CLK --------------- Pin 12
#			DI ---------------- Pin 13
#			VCC ----------------- 3.3V (Or 5V)
#			GND ------------------ GND
#
#-----------------------------------------------------
from twython import Twython
import RPi.GPIO as GPIO
import time

SIX_HOURS_IN_SECONDS = 21600

# ADC Physical Pins
ADC_CS  = 11
ADC_CLK = 12
ADC_DIO = 13

# Twitter API keys - you need to add this!!
CONSUMER_KEY = ""
CONSUMER_SECRET = ""
ACCESS_TOKEN = ""
ACCESS_TOKEN_SECRET = ""

twitterConnection = Twython(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

# Using default pins for backwards compatibility
def setupADC(cs=11, clk=12, dio=13):
        global ADC_CS, ADC_CLK, ADC_DIO
        ADC_CS=cs
        ADC_CLK=clk
        ADC_DIO=dio
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)    		# Number GPIOs by its physical location
	GPIO.setup(ADC_CS, GPIO.OUT)		# Set pins' mode is output
	GPIO.setup(ADC_CLK, GPIO.OUT)		# Set pins' mode is output

def destroy():
	GPIO.cleanup()

# Get ADC result
def readSensor(channel=0):     				
		GPIO.setup(ADC_DIO, GPIO.OUT)
		GPIO.output(ADC_CS, 0)
		
		GPIO.output(ADC_CLK, 0)
		GPIO.output(ADC_DIO, 1);  time.sleep(0.000002)
		GPIO.output(ADC_CLK, 1);  time.sleep(0.000002)
		GPIO.output(ADC_CLK, 0)
	
		GPIO.output(ADC_DIO, 1);  time.sleep(0.000002)
		GPIO.output(ADC_CLK, 1);  time.sleep(0.000002)
		GPIO.output(ADC_CLK, 0)
	
		GPIO.output(ADC_DIO, channel);  time.sleep(0.000002)
	
		GPIO.output(ADC_CLK, 1)
		GPIO.output(ADC_DIO, 1);  time.sleep(0.000002)
		GPIO.output(ADC_CLK, 0)
		GPIO.output(ADC_DIO, 1);  time.sleep(0.000002)
	
		dat1 = 0
		for i in range(0, 8):
			GPIO.output(ADC_CLK, 1);  time.sleep(0.000002)
			GPIO.output(ADC_CLK, 0);  time.sleep(0.000002)
			GPIO.setup(ADC_DIO, GPIO.IN)
			dat1 = dat1 << 1 | GPIO.input(ADC_DIO)  
		
		dat2 = 0
		for i in range(0, 8):
			dat2 = dat2 | GPIO.input(ADC_DIO) << i
			GPIO.output(ADC_CLK, 1);  time.sleep(0.000002)
			GPIO.output(ADC_CLK, 0);  time.sleep(0.000002)
		
		GPIO.output(ADC_CS, 1)
		GPIO.setup(ADC_DIO, GPIO.OUT)

		if dat1 == dat2:
			return dat1
		else:
			return 0

# From playing with the sensor, ~70 is pure water and ~142 is 100% dry
def makeTweet(moistureLevel):
    tweet = ""
    if moistureLevel < 10:
        return tweet
    elif moistureLevel < 80:
        tweet += "The plant is pretty wet! Hold off on watering."
    elif moistureLevel < 115:
        tweet += "Moisture looks okay today! No need to water."
    elif moistureLevel < 125:
        tweet += "The plant is starting to get dry. Water soon!"
    elif moistureLevel < 130:
	    tweet += "Time to water!"
    else:
        tweet += "Hey! The plant really needs some water!!"
	
	tweet += " (" + str(moistureLevel) + ")"
	return tweet

def mainLoop():
	while True:
		moistureLevel = readSensor(0)
		print 'Water moisture = %d' % (moistureLevel)

		statusMsg =  makeTweet(moistureLevel)
		print statusMsg
		if statusMsg != "":
			try:
				print "Sending tweet..."
				twitterConnection.update_status(status=statusMsg)
				print "Tweet sent!"
			except Exception as e:
				print "Failed to tweet: " + str(e)
		
		time.sleep(SIX_HOURS_IN_SECONDS)

if __name__ == '__main__':	# Program start from here
	setupADC()
	try:
		mainLoop()
	except KeyboardInterrupt:  	# When 'Ctrl+C' is pressed, execute destroy()
		destroy()