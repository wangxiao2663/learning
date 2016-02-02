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
from multiprocessing import Process
import redis
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
			return '%.3fms' % (ping_time * 1000)
		else:
			return 'time out!'

	def get_result(self):
		xml_list = []
		xml_list.append(r'<item ip=%s port=%s>' % (self.__m_ip, self.__m_port))
		xml_list.append(r'%s' %(self.getRuntime()))
		xml_list.append(r'</item>')
		return ''.join(xml_list)



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

def getXml():
	xml_list = []
	xml_list.append(r'<?xml version="1.0" encoding="utf-8"?>')
	xml_list.append(r'<wlh_query_yyb>')
	for (cs,pinger) in pinger_list.items():
		xml_list.append(pinger.get_result())
	xml_list.append(r'</wlh_query_yyb>')
	return "".join(xml_list)

def die(signum, frame):
	print 'die!'
	r = redis.Redis(host='127.0.0.1', port=6379, db=0)
	xml_value = getXml()
	print xml_value
	try:
		r['ip'] = xml_value
	except:
		print 'redis error!'
	sys.exit(0)


def consumer():		
	cs_list = []
	pinger_list = global_dict[PINGER]
	while True:
		cs_list = yield cs_list
		if len(cs_list) > 0:
			try:
				readlist , writlist , exceptlist = select.select([], cs_list, cs_list)
				for wcs in writlist:
					pinger_list[wcs].OnConnectDone()
					cs_list.remove(wcs)
				for ecs in exceptlist:
					cs_list.remove(ecs)
			except:
				print 'exit!'
				sys.exit(0)


def produce(c, pinger_list):
	print 'produce'
	c.next()
	index = 0
	cs_list = []
	for (cs,pinger) in pinger_list.items():
		index = index + 1
		try:
			pinger.ping()
			cs_list.append(cs)
			if index % 10 == 0:
				cs_list = c.send(cs_list)
		except:
			continue
	while len(cs_list) > 0:
		cs_list = c.send(cs_list)


def ping():
	pinger_list = global_dict[PINGER]
	signal.alarm(5)
	c = consumer()
	produce(c, pinger_list)


global global_dict
global_dict = {}


if __name__ == '__main__':
	signal.signal(signal.SIGALRM, die)
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
	while(1):
		worker = Process(target = ping)
		worker.start()
		worker.join()



		





