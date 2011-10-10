'''**********************************************************************************************************************************
 * LDM :- Fork_Download.py
 * -Anand Kumar
 * 
 * To download & keep track of each and individual download , this module is called.It also stores information each download.
 * Description :-
 *             Fork_Info :- It stores each individual download information & all the shared variable to communicate between individual
 *			    process.
 *             Fork_Download :- Each individual download process is forkVariousPart.
 * 	       YTube_Download :- fetches youtube files & links to proceed through download
***********************************************************************************************************************************'''

import os,sys,time,re,urllib2,array,thread,math
from threading import Timer
from dLoadInformation import dLoadInfo,Info
from UIXML import UIXML
from multiprocessing import Queue,Process,Value,Lock

class Fork_Info :
	'''A data-structure to store information about download partitions'''
	def __init__(self) :
		self.mutex = Lock() # A mutex variable required to handle critial zones of the individual download
		self.type = 0       # A boolean variable to identify whether download is a resumed download of initial download.
		self.LOCK = Value('i') 
		''' A shared variable required to get the information about the state of each download
         	     LOCK                          state
		     1        Download complete not writting information into file
		     2        Information has been written into file now fetching next packet
		     3        Process download complete & have been written into file 					
		'''
		self.length = Value('i') # A shared variable that stores net download till then
		self.initiated = Value('i') # A shared variable that tells whether download has been initiated or not

		''' Intitialization '''
		self.P=None		
		self.LOCK.value = 2
		self.length.value = 0
		self.initiated.value = 0
		self.LL=0
		self.UL=0
		self.timeElapsed = 0
		
	def reInit(self) :
		''' Reinitializes all variables for another download '''
		self.type=0
		self.P=None
		self.length.value=0
		self.initiated.value=0
		self.UL=0
		self.LL=0
		self.timeElapsed=0
		
class Fork_Download :
	''' Each individual download is done through this class '''
	def __init__(self) :
		pass
		
	def forkVariousPart(self,obj,url,fileName,transmit,monitor) :
		''' To fetch individual part this technique is used '''
		if obj.UL-(obj.LL+obj.length.value) <= 0 : # checks whether partition is a valid partition
			sys.exit(0)
		# intializes state
		obj.LOCK.value=2
		req = urllib2.Request(url) # perform the request from the url
		proXy={}
		proxy_info=UIXML().getProxyInformation('&LDM') # If user is working under a proxy , fetches proxy information
		try :
			if len(proxy_info) == 2:
				proXy['host']=str(proxy_info[0])
				proXy['port']=int(proxy_info[1])
				proxy="http://%(host)s:%(port)d"%proXy
				info={"http":""}
				info["http"]="http://%(host)s:%(port)d"%proXy
				handler = urllib2.ProxyHandler(info)
				opener=urllib2.build_opener(handler) # Add proxy information
			elif len(proxy_info)==4 :	
				proXy['host']=str(proxy_info[0])
				proXy['port']=int(proxy_info[1])
				proXy['user']=str(proxy_info[2])
				proXy['pass']=str(int(proxy_info[3]))
				proxy="http://%(user)s:%(pass)s@%(host)s:%(port)d"%proXy
				info={"http":""}
				info["http"]="http://%(user)s:%(pass)s@%(host)s:%(port)d"%proXy
				handler = urllib2.ProxyHandler(info)
				opener=urllib2.build_opener(handler)	# Add USER & PASS	
			else :			
				opener = urllib2.build_opener() # build empty handler	
		except Exception,e :
			print "Error : ",str(e)
			
		# adds requisite headers to the handler
		opener.addheaders = [('User-Agent','Magic Browser'),('Range','bytes='+str(obj.LL+obj.length.value)+'-'+str(obj.UL))]
	
		opened=False	
		while not(opened) :
			try :
				stream1 = opener.open(req) # Using handler to start the request.
				opened=True
			except :
				opened=False

		if obj.type == 0 :
			transmit.put('Init:'+str(obj.LL)+':'+str(obj.UL)) # puts the Intialization information & partition range in PIPE
			obj.initiated.value=1 # Download Initiated
		data=''
		while True :
			data=stream1.read(500000) # Reading http packets.

			if not(len(data)) :
				break
			if obj.LOCK.value == 2 : # If process has taken too much time to download must be killed
				obj.mutex.acquire(True)
				obj.LOCK.value = 1  # if download has been completed it must write LOCK variable before writing into file
				obj.mutex.release()
				
				obj.length.value+=len(data)
				fObj = open(os.getcwd()+'/Download/'+fileName+'_LDM/'+'LDM_'+str(obj.LL),'ab') # writing into file
				transmit.put(str(obj.length.value)+':'+str(obj.LL)+':'+str(obj.UL)) # Puts download range & info into PIPE
				monitor.put(str(os.getpid())+':'+str(obj.length.value)+':'+str(obj.LL)+':'+str(obj.UL)) # Inform monitor
				fObj.write(data) # writing data into file.
				fObj.close()
				
				obj.mutex.acquire(True)
				obj.LOCK.value = 2 # releases LOCK
				obj.mutex.release()
			else :
				while obj.LOCK.value==0 : # If process has been selected to kill it must wait before Monitor terminates it
					time.sleep(3)
		
		while obj.LOCK.value == 0 :
			pass
		obj.mutex.acquire(True)
		obj.LOCK.value=3 #LOCKS before termination
		obj.mutex.release()
		while obj.LOCK.value == 0 :
			pass
		monitor.put(str(os.getpid())+':Done:'+str(obj.LL)+':'+str(obj.UL)) # Sends final information to the Monitor process
		transmit.put('Done:'+str(obj.LL)+':'+str(obj.UL)) # transmit download range with required information
		
		sys.exit(0)
	
