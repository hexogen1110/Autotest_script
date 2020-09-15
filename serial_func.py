import serial #pyserial module
import time
#--------------
# Definition
#------------------------------------------------------------------------
serial_port = "COM81"
login_id = "root\r\n"
login_pwd = "!@AskeyRtl0100vw\r\n"

#----------------
# Base Function
#------------------------------------------------------------------------
def serial_login_device():
	com_port= serial.Serial(serial_port, baudrate = 115200,\
	timeout=0, bytesize = 8, parity = 'N', stopbits = 1)
	if com_port.isOpen():
		try:
			#print(com_port.name+" is opened")
			com_port.write(login_id)		
			time.sleep(1)				
			com_port.write(login_pwd)	
			time.sleep(1)
			ret = 0
		except:
			ret = 1
	com_port.close()
	return ret

def serial_write_command(command):
	com_port= serial.Serial(serial_port, baudrate = 115200,\
	timeout=0, bytesize = 8, parity = 'N', stopbits = 1)
	if com_port.isOpen():
		try:
			com_port.write(command)	
			ret = 0
		except:
			ret = 1
	com_port.close()
	return ret
	
#----------------
# Wrapper Function
#------------------------------------------------------------------------	
def serial_unlock_device(platform):
	try:
		ret = serial_login_device()
		if ret: return 1
		if platform == "rtl0108":
			serial_write_command("e2ptools -s UNLOCK -d 1 -m 0 -p rtl0108\r\n")
		else:
			serial_write_command("e2ptools -s UNLOCK -d 1 -m 0 -p rtl0300\r\n")
		serial_write_command("reboot\r\n")
	except:
		return 1
		
def serial_reboot_device():
	try:
		ret = serial_login_device()
		if ret: return 1
		serial_write_command("echo 1 > /sys/class/leds/led_3/brightness\r\n")
		serial_write_command("echo timer > /sys/class/leds/led_3/trigger\r\n")
		serial_write_command("echo 1 > /sys/class/leds/led_4/brightness\r\n")
		serial_write_command("echo timer > /sys/class/leds/led_4/trigger\r\n")	
		serial_write_command("reboot\r\n")
	except:
		return 1