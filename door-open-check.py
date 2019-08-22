### door-open-check.py	- Andrew R Gross  2019-04-02
### Check if door is open

### Header
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

# Define starting states
door_is_open = False
prior_state = False
time_closed = datetime.datetime.now()
# Open log file in append mode
log_file = open('/home/pi/RFID/log-door.csv', 'a')

try:	### Loop continuously

	while True:

		### Check if the door is open
		if GPIO.input(doorswitch):	# If door is open, define door_is_open as True
			door_is_open = True
		else:				# if closed, define door_is_open as False
			door_is_open = False

		### Check if door status has changed
		if door_is_open == prior_state:	# If status hasn't changed, do nothing
			pass

		else: 				# If changed:
		        time = datetime.datetime.now()				# deefine time
			log_file = open('/home/pi/Desktop/RFID/log-door.csv', 'r')	# Open log file in append mode

			if door_is_open == True:				# If door just opened:
				print('Door Opened')
				time_opened = time				# Define current time as last time opened
				duration_closed = time_opened - time_closed	# Define duration since last opened
				duration_closed_string = str(duration_closed)[0:9]
		#		log_file.write(time.strftime('%Y-%m-%d %H:%M:%S') + ', Door Opened \n')
			else:							# If door just closed:
				print('Door Closed')
				time_closed = time
				duration_open = time_closed - time_opened
				duration_open_string = str(duration_open)[2:9]

				#log_file.write(time.strftime('%a %Y-%m-%d, %H:%M:%S, After') + duration_closed_string + ', Opened for: ' + duration_open_string + '\n')
				new_line = (time.strftime('%a %Y-%m-%d, %H:%M:%S, After ') + duration_closed_string + ', Opened for: ' + duration_open_string + '\n')
				contents = log_file.readlines()
				contents.insert(0, new_line)
				log_file.close()
				log_file = open('/home/pi/Desktop/RFID/log-door.csv', 'w')
				log_file.writelines(contents)
				log_file.close()

        #                log_file = open('/home/pi/Desktop/RFID/log-door.csv', 'r')
        #               log_file.write(time.strftime('%a %Y-%m-%d,%H:%M:%S') + ',' + ss + ',' + names_list[pos] + ',Approved \n')
        #                new_line = (time.strftime('%a %Y-%m-%d,%H:%M:%S') + ',' + ss + ',' + names_list[pos] + ',Approved \n')
        #                contents = log_file.readlines()
         #               contents.insert(0, new_line)
          #              log_file.close()
           #             log_file = open('/home/pi/Desktop/RFID/log-door.csv', 'w')
            #            log_file.writelines(contents)
             #           log_file.close()

		#		log_file.write(time.strftime('%Y-%m-%d %H:%M:%S') + ', Door Closed \n')
			os.system('rclone copy /home/pi/Desktop/RFID/log-door.csv door-log3:door-access')
		        print('Backup complete')

			prior_state = door_is_open
	#		log_file.close()

		sleep(0.1)

# When you press ctrl+c, this will be called
finally:
    GPIO.cleanup()
