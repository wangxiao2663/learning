#!/usr/bin/env python
#coding:utf-8
#filename:my_ping_version3.py
#this version could lost some port

import string 
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
import sys,os
import socket
import time
import select
import signal


NORMAL = 0
ERROR = 1
TIMEOUT = 1

class Pinger(object):
	def __init__(self, ip, port, timeout = TIMEOUT):
		self.__m_ip = ip
		self.__m_port = port
		self.__m_timeout = timeout
		self.__m_stime = 0
		self.__m_endtime = 0
		self.__m_fd = -1
		self.__m_socket = 0

	def setaddress(self, ip, port):
		self.__m_ip = ip
		self.__m_port = port

	def makeSocket(self):
		cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		cs.settimeout(self.__m_timeout)
		cs.setblocking(0)
		self.__m_socket = cs
		return cs

	def ping(self):
		self.__m_stime = time.time()
		self.__m_socket.connect_ex((str(self.__m_ip), int(self.__m_port)))

	def OnConnectDone(self):
		self.__m_endtime = time.time()		

	def getRuntime(self):
		if self.__m_endtime != 0:
			return self.__m_endtime - self.__m_stime
		else:
			return 'time out!'

	def get_result(self):
		print '%s:%s  %s' %(self.__m_ip, self.__m_port, self.getRuntime())



def my_parse_config(filepath):
	tree = ET.ElementTree(file = filepath)
	root = tree.getroot()
	reqlist = {} 									#declare a dict
	for item in root:
		ip = item.get('mobileip')
		port = item.get('portlist')
		port = (port.split('|'))[0].split(',')[1]	#get port
		reqlist[ip] = port
	return reqlist


def timeOut(signum, frame):
    print("Now, it's the time")
    for (cs,pinger) in pinger_list.items():
    	pinger.get_result()
    exit()


global pinger_list
global starttime
pinger_list = {}

if __name__ == '__main__':
	signal.signal(signal.SIGALRM, timeOut)
	
	path = sys.path[0]
	filepath = "%s/%s" % (path, 'yybtb_utf-8.xml')
	ip_port_list = my_parse_config(filepath)
	cs_list = []

	for (ip, port) in ip_port_list.items():
		pinger = Pinger(ip, port)
		cs = pinger.makeSocket()
		cs_list.append(cs)
		pinger_list[cs] = pinger


	for (cs,pinger) in pinger_list.items():
		pinger.ping()

	signal.alarm(1)

	while 1:
		readlist , writlist , exceptlist = select.select([], cs_list, cs_list)
		for wcs in writlist:
			pinger_list[wcs].OnConnectDone()
			cs_list.remove(wcs)

		for ecs in exceptlist:
			cl_list.remove(ecs)







#c = consumer()
#produce(c, reqlist)


