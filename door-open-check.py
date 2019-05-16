### Check if door is open

from time import sleep
import RPi.GPIO as GPIO
import csv
import datetime
import sys
import os

# Pin definition
doorswitch = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(doorswitch, GPIO.IN)

door_is_open = False
prior_state = False

log_file = open('/home/pi/RFID/log-door.csv', 'a')

try:
	while True:
		if GPIO.input(doorswitch):
			door_is_open = True
		#	print('door switch is open!')
		else:
			door_is_open = False
		#	print('door switch is closed')

		if door_is_open == prior_state:
			pass
		else: 
		        time = datetime.datetime.now()
			log_file = open('/home/pi/RFID/log-door.csv', 'a')

			if door_is_open == True:
				print('Door Opened')
	        	        log_file.write(time.strftime('%Y-%m-%d %H:%M:%S') + ', Door Opened \n')
			else:
				print('Door Closed')
				log_file.write(time.strftime('%Y-%m-%d %H:%M:%S') + ', Door Closed \n')
			os.system('rclone copy /home/pi/RFID/log-door.csv door-log3:door-access')
		        print('Backup complete')

			prior_state = door_is_open
			log_file.close()

		sleep(0.1)

# When you press ctrl+c, this will be called
finally:
    GPIO.cleanup()
