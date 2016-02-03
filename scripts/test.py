import socket

TEST_IP = '54.223.35.72'
def getLocalIp():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect((TEST_IP,80))
	local_ip = s.getsockname()[0]
	s.close()
	return local_ip

print getLocalIp()