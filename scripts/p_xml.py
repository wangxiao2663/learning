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

	def run(self):
		print 'run!'
		cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		address = (str(self.__m_ip), int(self.__m_port))
		cs.settimeout(self.__m_timeout)
		self.__m_stime = time.time()
		cs.setblocking(0)
		cs.connect_ex((address))
		self.__m_socket = cs
		return cs

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

'''
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


def consumer():
	r = dict
	while True:
		string = yield r
		if not string:
			continue
		tmplist = string.split(":")
		ip = tmplist[0]
		port = tmplist[1]
		print('[CONSUMER] Consuming %s:%s...' % (tmplist[0],tmplist[1]))
		try:
			time1 = time.time()
			if ping(ip, port) == 0:
				time2 = time.time()
				time3 = (time2 - time1) * 1000
				print time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
				print "%.3fms" % (time3)
#				time.sleep(1)
			else:
				print "time out"
		except:
	#	break
			print "error!"
			sys.exit()
		r = '200 OK'

def produce(c, reqlist):
	c.next()
	for (ip, port) in reqlist.items():
		print('[PRODUCER] →→ Producing %s...' % ip)
		cr = c.send('%s:%s' % (ip, port))
		print('[PRODUCER] Consumer return: %s' % cr)
	c.close()

'''

def timeOut(signum, frame):
    print("Now, it's the time")
    for (cs,pinger) in pinger_list.items():
    	pinger.get_result()
    exit()

global pinger_list
pinger_list = {}

signal.signal(signal.SIGALRM, timeOut)


path = sys.path[0]
filepath = "%s/%s" % (path, 'yybtb_utf-8.xml')
ip_port_list = my_parse_config(filepath)


cs_list = []

for (ip, port) in ip_port_list.items():
	pinger = Pinger(ip, port)
	cs = pinger.run()
	cs_list.append(cs)
	pinger_list[cs] = pinger

signal.alarm(1)
while len(cs_list) > 0:
	print "waiting for next event, count = %d" % len(cs_list)
#--------------------------------------------------
	readlist , writlist , exceptlist = select.select([], cs_list, cs_list)
#--------------------------------------------------
#    for temp in readable:
#        print temp	
#    print "writable:",writable
	for wcs in writlist:
		for cs in cs_list:
			if cs == wcs:
				pinger_list[cs].OnConnectDone()
				cs_list.remove(cs)
				break
	print "exceptional:",exceptlist

print 'done!'




#c = consumer()
#produce(c, reqlist)


