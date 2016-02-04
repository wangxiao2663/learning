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
from multiprocessing import Process, Queue


NORMAL = 0
ERROR = 1
TIMEOUT = 1

PINGER = 'pinger'
REDIS_HOST = '127.0.0.1'
REDIS_PORT = '6379'
REDIS_DB = 0
REDIS_PASSWORD = ''
#TEST_IP = '54.223.35.72'
TEST_IP = 'www.sina.com.cn'
SERVER_IP = '127.0.0.1'


class Pinger(object):
	def __init__(self, ip, port, timeout = TIMEOUT):
		self.__m_ip = ip
		self.__m_port = port
		self.__m_timeout = timeout
		self.__m_stime = 0
		self.__m_endtime = 0
		self.__m_fd = -1
		self.__m_socket = None

	def setaddress(self, ip, port):
		self.__m_ip = ip
		self.__m_port = port

	def makeSocket(self):
		if self.__m_socket:
			self.__m_socket.close()
			self.__m_socket = ''
		cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		cs.settimeout(self.__m_timeout)
		cs.setblocking(0)
		self.__m_socket = cs
		return cs

	def ping(self):
		self.__m_stime = time.time()
		self.__m_endtime = 0
		try:
			self.__m_socket.connect_ex((str(self.__m_ip), int(self.__m_port)))
		except:
			print 'ping failed'

	def OnConnectDone(self):
		self.__m_endtime = time.time()

	def endWork(self):
		self.__m_socket.close()

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

	def stop(self):
		try:
			self.__m_socket.setblocking(1)
			self.__m_socket.shutdown(socket.SHUT_RDWR)
		except:
			print 'error..'
		self.__m_socket.close()
		self.__m_socket = None


class PingerManager(object):
	def __init__(self, configPath):
		self.__m_localip = ''
		self.__m_pinger_dict = {}
		self.__m_config = configPath
		self.__m_ip_port_set = {}
		self.__m_pinger_list = []
		self.__m_cs_list = []
		self.__m_socket = ''


	def parse_config(self):
		tree = ET.ElementTree(file = self.__m_config)
		root = tree.getroot()
		reqlist = [] 									#declare a dict
		for item in root:
			ip = item.get('mobileip')
			port = item.get('portlist')
			port = (port.split('|'))[0].split(',')[1]	#get port
			reqlist.append((ip,port))
		self.__m_ip_port_set = set(reqlist)


	def getLocalIp(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect((TEST_IP,80))
		local_ip = s.getsockname()[0]
		s.close()
		return local_ip


	def preWork(self):
		self.parse_config()
		self.__m_localip = self.getLocalIp()
		self.connect()
		print self.__m_localip
		for key in self.__m_ip_port_set:
			ip = key[0]
			port = key[1]
			pinger = Pinger(ip, port)
			self.__m_pinger_list.append(pinger)
		print 'work down'
	


	def connect(self):
		self.__m_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			status = self.__m_socket.connect_ex(('127.0.0.1', 9501))
		except:
			print 'server connot connect!'
			sys.exit(0)


	def send(self, msg):
		new_msg = "%s:%s" % (self.__m_localip,msg)
		print new_msg
		try:
			self.__m_socket.send(new_msg)
		except:
			self.connect()
			self.__m_socket.send(new_msg)



	def run(self):
		self.__m_pinger_dict = {}
		self.__m_cs_list = []
		for pinger in self.__m_pinger_list:
			cs = pinger.makeSocket()
			self.__m_pinger_dict[cs] = pinger
			self.__m_cs_list.append(cs)

		cs_list = []
		pinger_list = self.__m_pinger_dict

		index = 0
		for (cs, pinger) in self.__m_pinger_dict.items():
			index = index + 1			
			pinger.ping()
			cs_list.append(cs)
			if index % 50 == 0 and len(cs_list) > 0:
				print len(cs_list)
				cs_list = self.receive(cs_list)

		while len(cs_list) > 0:
			cs_list = self.receive(cs_list)

		self.send(self.getResult())
		self.stop()


	def receive(self, cs_list):
		try:
			print 'try'
			readlist , writlist , exceptlist = select.select([], cs_list, cs_list, 1)
			print len(writlist)
			for wcs in writlist:
				self.__m_pinger_dict[wcs].OnConnectDone()
				cs_list.remove(wcs)
			for ecs in exceptlist:
				cs_list.remove(ecs)
			if (len(writlist) == 0 and len(exceptlist) == 0):
				cs_list = []
				print 'empty'
			print 'select over'
		except:
			print 'select error!'
		return cs_list


	def start(self):
		while 1:
			self.run()
			time.sleep(10)
			print 'wake up'


	def stop(self):
		for pinger in self.__m_pinger_list:
			pinger.stop()
		self.__m_pinger_dict = {}


	def getResult(self):
		xml_list = []
		xml_list.append(r'<?xml version="1.0" encoding="utf-8"?>')
		time_now = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
		xml_list.append(r'<time>%s</time>' % time_now)
		xml_list.append(r'<massage local_ip="%s" count="%d">' % (self.__m_localip, len(self.__m_pinger_list)))
		for pinger in self.__m_pinger_list:
			xml_list.append(pinger.get_result())
		xml_list.append(r'</massage>')
		return "".join(xml_list)



if __name__ == '__main__':
	path = sys.path[0]
	filepath = "%s/%s" % (path, 'yybtb_utf-8.xml')
	pManager = PingerManager(filepath)
	pManager.preWork()
	pManager.start()

