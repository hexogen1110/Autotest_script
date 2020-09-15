import os
import shutil
from ppadb.client import Client as AdbClient #refer: https://pypi.org/project/pure-python-adb/
#--------------
# Definition
#------------------------------------------------------------------------
adb_hostname = "192.168.1.1"
client = AdbClient(host="127.0.0.1", port=5037)
rel_path = "result"
abs_file_path = os.path.join(os.path.dirname(__file__), rel_path)

status_tuple= (\
["\ifconfig.txt", "ifconfig"],\
["\dmesg.txt", "dmesg"],\
["\ipa_hdr.txt", "cat /sys/kernel/debug/ipa/hdr;dmesg | grep name:"])

# Define status tuple
#----------------
# Sub Function
#------------------------------------------------------------------------
def clean_device_log():
	# rm result dir
	if os.path.exists(abs_file_path):
		shutil.rmtree(abs_file_path)
		
def save_device_log(current_count):
	print("--->Get device status")
	# Using ADB connect to get command result
	result = client.remote_connect("192.168.1.1", 5555)
	device = client.device("192.168.1.1:5555")

	if not os.path.exists(abs_file_path):
		os.makedirs(abs_file_path)

	for ls in status_tuple:
		print ("--->"+ls[0])
		out = device.shell(ls[1])
		f = open(abs_file_path+ls[0], 'a')
		buf = "iteration:" + str(current_count) + "\n"
		f.write(buf)
		f.write(out)
		f.close()
		
		
def save_test_result(current_count, result):
	if not os.path.exists(abs_file_path):
		os.makedirs(abs_file_path)

	f = open(abs_file_path+"\\test_result.log", 'a')
	buf = "iteration:" + str(current_count) + ", test result:" + result + "\n"
	print(buf)
	f.write(buf)
	f.close()