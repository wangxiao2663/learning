#!/usr/bin/env python
#coding:utf-8
#filename:tcpping.py

import socket
import time
import sys

NORMAL = 0
ERROR = 1
TIMEOUT = 1


def ping(ip, port, timeout=TIMEOUT):
    try:
        cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        address = (str(ip), int(port))
        cs.settimeout(timeout)
        status = cs.connect_ex((address))
        if status == 0:
            return NORMAL
        else:
            return ERROR
    except:
        return ERROR


if len(sys.argv) != 3:
        print ur'input example: ./tcpping.py www.baidu.com 80'
        sys.exit(1)

ip = sys.argv[1]
port = sys.argv[2]
#while True:
try:
	time1 = time.time()
	if ping(ip, port) == 0:
		time2 = time.time()
		time3 = (time2 - time1) * 1000
		print time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
		print "%.3fms" % (time3)
#			time.sleep(1)
	else:
		print "time out"
#			time.sleep(1)
except:
#	break
	sys.exit()