class YTube_Download :
	'''Takes download , partition it , run individual downloads & monitors it '''
	def __init__(self,maxLink=10) :	
		self.paused=0 # To check whether download is paused or not
		self.wMutex=None  # A mutex variable to write download information into a file
		self.ext=''  
		self.netLink=maxLink # Decides maximum number of parallel downloads
		self.Commited=0	 # Decides how many downloads have been commited
		self.PARTS=maxLink # PARTS of individual file
		self.info=None # Information about downloads
		self.url='linkinAnand.blogspot.com' # Url to be downloaded
		self.fileName='LDM' # Destination file
		self.pid_dict={} # A dictionary that stores PID of various processes
		for i in range(self.PARTS) : # dictionary intialization
			self.pid_dict[i]=None 
		self.transmit = 0 # Tranmission PIPE
		self.monitor = Queue() # Monitoring PIPE
		self.regX='%7Chttp(.*?videoplayback.*?)%2C' # regEx to search html for content
	
	def clear(self) :
		''' Clears all initial content & brings them to initial form '''
		self.paused=0
		self.Commited=0
		self.info=None
		while not(self.monitor.empty()) :
			x=self.monitor.get()
		
	def resume(self) :
		''' It checks for Idle processes & kill them after communicating with them also forks new one '''
		for key in self.pid_dict :
			'''checks which are the processes which are to be killed '''
			obj=self.pid_dict[key]
			if not(obj==None) :
				if not(obj.LOCK.value==3) : # checks if download has completed
					fVP=Fork_Download()
					obj.P=0
					obj.timeElapsed=0
				
					if obj.initiated.value == 0 :	# If download has not been initiated replace it
						obj.type=0
						p = Process(target=fVP.forkVariousPart,args=(obj,self.url,str(self.fileName), self.transmit,self.monitor))
					else : # If download has been initiated append new process with it
						obj.type=1
						p = Process(target=fVP.forkVariousPart,args=(obj,self.url,str(self.fileName), self.transmit,self.monitor))
					p.start()
					obj.P = p
					self.pid_dict[key] = obj
		Timer(2,self.Monitor).start()
			
	def killSaveAllInformation(self,bit=0) :
		''' Kills all information of process & saves it's information '''
		for key in self.pid_dict :
			obj = self.pid_dict[key]
			if not(obj == None) :
				obj.mutex.acquire(True)
				while obj.LOCK.value == 1: # Wait till process is in a state (concurrent) to be killed
					pass
				if not(obj.LOCK.value == 3) :
					obj.LOCK.value=0
					if not(obj.P==None):
						if obj.P.is_alive(): #Kill if process is alive
							obj.P.terminate()
				obj.mutex.release()				
		
		if bit == 1:
			''' Operates if all download has been commited '''
			if not(self.info==None) :
				for key in self.pid_dict :
					obj = self.pid_dict[key]
					if not(obj==None) :
						self.info.partition[key]=[obj.LL,obj.UL,obj.length.value] 								
				self.wMutex.acquire(True)
				dLoadInfo().WriteInformation(self.info)
				self.wMutex.release()
				self.clear()			
				
		while not(self.monitor.empty()) :
			''' Empties PIPE & forces them to fill the output queue '''
			data=self.monitor.get()
			data=data.split(':')
			if len(data) == 4 :
				if data[1]=='Done' :
					self.Commited=self.Commited+1 # Commits all process


	def Monitor(self) :
		''' Monitors all download process & their progress '''
		if len(self.pid_dict) == self.Commited :
			''' If all process has been commited store all the information '''
			self.killSaveAllInformation(1)
			return
			
		for key in self.pid_dict :
			if not(self.pid_dict[key] == None) :
				if not(self.pid_dict[key].P==None) :
					self.pid_dict[key].timeElapsed+=2 # Increases timestamp of each download process by 2

		while not(self.monitor.empty()) :
			data = self.monitor.get() # Monitor queue that watches allprocess
			data = data.split(':') # Each individual information is seprerated by colon(':')
			if len(data) == 4 :
				if data[1] == 'Done' : # If done then 1 process commited
					self.Commited=self.Commited+1
				else : # Otherwise update information
					for key in self.pid_dict :
						if not(self.pid_dict[key] == None) :
							if not(self.pid_dict[key].P==None) :
								if self.pid_dict[key].P.pid==int(data[0]) :
									self.pid_dict[key].timeElapsed=0 # If any process has reported it means it is working well  (Reduce timestamp to 0 again)
									break

		for key in self.pid_dict :
			''' if any process is not reporting that means it is being idle for a long time '''
			obj=self.pid_dict[key]
			if obj==None :
				pass
			elif obj.timeElapsed >= 40 : # If timestamp >= 40 the process is reconsidered
				while obj.LOCK.value == 1 : # Waits till process reaches a consistent state
					pass
				setF=0
				if obj.mutex.acquire(False) : # Acquire lock
					if  obj.LOCK.value == 2: # If posible to lock then lock it
						obj.LOCK.value=0
						setF=1
					else :
						obj.mutex.release()
				else :
					obj.timeElapsed=0
				if obj.LOCK.value==0 and setF==1: # If process is to be killed	
					fVP=Fork_Download() # New Variable to store process new information
					obj.P.terminate() # terminate old one
					
					obj.P=0
					obj.type = 0
					obj.timeElapsed=0
					
					if obj.initiated.value == 0 : # If process has not been initiated replace it
						obj.type=0
						p = Process(target=fVP.forkVariousPart,args=(obj,self.url,str(self.fileName),self.transmit,self.monitor))
					else : # If process has been initiated append it
						obj.type=1
						p = Process(target=fVP.forkVariousPart,args=(obj,self.url,str(self.fileName),self.transmit,self.monitor))
					p.start()
					obj.P = p
					self.pid_dict[key] = obj
					
					obj.mutex.release()

		''' Kepp track of signals to perform any action '''
		if self.flag.value & 0x0002: # If signal to resume is send
			self.killSaveAllInformation()
			self.flag.value = self.flag.value & 0xfffd
			self.flag.value = self.flag.value | 0x0010 #Resume Confirmation
			return
		if self.flag.value & 0x0004 : # If signal to kill is send
			self.paused=1
			self.killSaveAllInformation(1)
			self.flag.value = self.flag.value & 0xfffb
			self.flag.value = self.flag.value | 0x0008 #Cancel confirmation
			self.paused=0			
			return			
			
		Timer(2,self.Monitor).start()
		
	def getObject(self,i) :
		''' Checks for free started window & transfer it to callee '''
		if len(self.pid_dict) > i :
			if not(self.pid_dict[i]==None) :
				obj=self.pid_dict[i]
				obj.reInit()
				return obj
		return None
			
	def fork(self,url,LL,UL,PARTS,transmit,fileName) :
		''' Gets information & brings the process to life '''
		self.fileName=fileName
		self.netLink=PARTS
		for j in range(PARTS) :			
			fVP = Fork_Download() # Data-Structure to store information
			obj = self.getObject(j)
			if obj==None :
				obj=Fork_Info()
		
			obj.LL=LL[j] # Lower limit
			obj.UL=UL[j] # Upper Limit
			obj.type=0
			p = Process(target=fVP.forkVariousPart,args=(obj,url,str(fileName),transmit,self.monitor))
			p.start() # Start new process	
			obj.P=p
			self.pid_dict[j]=obj
		t = Timer(2,self.Monitor) # Start Monitor to watch process
		t.start()		
	
	def YTubePartition(self,info,recv,PARTS,wMutex,flag,bit) :		
		''' It download if resume is called with download information '''
		if recv == None :
			return
		
		if not(os.path.exists(os.getcwd()+'/Download/'+info.fileName+'_LDM')) :
			''' Checks if file with past download is not present is start-over again '''
			info=self.YTubeDownload(info.url,recv,PARTS,info,wMutex,flag)
			return info[0],info[1],0
		
		if bit == 1:
			''' If url is a youtube url Link is fetched again '''
			headers={'User-Agent':'LINUX DOWNLOAD MANAGER'} # building of header
			req=urllib2.Request(info.url,None,headers)
			proXy={}
			proxy_info=UIXML().getProxyInformation('&LDM')
			try :
				if len(proxy_info) == 2:
					proXy['host']=str(proxy_info[0])
					proXy['port']=int(proxy_info[1])
					proxy="http://%(host)s:%(port)d"%proXy
					info={"http":""}
					info["http"]="http://%(host)s:%(port)d"%proXy
					handler = urllib2.ProxyHandler(info)
					opener=urllib2.build_opener(handler) # Add proxy information
				elif len(proxy_info)==4 :	
					proXy['host']=str(proxy_info[0])
					proXy['port']=int(proxy_info[1])
					proXy['user']=str(proxy_info[2])
					proXy['pass']=str(int(proxy_info[3]))
					proxy="http://%(user)s:%(pass)s@%(host)s:%(port)d"%proXy
					info={"http":""}
					info["http"]="http://%(user)s:%(pass)s@%(host)s:%(port)d"%proXy
					handler = urllib2.ProxyHandler(info)
					opener=urllib2.build_opener(handler)	# Add USER & PASS	
				else :			
					opener = urllib2.build_opener() # build empty handler	
			except Exception,e :
				print "Error ",str(e)
			
			s=opener.open(req).read() # reads html		
			search=re.search(self.regX,s)	
			
			if search:
				url='http'+urllib2.unquote(search.group(1))				
		else :
			url=info.url
			
		''' Sets Initial value of all variables '''
		self.wMutex=wMutex
		self.transmit=recv
		self.info=info
		flag.value=0
		self.flag=flag
		self.url=url
		self.fileName=info.fileName
		
		l=0
		for i in range(len(info.partition)) :
			fVP = Fork_Download()
			obj=self.getObject(i)		
			if obj==None :
				obj = Fork_Info()
						
			obj.LL=info.partition[i][0]
			obj.UL=info.partition[i][1]	
			obj.type=0
			obj.initiated.value=0
			obj.length.value=int(info.partition[i][2])
			self.fileName=info.fileName
			if obj.UL-obj.LL==obj.length.value-1 : # Checks for number of commited process		
				l=l+obj.length.value
				self.Commited=self.Commited+1
			elif obj.UL-obj.LL==obj.length.value and i==len(info.partition)-1 : # Checks for Commited process
				l=l+obj.length.value			
				self.Commited=self.Commited+1
			else : # If process wasn't complete last time , it start over again
				p = Process(target=fVP.forkVariousPart,args=(obj,self.url,str(info.fileName),self.transmit,self.monitor))
				p.start()		
				obj.P=p
			self.pid_dict[i]=obj					
		t = Timer(2,self.Monitor)
		t.start()	
		return None,l,self.Commited
					
	def YTubeDownload(self,url,recv,PARTS,info,wMutex,flag):		
		''' Calls a Youtube download by fetching the link '''
		self.info=info
		if recv == None :
			return
		headers={'User-Agent':'LINUX DOWNLOAD MANAGER'} # build header
		req=urllib2.Request(url,None,headers)
		proXy={}
		proxy_info=UIXML().getProxyInformation('&LDM')
		try :
			if len(proxy_info) == 2:
				proXy['host']=str(proxy_info[0])
				proXy['port']=int(proxy_info[1])
				proxy="http://%(host)s:%(port)d"%proXy
				info={"http":""}
				info["http"]="http://%(host)s:%(port)d"%proXy
				handler = urllib2.ProxyHandler(info)
				opener=urllib2.build_opener(handler) # Add proxy information
			elif len(proxy_info)==4 :	
				proXy['host']=str(proxy_info[0])
				proXy['port']=int(proxy_info[1])
				proXy['user']=str(proxy_info[2])
				proXy['pass']=str(int(proxy_info[3]))
				proxy="http://%(user)s:%(pass)s@%(host)s:%(port)d"%proXy
				info={"http":""}
				info["http"]="http://%(user)s:%(pass)s@%(host)s:%(port)d"%proXy
				handler = urllib2.ProxyHandler(info)
				opener=urllib2.build_opener(handler)	# Add USER & PASS	
			else :			
				opener = urllib2.build_opener() # build empty handler	
		except Exception,e :
			print "Error ",str(e)
			sys.exit(0);

		print "About to fetch page info"		
		s=opener.open(req).read()
		print 'Npes opened the link'	
		search=re.search(self.regX,s)
			
		start = s.find('<title>')
		end = s.find('</title>')			

		fileName = s[start+7:end] # finds filename
		
		fileName=fileName.replace('\n','')
		fileName=fileName.replace('/','')
		fileName=fileName.replace(' ','')				
		fileName=fileName.replace('.','')	
		if search:
			flash_url='http'+urllib2.unquote(search.group(1))
			if len(flash_url) : # After all information has been fetched it start the download from the fetched link
				fileName,length = self.Download(flash_url,recv,PARTS,info,wMutex,flag,fileName)
		return (fileName,length)
			
	def InAscii(self,string) :
		''' Remove non-Ascii character from the string '''
		x=''
		for i in range(len(string)) :
			if (ord(string[i]) >= 65 and ord(string[i]) <= 90) or (ord(string[i]) >= 97 and ord(string[i]) <= 123):
				x=x+string[i]
		if len(x) == 0:
			x='LDM_OUT'
			
		return x
					
	def Download(self,url,recv,PARTS,info,wMutex,flag,fileName='') :
		''' Takes a url fetches it's information & partition it to calls download routine '''
		self.flag=flag # To keep track of signal send to it from GUI
		self.wMutex=wMutex # Synchronize Loading of information & writing of information of a download
		self.transmit=recv # Communication PIPE
		self.url=url # Url or location form where to download
		self.info=info # Have download prtition & information
		
		if len(url)==0 :
			return
			
		if len(fileName)==0 : # If filename not present , read it from the link
			self.aUrl=url
			fileName=url.split('/')
			fileName=fileName[len(fileName)-1]
			
		fileName = self.InAscii(fileName)
		req=urllib2.Request(url,None,{'User-Agent':'LINUX DOWNLOAD MANAGER'}) # build the header
		proXy={}
		proxy_info=UIXML().getProxyInformation('&LDM')
		try :
			if len(proxy_info) == 2:
				proXy['host']=str(proxy_info[0])
				proXy['port']=int(proxy_info[1])
				proxy="http://%(host)s:%(port)d"%proXy
				info={"http":""}
				info["http"]="http://%(host)s:%(port)d"%proXy
				handler = urllib2.ProxyHandler(info)
				opener=urllib2.build_opener(handler) # Add proxy information
			elif len(proxy_info)==4 :	
				proXy['host']=str(proxy_info[0])
				proXy['port']=int(proxy_info[1])
				proXy['user']=str(proxy_info[2])
				proXy['pass']=str(int(proxy_info[3]))
				proxy="http://%(user)s:%(pass)s@%(host)s:%(port)d"%proXy
				info={"http":""}
				info["http"]="http://%(user)s:%(pass)s@%(host)s:%(port)d"%proXy
				handler = urllib2.ProxyHandler(info)
				opener=urllib2.build_opener(handler)	# Add USER & PASS	
			else :			
				opener = urllib2.build_opener() # build empty handler	
		except Exception,e :
			print "Error ",str(e)
			sys.exit(0)

		s=opener.open(req)
		
		''' Read HTTP to get all information '''
		ctype = s.info().get('Content-Type')
		length = int(s.info().get('Content-Length'))				
		
		self.length=length
		i=0
		temp=fileName
		while os.path.isdir(os.getcwd()+'/Download/'+fileName+'_LDM')==True :
			''' Checks for the availibility of location '''
			fileName=temp+'_'+str(i)
			i=i+1
		os.mkdir(os.getcwd()+'/Download/'+fileName+'_LDM')
		self.fileName=fileName
		LL = array.array('I')
		UL = array.array('I')
				
		for i in range(PARTS) : # Partition file to be downloaded
			if not(i==0) :
				L=(i*length/PARTS)+1
			else :
				L=0
			LL.append(L)
			UL.append((i+1)*length/PARTS)
			
		self.fork(url,LL,UL,PARTS,recv,fileName) # calls routine to start downloads
		
		self.info.fileName=self.fileName
		self.info.length=length		
		
		return (fileName,length)