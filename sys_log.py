import os
from ppadb.client import Client as AdbClient #refer: https://pypi.org/project/pure-python-adb/
#--------------
# Definition
#------------------------------------------------------------------------
adb_hostname = "192.168.1.1"
client = AdbClient(host="127.0.0.1", port=5037)

# Define status tuple
status_tuple= (\
["ipa_hdr.txt", "cat /sys/kernel/debug/ipa/hdr;dmesg | grep name:"],\
["ipacm_time.txt", "dmesg | grep ipacm"],\
["ip_ne.txt", "ip ne"])

#----------------
# Sub Function
#------------------------------------------------------------------------
def clean_log():
	for ls in status_tuple:
		if os.path.exists(ls[0]):
			os.remove(ls[0])
			
def save_log(current_count):
	print("--->Get device status")
	device = client.device("192.168.1.1:5555")
	
	for ls in status_tuple:
		print ("--->"+ls[0])
		out = device.shell(ls[1])
		f = open(ls[0], 'a')
		buf = "iteration:" + str(current_count) + "\n"
		f.write(buf)
		f.write(out)
		f.close()