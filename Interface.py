'''**********************************************************************************************************************************
 * LDM :- interface.py
 * -Anand Kumar
 * 
 * MainFrame window communicate with each individual download process through interface & all it's information is stored at interface
 * Description :-
 *             Interface :- Contains all information about download process , starts it & establish comminication with MainFrame Widget.
 * 	       All communications are done through flag & it's contents says :-
 *	       Bitwise (|7|6|5|4|3|2|1|0|)===> Terminate,Fatal Error,Downloading,Show,Started,Inform Completion,Terminated,Hide	
***********************************************************************************************************************************'''

import time,sys,urllib2,os
from PyQt4 import QtGui
from dLoadInformation import Info
from multiprocessing import Value,Process
from DownloadWindow import DownloadWindow

class Interface :
	''' Store Download information start 'em '''
	def __init__(self,PARTS=10) :
		self.dLocation = '/home'
		loc=''		
		if os.path.exists(os.getcwd()+'/Locale/desF') :
			f=open(os.getcwd()+'/Locale/desF','r')
			loc=f.read()
			f.close()
		if len(loc) > 0:
			if os.path.exists(loc) :
				self.dLocation=loc
					
		self.PARTS=PARTS
		self.fileName='____'
		self.obj = DownloadWindow(self.PARTS)
		self.clear()
		
	def clear(self) :
		''' reinitialize interface for another download '''
		self.dt=''
		self.tm=''
		self.url=''
		self.flag = 0  # Terminate,Fatal Error,Downloading,Show,Started,Inform Completion,Terminated,Hide
		self.free=0	
		self.length = 0
		self.downloaded = 0	
		self.timeLeft = ''
		self.obj.Clear()
		
	def getInfo(self) :
		''' builds an Info() object out of download informations '''
		obj=Info()
		obj.url=self.url
		obj.fileName=self.fileName
		obj.date=self.dt
		obj.time=self.tm
		obj.length=self.length
		
		return obj
		
	def start_from_Part(self,wMutex,bit) :
		''' When a download is resumed it is started from partial downloads '''
		self.obj.PARTS=self.PARTS
		try :
			x=self.obj.getPartDownload(self.getInfo(),self,wMutex,bit)
			if x==0 :
				self.flag = self.flag | 0x0040
				return
		except :
			self.flag = self.flag | 0x0040
			return
		self.obj.resize(700,225)
		self.free=0
		if x==2:
			self.flag=self.flag | 0x0008
			return
		self.flag=self.flag | 0x0100
		
	def start_Download(self,url,wMutex,bit=0) :
		''' If a fresh download is started it starts from here '''
		self.obj.PARTS=self.PARTS
		self.url=url
		self.dt = time.strftime("%a %d %b %Y",time.localtime())
		self.tm = time.strftime("%H:%M:%S",time.localtime())
		try :	
			self.fileName,self.length=self.obj.getDownload(str(url),self,wMutex,bit)
		except urllib2.URLError as e :		
			self.flag = self.flag | 0x0040				
		except Exception :
			self.flag = self.flag | 0x0040			
			return
		self.obj.resize(700,225)
		self.free=0
		self.flag = self.flag | 0x0008
