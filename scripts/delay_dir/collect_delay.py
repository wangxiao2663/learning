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
from struct import pack, unpack


NORMAL = 0
ERROR = 1
TIMEOUT = 1

PINGER = 'pinger'
TEST_IP = '54.223.35.72'
SERVER_IP = '192.168.200.132'
SERVER_PORT = 9501
GROUPSIZE = 50

DEFAULT_DELAYTIME = 3000
CONFIG_FILE = 'yybtb.xml'

START_HEAD = 'fdfdfdfd'
END_TAIL = 'DONEDONEDONE'

provincesArr = {
			'11':'北京',
			'12':'天津',
			'13':'河北',
			'14':'山西',
			'15':'内蒙古',
			'21':'辽宁',
			'22':'吉林',
			'23':'黑龙江',
			'31':'上海',
			'32':'江苏',
			'33':'浙江',
			'34':'安徽',
			'35':'福建',
			'36':'江西',
			'37':'山东',
			'41':'河南', 
			'42':'湖北',
			'43':'湖南',
			'44':'广东',
			'45':'广西',
			'46':'海南',
			'50':'重庆',
			'51':'四川',
			'52':'贵州',
			'53':'云南',
			'54':'西藏',
			'61':'陕西',
			'62':'甘肃',
			'63':'青海',
			'64':'宁夏',
			'65':'新疆',
			'71':'台湾',
			'81':'香港',
			'82':'澳门', 
			'0':'其他1',
			'99':'其他2'
			}


ISP_Server = {
	'铁通':'CMCC',
	'电信':'CT',
	'移动':'CMCC',
	'联通':'CU'
}



def getProvinceKey(Province):
	for (key,value) in provincesArr.items():
		try:
			nPos = Province.index(value)
			return key
		except:
			continue
	return None;


def getIsp(isp):
	for (name, key) in ISP_Server.items():
		try:
			nPos = isp.index(name)
			return key
		except:
			continue
	print isp
	return 'Other'



def ip2string( ip ):
    a = (ip & 0xff000000) >> 24
    b = (ip & 0x00ff0000) >> 16
    c = (ip & 0x0000ff00) >> 8
    d = ip & 0x000000ff
    return "%d.%d.%d.%d" % (a,b,c,d)

def string2ip( str ):
    ss = string.split(str, '.');
    ip = 0L
    for s in ss: ip = (ip << 8) + string.atoi(s)
    return ip;

class IpLocater :
    def __init__( self, ipdb_file ):
        self.ipdb = open( ipdb_file, "rb" )
        # get index address 
        str = self.ipdb.read( 8 )
        (self.first_index,self.last_index) = unpack('II',str)
        self.index_count = (self.last_index - self.first_index) / 7 + 1

    def getString(self,offset = 0):
        if offset :
            self.ipdb.seek( offset )
        str = ""
        ch = self.ipdb.read( 1 )
        (byte,) = unpack('B',ch)
        while byte != 0:
            str = str + ch
            ch = self.ipdb.read( 1 )
            (byte,) = unpack('B',ch) 
        return str

    def getLong3(self,offset = 0):
        if offset :
            self.ipdb.seek( offset )
        str = self.ipdb.read(3)
        (a,b) = unpack('HB',str)
        return (b << 16) + a

    def getAreaAddr(self,offset=0):
        if offset :
            self.ipdb.seek( offset )
        str = self.ipdb.read( 1 )
        (byte,) = unpack('B',str)
        if byte == 0x01 or byte == 0x02:
            p = self.getLong3()
            if p:
                return self.getString( p )
            else:
                return ""
        else:
            return self.getString( offset )

    def getAddr(self,offset ,ip = 0):
        self.ipdb.seek( offset + 4)

        countryAddr = ""
        areaAddr = ""
        str = self.ipdb.read( 1 )
        (byte,) = unpack('B',str)
        if byte == 0x01:
            countryOffset = self.getLong3()
            self.ipdb.seek(countryOffset )
            str = self.ipdb.read( 1 )
            (b,) = unpack('B',str)
            if b == 0x02:
                countryAddr = self.getString( self.getLong3() )
                self.ipdb.seek( countryOffset + 4 )
            else:
                countryAddr = self.getString( countryOffset )
            areaAddr = self.getAreaAddr()
        elif byte == 0x02:
            countryAddr = self.getString( self.getLong3() )
            areaAddr = self.getAreaAddr( offset + 8 )
        else:
            countryAddr = self.getString( offset + 4 )
            areaAddr = self.getAreaAddr( )

        return countryAddr + "/" + areaAddr

    def output(self, first ,last ):
        if last > self.index_count :
            last = self.index_count
        for index in range(first,last):
            offset = self.first_index + index * 7
            self.ipdb.seek( offset )
            buf = self.ipdb.read( 7 )
            (ip,of1,of2) = unpack("IHB",buf)
            print "%s - %s" % (ip, self.getAddr( of1 + (of2 << 16) ) )

    def find(self,ip,left,right):
        if right-left == 1:
            return left
        else:
            middle = ( left + right ) / 2
            offset = self.first_index + middle * 7
            self.ipdb.seek( offset )
            buf = self.ipdb.read( 4 )
            (new_ip,) = unpack("I",buf)
            if ip <= new_ip :
                return self.find( ip, left, middle )
            else:
                return self.find( ip, middle, right )

    def getIpAddr(self,ip):
        index = self.find( ip,0,self.index_count - 1 )
        ioffset = self.first_index + index * 7
        aoffset = self.getLong3( ioffset + 4)
        address = self.getAddr( aoffset )
        return unicode(address,'gb2312').encode('utf-8')


