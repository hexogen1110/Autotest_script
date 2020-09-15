import subprocess
import time
#--------------
# Definition
#------------------------------------------------------------------------
rtl0108_hostname = "192.168.1.1"
rtl0300_hostname = "172.20.168.1"

#----------------
# Sub Function
#------------------------------------------------------------------------
def ping_device(platform):
	err_count = 0
	if platform == "rtl0108":
		hostname = rtl0108_hostname
	else:
		hostname = rtl0300_hostname
	while err_count < 9:
		print("Ping device...{} times".format(err_count))
		ping_command = "ping -n 2 " + hostname
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