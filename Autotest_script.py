import configparser
from ppadb.client import Client as AdbClient #refer: https://pypi.org/project/pure-python-adb/
import paramiko #python ssh module

from serial_func import *
from sys_log import *
from network import ping_device

#--------------
# Definition
#------------------------------------------------------------------------

client = AdbClient(host="127.0.0.1", port=5037)
pingstatus = False
reboot_delay_sec = 60
loop_count = 10000

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
	# Reboot method
	conf.reboot_method = config.get('Reboot method', 'reboot_method')
	# Misc
	conf.default_unlock = config.getboolean('Misc', 'default_unlock_device')
	conf.platform = config.get('Misc', 'platform')
	# Test item
	conf.reboot_test = config.getboolean('Test item', 'reboot_test')
	conf.led_test = config.getboolean('Test item', 'led_test')
	conf.iperf_test = config.getboolean('Test item', 'iperf_test')
	
def set_config(sect, item, value):
	config = configparser.ConfigParser()
	config.read('Config.ini')
	config[sect][item] = value
	with open('Config.ini', 'w') as configfile:
		config.write(configfile)
	


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
	print("reboot_test={}".format(conf.reboot_test))	
	
	# Unlock device ?
	if conf.default_unlock == 1:
		ret = serial_unlock_device(conf.platform)
		if ret:
			print ("Unlock fail!")
		else:
			print ("Unlock success!, rebooting...")
			# Set unlock bit to 0 to prevent unlock at everytime run this script
			set_config('Misc', 'default_unlock_device', "0")			
			time.sleep(reboot_delay_sec)
	
	# Main test area
	for i in range(loop_count):
		print("================")
		print "[Iteration ",i,"]"
		
		# Reboot test
		if conf.reboot_test == 1:
			print("--> Reboot test start...")
			print("--> Check network status...")
			status = ping_device(conf.platform)
			if status is 1:
				print("---> Ping available, reboot device")
				reboot_device(reboot_method)
				print("--->reboot device done, waiting...")
				time.sleep(reboot_delay_sec)
			continue
		else:
			print("Network unavailable, may be a problem.")
			raise SystemExit
		print""
	raise SystemExit


