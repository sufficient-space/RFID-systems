### door-access.py -- Andrew R Gross -- 2019-03-13
### This program continuously checks an RFID reader for the correct ID, then 
### checks IDs against a whitelist

### Header
import sys
import csv
import datetime
import os
import subprocess
from gpiozero import LED
from time import sleep
from RPLCD.gpio import CharLCD
from RPi import GPIO

# Define GPIO Pins
door_lock = LED(17)
blue_backlight = LED(27)
green_backlight = LED(22)
red_backlight = LED(23)

# Define LCD
print("define LCD")
GPIO.setwarnings(False)
lcd = CharLCD(cols=16, rows=2, pin_rs=26, pin_rw=24, pin_e=19, pins_data=[13, 6, 5, 11],numbering_mode=GPIO.BCM)
#lcd = CharLCD(cols=16, rows=2, pin_rs=37, pin_rw=18, pin_e=35, pins_data=[33, 31, 29, 23], numbering_mode=GPIO.BOARD)
print('lcd defined')

### Declare functions

def backlight_blink_green(duration,loop_counter):
    while loop_counter > 0:
        blue_backlight.off()
        sleep(duration)
        green_backlight.on()
        sleep(duration)
        green_backlight.off()
        sleep(duration)
        blue_backlight.on()
        sleep(duration)
	loop_counter = loop_counter - 1

def access_granted():
	print('Welcome ' + nicknames_list[pos] + '. Member type: ' + member_type_list[pos])
	blue_backlight.off()
	green_backlight.on()
	lcd.clear()
	lcd.write_string('Access Granted')
	lcd.cursor_pos = (1,0)
	lcd.write_string(nicknames_list[pos])
	door_lock.on()
	sleep(2)
	door_lock.off()
	lcd.clear()
	green_backlight.off();blue_backlight.on()

	log_file = open('/home/pi/Desktop/RFID/log-door.csv', 'a')
	log_file.write(time.strftime('%a %Y-%m-%d,%H:%M:%S') + ',' + rfid_number + ',' + names_list[pos] + ',Approved \n')
	log_file.close()  

def access_denied():        #The tab size in Spyder appears different than nano
    print('User not found.  Access Denied')
    #lcd.write_string('Access DENIED')
    log_file = open('/home/pi/Desktop/RFID/log-door.csv', 'a')
    log_file.write(time.strftime('%a %Y-%m-%d,%H:%M:%S') + ',' + rfid_number + ', Unknown (ACCESS DENIED) \n')
    log_file.close()

### Import whitelist

with open('/home/pi/Desktop/RFID/members_list') as whitelist:
	csv_reader = csv.reader(whitelist, delimiter=',')
	line_count = 0
	ID_list = []
	names_list = []
	nicknames_list = []
	member_type_list = []
	for row in csv_reader:
		ID = row[0]
		first_name = row[2]
		last_name = row[1]
		nickname = row[3]
		member_type = row[4]
		full_name = first_name+' '+last_name
		ID_list.append(ID)
		names_list.append(full_name)
		nicknames_list.append(nickname)
		member_type_list.append(member_type)
	print(ID_list)


#whitelist = ''    # I think I can get rid of this, but test first

### Parse RFID input
hid = { 4: 'a', 5: 'b', 6: 'c', 7: 'd', 8: 'e', 9: 'f', 10: 'g', 11: 'h', 12: 'i', 13: 'j', 14: 'k', 15: 'l', 16: 'm', 17: 'n', 18: 'o', 19: 'p', 20: 'q', 21: 'r', 22: 's', 23: 't', 24: 'u', 25: 'v', 26: 'w', 27: 'x', 28: 'y', 29: 'z', 30: '1', 31: '2', 32: '3', 33: '4', 34: '5', 35: '6', 36: '7', 37: '8', 38: '9', 39: '0', 44: ' ', 45: '-', 46: '=', 47: '[', 48: ']', 49: '\\', 51: ';' , 52: '\'', 53: '~', 54: ',', 55: '.', 56: '/'  }
hid2 = { 4: 'A', 5: 'B', 6: 'C', 7: 'D', 8: 'E', 9: 'F', 10: 'G', 11: 'H', 12: 'I', 13: 'J', 14: 'K', 15: 'L', 16: 'M', 17: 'N', 18: 'O', 19: 'P', 20: 'Q', 21: 'R', 22: 'S', 23: 'T', 24: 'U', 25: 'V', 26: 'W', 27: 'X', 28: 'Y', 29: 'Z', 30: '!', 31: '@', 32: '#', 33: '$', 34: '%', 35: '^', 36: '&', 37: '*', 38: '(', 39: ')', 44: ' ', 45: '_', 46: '+', 47: '{', 48: '}', 49: '|', 51: ':' , 52: '"', 53: '~', 54: '<', 55: '>', 56: '?'  }
fp = open('/dev/hidraw0', 'rb')
rfid_number = ""
shift = False
done = False

