import configparser
import subprocess
import os
import time
from ppadb.client import Client as AdbClient #refer: https://pypi.org/project/pure-python-adb/
import paramiko #python ssh module
from serial_func import *

#--------------
# Definition
#------------------------------------------------------------------------
adb_hostname = "192.168.1.1"
client = AdbClient(host="127.0.0.1", port=5037)
pingstatus = False
reboot_delay_sec = 60
serial_port = "COM81"
loop_count = 10000

# Define status tuple
status_tuple= (\
["ipa_hdr.txt", "cat /sys/kernel/debug/ipa/hdr;dmesg | grep name:"],\
["ipacm_time.txt", "dmesg | grep ipacm"],\
["ip_ne.txt", "ip ne"])

# Initialize object for config
class conf: 
    def __init__(self): 
        self.reboot_method = ""
        self.default_unlock = 0   
        self.platform = ""   
		self.reboot_test = 0
		self.led_test = 0
		self.iperf_test = 0
		
#----------------
# Sub Function
#------------------------------------------------------------------------
def get_config():
	config = configparser.ConfigParser()
	config.read('Config.ini')
	conf.reboot_method = config.get('Reboot method', 'reboot_method')
	conf.default_unlock = config.get('Misc', 'default_unlock_device')
	conf.platform = config.get('Misc', 'platform')
	print("conf.default_unlock={}".format(conf.default_unlock))	
	
def set_config(sect, item, value):
	config = configparser.ConfigParser()
	config.read('Config.ini')
	config[sect][item] = value
	with open('Config.ini', 'w') as configfile:
		config.write(configfile)
	
def clean_log():
	for ls in status_tuple:
		if os.path.exists(ls[0]):
			os.remove(ls[0])

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
				serial_reboot_device()
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
	clean_log()
	get_config()

	print("default_unlock {}".format(conf.default_unlock))
	print("platform {}".format(conf.platform))
	
	# Unlock device ?
	if (conf.default_unlock):
		ret = serial_unlock_device(conf.platform)
		if ret:
			print ("Unlock fail!")
		else:
			print ("Unlock success!, rebooting...")
			# Set unlock bit to 0 to prevent unlock at everytime run this script
			set_config('Misc', 'default_unlock_device', "0")			
			time.sleep(reboot_delay_sec)
			
	for i in range(loop_count):
		print("================")
		print "[Iteration ",i,"]"
#		print("-->Check network status")
#		pingstatus = ping_device()
#
#		if pingstatus is 1:
#			print("--->Ping available, reboot device")
		reboot_device("serial")
#			reboot_device("ssh")
#			print("--->reboot device done, waiting...")
		time.sleep(reboot_delay_sec)
#			continue
#		else:
#			print("Network unavailable, may be a problem.")
#			raise SystemExit
#		print""
	raise SystemExit


