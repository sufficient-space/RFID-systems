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
import pigpio
from RPLCD.pigpio import CharLCD

led = LED(17)

pi = pigpio.pi()
lcd = CharLCD(pi,pin_rs=15, pin_rw=18, pin_e=16, pins_data=[21, 22, 23, 24],cols=20, rows=4, dotsize=8,charmap='A02',auto_linebreaks=True)


### Import whitelist

with open('/home/pi/RFID/keyed-members') as whitelist:
	csv_reader = csv.reader(whitelist, delimiter=',')
	line_count = 0
	ID_list = []
	names_list = []
	nicknames_list = []
	member_type = []
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
		member_type.append(member_type)
	print(ID_list)


whitelist = ''

### Parse RFID input

hid = { 4: 'a', 5: 'b', 6: 'c', 7: 'd', 8: 'e', 9: 'f', 10: 'g', 11: 'h', 12: 'i', 13: 'j', 14: 'k', 15: 'l', 16: 'm', 17: 'n', 18: 'o', 19: 'p', 20: 'q', 21: 'r', 22: 's', 23: 't', 24: 'u', 25: 'v', 26: 'w', 27: 'x', 28: 'y', 29: 'z', 30: '1', 31: '2', 32: '3', 33: '4', 34: '5', 35: '6', 36: '7', 37: '8', 38: '9', 39: '0', 44: ' ', 45: '-', 46: '=', 47: '[', 48: ']', 49: '\\', 51: ';' , 52: '\'', 53: '~', 54: ',', 55: '.', 56: '/'  }
hid2 = { 4: 'A', 5: 'B', 6: 'C', 7: 'D', 8: 'E', 9: 'F', 10: 'G', 11: 'H', 12: 'I', 13: 'J', 14: 'K', 15: 'L', 16: 'M', 17: 'N', 18: 'O', 19: 'P', 20: 'Q', 21: 'R', 22: 'S', 23: 'T', 24: 'U', 25: 'V', 26: 'W', 27: 'X', 28: 'Y', 29: 'Z', 30: '!', 31: '@', 32: '#', 33: '$', 34: '%', 35: '^', 36: '&', 37: '*', 38: '(', 39: ')', 44: ' ', 45: '_', 46: '+', 47: '{', 48: '}', 49: '|', 51: ':' , 52: '"', 53: '~', 54: '<', 55: '>', 56: '?'  }
fp = open('/dev/hidraw0', 'rb')
ss = ""
shift = False
done = False
while True:
	while not done:			## Get the character from the HID
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
						ss += hid2[ int(ord(c)) ]
						shift = False
				else:		# if not shifted, use the hid characters
					if int(ord(c)) == 2 :	# if 2, then it is the shift key
						shift = True
					else:	# If not a 2, lookup mapping
						ss += hid[ int(ord(c)) ]

	### When an RFID is detected:
	print ss				# Print it
	time = datetime.datetime.now()		# Define the current time

	### Check whitelist
	if ID_list.count(ss) > 0:		# If the ID appears on the white list:

		### Check the membership type
		pos = ID_list.index(ss)
		if member_type[pos] == 'keyed_membership':	# If keyed, open

			print('Welcome ' + nicknames_list[pos])
	#		lcd.write_string('Access Granted')
			led.on()
			sleep(2)
			led.off()

			log_file = open('/home/pi/RFID/log-door.csv', 'a')
			log_file.write(time.strftime('%Y-%m-%d %H:%M%S') + ',' + ss ++ ',' + names_list[pos] + ',Approved \n')
			log_file.close()

		if member_type[pos] == 'standard_membership':	# If standard, check the time

			if time_open < time < time_close:	# If within open hours, open

				print('Welcome ' + nicknames_list[pos])
	#			lcd.write_string('Access Granted')
				led.on()
				sleep(2)
				led.off()

			else:					# If outside open hours, output to LCD
				print('Please return during open hours')
	#			lcd.write_string('Return after 4')
				log_file = open('/home/pi/RFID/log-door.csv','a')
				log_file.write(time.strftime('%Y-%m-%d %H:%M:%S') + ',' + ss + ',' + names_list[pos] + ',Wrong time \n')
				log_file.close()

	### If the user isn't found:
	if ID_list.count(ss) == 0:
		print('User not found.  Access Denied')
		#lcd.write_string('Access DENIED')
		log_file = open('/home/pi/RFID/log-door.csv', 'a')
		log_file.write(time.strftime('%Y-%m-%d %H:%M:%S') + ',' + ss + ', Unknown (ACCESS DENIED) \n')
		log_file.close()

	### After completing checks, backup the new log file
	os.system('rclone copy /home/pi/RFID/log-door.csv door-log3:door-access')
	print('Backup complete')

	ss = ''
	done = False