class QsInfo(object):
	def __init__(self, qsid, wtid, yybname, area, qsname, ip, port):
		self.__m_qsid = qsid
		self.__m_wtid = wtid
		self.__m_yybname = yybname
		self.__m_area = area
		self.__m_qsname = qsname
		self.__m_ip = ip
		self.__m_port = port

	def getIpPort(self):
		return (self.__m_ip, self.__m_port)

	def getInfo(self):
		xml_list = []
		xml_list.append(r'<QsInfo><qsid>%s</qsid><wtid>%s</wtid><yybname>%s</yybname><area>%s</area><qsname>%s</qsname></QsInfo>' 
						% (self.__m_qsid, self.__m_wtid, self.__m_yybname, self.__m_area, self.__m_qsname))
		return ''.join(xml_list)	



class Pinger(object):
	def __init__(self, ip, port, address, ISP, timeout = TIMEOUT):
		self.__m_ip = ip
		self.__m_port = port
		self.__m_address = address
		self.__m_isp = ISP
		self.__m_timeout = timeout
		self.__m_stime = 0
		self.__m_endtime = 0
		self.__m_fd = -1
		self.__m_socket = None
		self.__m_qsList = []


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

	def getIsp(self):
		return self.__m_isp

	def getAddress(self):
		return self.__m_address

	def getRuntime(self):
		if self.__m_endtime != 0:
			ping_time = self.__m_endtime - self.__m_stime
			return '%.3f' % (ping_time * 1000)
		else:
			return -1

	def addQsInfo(self, qsInfo):
		self.__m_qsList.append(qsInfo)


	def get_result(self):
		xml_list = []
		result = self.getRuntime()
		if (result < 0):
			result = 'time out!'
		xml_list.append(r'<item>')
		xml_list.append(r'<ip>%s</ip><port>%s</port><result>%s</result>' % (self.__m_ip, self.__m_port, result))
		xml_list.append(r'<QsList>')
		for qsInfo in self.__m_qsList:
			xml_list.append(qsInfo.getInfo()) 
		xml_list.append(r'</QsList>')
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
		self.__m_IPInfo = IpLocater('QQWry.Dat')
		self.__m_localip = ''
		self.__m_pinger_dict = {}
		self.__m_config = configPath
		self.__m_ip_port_set = {}
		self.__m_pinger_list = []
		self.__m_cs_list = []
		self.__m_calc_pinger_dict = {}
		self.__m_ip_port_pinger_dict = {}
		self.__m_socket = ''
		self.__m_qsList = []


	def parse_config(self):
		dstr = ""
		with open(self.__m_config, 'r') as fp:
			dstr = fp.read()
			dstr = dstr.decode('GBK').encode('utf-8')
			dstr = dstr.replace('GBK', 'utf-8')
		root = ET.fromstring(dstr)
		reqlist = [] 		

		for item in root:
			ip = item.get('mobileip')
			port = item.get('portlist')
			port = (port.split('|'))[0].split(',')[1]	#get port
			reqlist.append((ip,port))
			qsid = item.get('qsid')
			wtid = item.get('wtid')
			yybname = item.get('yybname')
			area = item.get('area')
			qsname = item.get('qsname')
			qsInfo = QsInfo(qsid, wtid, yybname, area, qsname, ip, port)
			self.__m_qsList.append(qsInfo)

		self.__m_ip_port_set = set(reqlist)


	def getLocalIp(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect((TEST_IP,80))
		local_ip = s.getsockname()[0]
		s.close()
		return local_ip

	def addPingerData(self):
		root = ET.fromstring(self.__m_dstr)
		reqlist = [] 									#declare a dict
		for item in root:
			ip = item.get('mobileip')
			port = item.get('portlist')
			port = (port.split('|'))[0].split(',')[1]	#get port
			
		

	def preWork(self):
		self.parse_config()
		self.__m_localip = self.getLocalIp()
		self.connect()
		print self.__m_localip
		for key in self.__m_ip_port_set:
			ip = key[0]
			port = key[1]
			try:
				address = self.__m_IPInfo.getIpAddr(string2ip(ip))
			except:
				continue 
			addressKey = getProvinceKey(address)
			if (address == None):
				continue
			isp = getIsp(address)

			pinger = Pinger(ip, port, addressKey, isp)
			self.__m_pinger_list.append(pinger)
			self.__m_ip_port_pinger_dict[(ip,port)] = pinger

			if self.__m_calc_pinger_dict.has_key(isp) == False:
				self.__m_calc_pinger_dict[isp] = dict()
			if self.__m_calc_pinger_dict[isp].has_key(addressKey) == False:
				self.__m_calc_pinger_dict[isp][addressKey] = []
			self.__m_calc_pinger_dict[isp][addressKey].append(pinger);

		for qsInfo in self.__m_qsList:
			key = qsInfo.getIpPort()
			try:
				pinger = self.__m_ip_port_pinger_dict[key]
				pinger.addQsInfo(qsInfo)
			except:
				continue

		print 'work down'
	

	def connect(self):
		self.__m_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			status = self.__m_socket.connect_ex((SERVER_IP, SERVER_PORT))
			if status != NORMAL:
				return False
			return True
		except:
			print 'server connot connect!'
			sys.exit(0)


	def send(self, msg):
		new_msg = "%s:%s" % (self.__m_localip,msg)
		new_msg = new_msg.encode('GBK')
		try:
			print 'send hello'
			self.__m_socket.send(START_HEAD)
		except:
			if self.connect() == True:
				self.send(msg)
			else:
				return
		time.sleep(1);
		try:
			print 'send message'
			self.__m_socket.send(new_msg)
		except:
			if self.connect() == True:
				self.send(msg)
			else:
				return

		time.sleep(1);
		try:
			print 'send tail'
			self.__m_socket.send(END_TAIL)
		except:
			if self.connect() == True:
				self.send(msg)
			else:
				return


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
			if index % GROUPSIZE == 0 and len(cs_list) > 0:
				cs_list = self.receive(cs_list)

		while len(cs_list) > 0:
			cs_list = self.receive(cs_list)

		self.send(self.getResult())
		self.stop()


	def receive(self, cs_list):
		try:
			readlist , writlist , exceptlist = select.select([], cs_list, cs_list, 1)
			for wcs in writlist:
				self.__m_pinger_dict[wcs].OnConnectDone()
				cs_list.remove(wcs)
			for ecs in exceptlist:
				cs_list.remove(ecs)
			if (len(writlist) == 0 and len(exceptlist) == 0):
				cs_list = []
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
		xml_list.append(r'<?xml version="1.0" encoding="GBK"?>')
		xml_list.append(r'<root>')
		time_now = time.strftime("%Y-%m-%d-%H-%M-%S",time.localtime())
		xml_list.append(r'<time>%s</time>' % time_now)
		xml_list.append(r'<local_ip>%s</local_ip>' % (self.__m_localip))
		xml_list.append(r'<delayMessage>')
		for (isp, provice_dict) in self.__m_calc_pinger_dict.items():
			xml_list.append(r'<%s>' % isp)
			for (provice, pinger_list) in provice_dict.items():
				msg_list = []
				nCount = len(pinger_list)
				if (nCount <= 0):
					continue
				delayTime = 0.000;
				for pinger in pinger_list:
					runtime = pinger.getRuntime()
					if (runtime < 0):
						delayTime = delayTime + DEFAULT_DELAYTIME
					else:
						delayTime = delayTime + float(runtime)
					msg_list.append(pinger.get_result())

				fAvgDelayTime = delayTime / nCount
				xml_list.append(r'<Row>')
				xml_list.append(r'<provice>%s</provice>' % provice)
				xml_list.append(r'<OvertimeRate>%.3f</OvertimeRate>' % fAvgDelayTime)
				xml_list.append(r'<detailMsg>%s</detailMsg>' % "".join(msg_list))
				xml_list.append(r'</Row>')
				#xml_list.append(r'<detailRow provice=%s OvertimeRate = %.3f>%s</provice>' % (provice, fPer, "".join(msg_list)))
			xml_list.append(r'</%s>' % isp)
		xml_list.append(r'</delayMessage>')
		xml_list.append(r'</root>')
		return "".join(xml_list)


def getIpAddr(domain):
	'''
	阻塞，效率低
	'''
	ipAddr = socket.getaddrinfo(domain, None)[0][4][0]
	return ipAddr

def main():
	path = sys.path[0]
	filepath = "%s/%s" % (path, CONFIG_FILE)
	pManager = PingerManager(filepath)
	pManager.preWork()
	pManager.start()



if __name__ == '__main__':
	main()

