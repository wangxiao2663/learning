#!/usr/bin/env python
#coding:utf-8
#filename:p_xml.py

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
import copy
import threading

NORMAL = 0
ERROR = 1
TIMEOUT = 1

PINGER = 'pinger'


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
		self.__m_endtime = 0
		self.__m_socket.connect_ex((str(self.__m_ip), int(self.__m_port)))


	def OnConnectDone(self):
		self.__m_endtime = time.time()		

	def getRuntime(self):
		if self.__m_endtime != 0:
			ping_time = self.__m_endtime - self.__m_stime
			return ping_time
		else:
			return 'time out!'

	def get_result(self):
		print '%s:%s  %s' %(self.__m_ip, self.__m_port, self.getRuntime())



def my_parse_config(filepath):
	tree = ET.ElementTree(file = filepath)
	root = tree.getroot()
	reqlist = [] 									#declare a dict
	for item in root:
		ip = item.get('mobileip')
		port = item.get('portlist')
		port = (port.split('|'))[0].split(',')[1]	#get port
		reqlist.append((ip,port))
	reqset = set(reqlist)
	return reqset


def timeOut(signum, frame):
	for (cs,pinger) in pinger_list.items():
		pinger.get_result()
	exit()

def consumer():		
	ret_list = []
	pinger_list = global_dict[PINGER]
	while True:
		cs_list = yield ret_list
		readlist , writlist , exceptlist = select.select([], cs_list, cs_list)
		for wcs in writlist:
			pinger_list[wcs].OnConnectDone()
			cs_list.remove(wcs)
		for ecs in exceptlist:
			cs_list.remove(ecs)
		ret_list = []
		for cs in cs_list:
			ret_list.append(cs)

def produce(c, pinger_list):
	c.next()
	index = 0
	cs_list = []
	for (cs,pinger) in pinger_list.items():
		index = index + 1
		pinger.ping()
		cs_list.append(cs)
		if index % 10 == 0:
			cs_list = c.send(cs_list)
	while 1:
		c.send(cs_list)



global global_dict
global_dict = {}

if __name__ == '__main__':

	signal.signal(signal.SIGALRM, timeOut)
	path = sys.path[0]
	filepath = "%s/%s" % (path, 'yybtb_utf-8.xml')
	ip_port_set = my_parse_config(filepath)

	cs_list = []
	pinger_list = {}
	for key in ip_port_set:
		ip = key[0]
		port = key[1]
		pinger = Pinger(ip, port)
		cs = pinger.makeSocket()
		cs_list.append(cs)
		pinger_list[cs] = pinger

	global_dict[PINGER] = pinger_list

	c = consumer()
	signal.alarm(5)
	produce(c, pinger_list)



