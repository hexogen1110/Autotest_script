import configparser
import subprocess
import os
import time
import serial #pyserial module
from ppadb.client import Client as AdbClient #refer: https://pypi.org/project/pure-python-adb/
import paramiko #python ssh module

#--------------
# Definition
#------------------------------------------------------------------------
adb_hostname = "192.168.1.1"
client = AdbClient(host="127.0.0.1", port=5037)
pingstatus = False
reboot_delay_sec = 60
serial_port = "COM81"

# Define status tuple
status_tuple= (\
["ipa_hdr.txt", "cat /sys/kernel/debug/ipa/hdr;dmesg | grep name:"],\
["ipacm_time.txt", "dmesg | grep ipacm"],\
["ip_ne.txt", "ip ne"])

# Object for config
class conf: 
    def __init__(self): 
        self.reboot_method = ""
        self.default_unlock = 0   

#----------------
# Sub Function
#------------------------------------------------------------------------
def get_config():
	config = configparser.ConfigParser()
	config.read('Config.ini')
	conf.reboot_method = config.get('Reboot method', 'reboot_method')
	conf.default_unlock = config.get('Misc', 'Default_unlock_device')
	
def clean_log():
	for ls in status_tuple:
		if os.path.exists(ls[0]):
			os.remove(ls[0])

def serial_unlock_device():
	com_port= serial.Serial(serial_port, baudrate = 115200,\
	timeout=0, bytesize = 8, parity = 'N', stopbits = 1)
	if com_port.isOpen():
		try:
			print(com_port.name+" is opened")
			com_port.write("root\r\n")
			time.sleep(1)
			com_port.write("!@AskeyRtl0100vw\r\n")
			time.sleep(1)
			com_port.write("e2ptools -s UNLOCK -d 1 -m 0 -p rtl0108\r\n")
			com_port.write("sync\r\n")
			com_port.write("reboot\r\n")
			print("unlock_device success and reboot now")			
			ret = 0
		except:
			ret = 1
	com_port.close()
	return ret

def ping_device():
	err_count = 0
	print("Ping device...")	
	while err_count < 9:
		ping_command = "ping -n 2 " + adb_hostname
		(output, error) = subprocess.Popen(ping_command,
										stdout=subprocess.PIPE,
										stderr=subprocess.PIPE,
										shell=True).communicate()
		if "TTL" in output:
			print("ping available!")
			return 1
		else:
			print("ping not available!")
			err_count = err_count + 1
		time.sleep(5)
	#failed to ping
	return 0

def get_device_status(i):
	print("--->Get device status")
	device = client.device("192.168.1.1:5555")
	
	for ls in status_tuple:
		print ("--->"+ls[0])
		out = device.shell(ls[1])
		f = open(ls[0], 'a')
		buf = "iteration:" + str(i) + "\n"
		f.write(buf)
		f.write(out)
		f.close()

def reboot_device(type):
	err_count = 0
	while True:
		if type == "serial":
			print("---->Reboot device by serial port")
			try:
				com_port= serial.Serial('COM81', baudrate = 115200,\
				timeout=0, bytesize = 8, parity = 'N', stopbits = 1)
				if com_port.isOpen():
					print(com_port.name+" is opened")
					com_port.write("root\r\n")
					time.sleep(1)
					com_port.write("!@AskeyRtl0100vw\r\n")
					time.sleep(1)
					# Light LED to notify user
					com_port.write("echo 1 > /sys/class/leds/led_3/brightness\r\n")
					com_port.write("echo timer > /sys/class/leds/led_3/trigger\r\n")
					com_port.write("echo 1 > /sys/class/leds/led_4/brightness\r\n")
					com_port.write("echo timer > /sys/class/leds/led_4/trigger\r\n")	
					com_port.write("reboot\r\n")				
				com_port.close()
				return 0
			except:
				print("COM port fail to open!")
				err_count += 1
		elif type == "ssh":
			print("---->Reboot device by SSH")
			try:
				ssh = paramiko.SSHClient()
				ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
				ssh.connect(hostname="192.168.1.1", username="root", password="!@AskeyRtl0100vw")
				ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('reboot')
				print( '\n'.join( ssh_stdout.readlines() ) )
				return 0
			except:
				print("SSH port fail to open!")
				err_count += 1
		else:
			print("---->Reboot device by ADB")
			device = client.device("192.168.1.1:5555")
			device.shell("reboot")
			return 0
			
		if (err_count == 3):
			break
#----------------
# Main Function			
#------------------------------------------------------------------------
if __name__ == '__main__':
	# Initialization
	reboot_method = ""
	default_unlock = 0
	clean_log()
	get_config()
	print("default_unlock {}".format(conf.default_unlock))
	
	# Unlock device ?
	if (conf.default_unlock):
		ret = serial_unlock_device()
		if ret:
			print ("Unlock fail!")
#	for i in range(10000):
#		print("================")
#		print "[Iteration ",i,"]"
#		print("-->Check network status")
#		pingstatus = ping_device()
#
#		if pingstatus is 1:
#			print("--->Ping available, reboot device")
#			#reboot_device("serial")
#			reboot_device("ssh")
#			print("--->reboot device done, waiting...")
#			time.sleep(reboot_delay_sec)
#			continue
#		else:
#			print("Network unavailable, may be a problem.")
#			raise SystemExit
#		print""
	raise SystemExit