### Begin run loop
while True:
	### Wait for RFID
	while not done:			## Get the character from the HID
		blue_backlight.on()	## Turn on the blue backlight
		lcd.cursor_pos = (0,3)	## Set cursor pos on first line
		lcd.write_string('Swipe Badge')
  
		buffer = fp.read(8)
		for c in buffer:
			if ord(c) > 0:	##  40 is carriage return which signifies we are done looking for characters
				if int(ord(c)) == 40:
					done = True
					break;	##  If we are shifted then we have to  use the hid2 characters.
				if shift: 	## If it is a '2' then it is the shift key
					if int(ord(c)) == 2 :
						shift = True
					else:	# if not a 2, lookup mapping
						rfid_number += hid2[ int(ord(c)) ]
						shift = False
				else:		# if not shifted, use the hid characters
					if int(ord(c)) == 2 :	# if 2, then it is the shift key
						shift = True
					else:	# If not a 2, lookup mapping
						rfid_number += hid[ int(ord(c)) ]

	### When an RFID is detected:
	print rfid_number		## Print it
	time = datetime.datetime.now()	## Define the current time

	### Check whitelist
	if ID_list.count(rfid_number) > 0: # If the ID appears on the white list:

		### Check the membership type
		pos = ID_list.index(rfid_number)		# Define lin in member list
		if member_type_list[pos] == 'keyed_membership':	# If keyed: open

			## Open and print ID function here:
			#open(nickname)
			print('Welcome ' + nicknames_list[pos])
			backlight_blink_green(0.08,2)		# Blink green twice for 0.08 s
			blue_backlight.off()
			green_backlight.on()
			# Print output to LCD function goes here
			lcd.clear()
			lcd.write_string('Access Granted')
			lcd.cursor_pos = (1,0)
			lcd.write_string(nicknames_list[pos])
			# Door unlock function goes here
			#unlockDoor(2)
			door_lock.on()
			sleep(2)
			door_lock.off()
			lcd.clear()
			green_backlight.off();blue_backlight.on()
			# Log event function

                        log_file = open('/home/pi/Desktop/RFID/log-door.csv', 'r')
                        new_line = (time.strftime('%a %Y-%m-%d,%H:%M:%S') + ',' + rfid_number + ',' + names_list[pos] + ',Approved \n')
                        contents = log_file.readlines()
                        contents.insert(0, new_line)
                        log_file.close()
                        log_file = open('/home/pi/Desktop/RFID/log-door.csv', 'w')
                        log_file.writelines(contents)
                        log_file.close()

	#		log_file = open('/home/pi/Desktop/RFID/log-door.csv', 'a')
	#		log_file.write(time.strftime('%a %Y-%m-%d,%H:%M:%S') + ',' + rfid_number + ',' + names_list[pos] + ',Approved \n')
	#		log_file.close()

		if member_type_list[pos] == 'standard_membership': # If standard: check the time

			if time_open < time < time_close:	# If within open hours, open

				print('Welcome ' + nicknames_list[pos])
				# Door open function goes here
	#			lcd.write_string('Access Granted')
				door_lock.on()
				sleep(3)
				door_lock.off()

			else:					# If outside open hours, output to LCD
				print('Please return during open hours')
	#			lcd.write_string('Return after 4')
				door_lock.on()
				sleep(2)
				door_lock.off()

				log_file = open('/home/pi/RFID/log-door.csv','a')
				log_file.write(time.strftime('%a %Y-%m-%d,%H:%M:%S') + ',' + rfid_number + ',' + names_list[pos] + ',Wrong time \n')
				log_file.close()

	#	else:
	#		print('Error detecting membership type')

	### If the user isn't found:
	if ID_list.count(rfid_number) == 0:
		print('User not found.  Access Denied')
		#lcd.write_string('Access DENIED')
		log_file = open('/home/pi/Desktop/RFID/log-door.csv', 'a')
		log_file.write(time.strftime('%a %Y-%m-%d,%H:%M:%S') + ',' + rfid_number + ', Unknown (ACCESS DENIED) \n')
		log_file.close()

	### After completing checks, backup the new log file
	os.system('rclone copy /home/pi/Desktop/RFID/log-door.csv door-log3:door-access')
	print('Backup complete')

	rfid_number = ''
	done = False
