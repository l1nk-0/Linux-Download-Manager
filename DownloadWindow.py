'''**********************************************************************************************************************************
 * LDM :- DownloadWindow.py
 * -Anand Kumar
 * 
 * Build UI for taking information & starting various downloads
 * Description :-
 *             Download_Info :- It stores each individual download information 
 *             DownloadWidget :- Tracks each downloads & displays their progress.
 * 	       DownloadWindow :- Displays various downloads & their status with takes all user input links
***********************************************************************************************************************************'''

import sys,array,thread,os
from multiprocessing import Queue,Process,Value
from PyQt4 import QtGui,QtCore
from Fork_Download import YTube_Download
from dLoadInformation import dLoadInfo,Info

class DownloadInfo :
	''' Contains downloads & their information '''
	def __init__(self) :
		self.index = 0
		self.justDownload = 0
		self.downloadTillNow = 0
		self.timeElapsed = 0
		self.refresh = 0
		self.LL = 0
		self.UL = 0
		
class DownloadWidget(QtGui.QTableWidget) :
	''' it contains Downoads information in a tableView '''
	def __init__(self,parent=None) :
		''' contains download progress + speed + length '''
		QtGui.QTableWidget.__init__(self,parent)
		
		self.removeAllElements()

		self.setColumnCount(3)
		self.setColumnWidth(0,240)
		self.setColumnWidth(1,200)		
		self.setColumnWidth(2,200)				
		
		hitem1 = QtGui.QTableWidgetItem()
		hitem1.setText('Download Progress')
		self.setHorizontalHeaderItem(0,hitem1)
		
		hitem2 = QtGui.QTableWidgetItem()
		hitem2.setText('Instantaneous\nDownload Speed')
		self.setHorizontalHeaderItem(1,hitem2)
		
		hitem1 = QtGui.QTableWidgetItem()
		hitem1.setText('Partition Length')
		self.setHorizontalHeaderItem(2,hitem1)
			
	def removeAllElements(self):
		''' Clears the Widget '''
		self.index=0	
		row = self.rowCount()
		for i in range(row) :			
			self.removeRow(row-i-1)			
			
	def addDownloadProcess(self) :
		''' When a process starts it is added '''
		label = QtGui.QLabel('    0 KBPS');
		pBar = QtGui.QProgressBar()
		
		pBar.setMaximum(100) # To show % download
		
		self.insertRow(self.index)
		self.setCellWidget(self.index,0,pBar)
		self.setCellWidget(self.index,1,label)
		self.setCellWidget(self.index,2,QtGui.QLabel('0 to 0'))
		self.index=self.index+1
		
	def updateTable(self,index,progress,speed,p_len) :
		''' With progress in download table is updated '''
		if progress == 100 :
			speed = 0
		if index < self.index :
			self.cellWidget(index,0).setValue(progress)
			self.cellWidget(index,1).setText('    '+str(speed)+' KBPS')		
			self.cellWidget(index,2).setText('    '+p_len)
			
class DownloadWindow(QtGui.QWidget) :
	''' Main Window which contains download progress information & takes input from user '''
	def __init__(self,PARTS,url='',parent=None) :
		QtGui.QWidget.__init__(self,parent)
		self.PARTS=PARTS # Decides partitions
		self.dFlag = Value('i') # Communicates actions through this shared variable
		self.dFlag.value = 0
		self.setMouseTracking(1)
		self.recv=None
		
		self.pause = QtGui.QPushButton(self)
		self.resume = QtGui.QPushButton(self)
		cancel = QtGui.QPushButton(self)
		
		alwaysOnTop = QtGui.QRadioButton(self)
		minimize = QtGui.QPushButton(self)
		self.hideDL = QtGui.QPushButton(self)
		
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
								
		label = QtGui.QLabel('Downloading from')
		self.urlLabel = QtGui.QLabel(str(url))
		
		self.progressBar = QtGui.QProgressBar()
		self.progressBar.setMaximum(100)
		self.dWidget = DownloadWidget()

		self.Clear()
		
		self.t = QtGui.QLabel('Time Elapsed: 0 sec')
		self.Speed = QtGui.QLabel('Total Speed : 0 sec')
		self.Size = QtGui.QLabel('Downloaded Size: 0 Bytes')
		self.Remaining = QtGui.QLabel('Remaining : 0 Bytes')
				
		self.pause.setText('Pause')
		self.resume.setText('Resume')
		cancel.setText('Cancel')

		self.pause.setEnabled(False)
		self.resume.setEnabled(False)
				
		self.hideDL.setText("Hide Downloads")
		alwaysOnTop.setText("On Top of all")
		minimize.setText("Minimize To Tray")
		
		hbox = QtGui.QHBoxLayout()
		hbox.addWidget(self.pause)
		hbox.addWidget(self.resume)
		hbox.addWidget(cancel)

		hbox1 = QtGui.QHBoxLayout()
		hbox1.addWidget(alwaysOnTop)			
		hbox1.addWidget(self.hideDL)
		hbox1.addWidget(minimize)	

		vbox = QtGui.QVBoxLayout()
		vbox.addWidget(label)
		vbox.addWidget(self.urlLabel)
		vbox.addWidget(self.t)
		vbox.addWidget(self.Speed)
		vbox.addWidget(self.Size)
		vbox.addWidget(self.Remaining)		
		vbox.addWidget(self.progressBar)
		vbox.addLayout(hbox1)
		vbox.addWidget(self.dWidget)
		vbox.addLayout(hbox)

		self.setLayout(vbox)
		
		self.timer = QtCore.QTimer()
		
		self.connect(self.timer,QtCore.SIGNAL('timeout()'),self.UpdateInterface)
		self.connect(self.hideDL,QtCore.SIGNAL('clicked()'),self.hideDownloads)
		self.connect(self.pause,QtCore.SIGNAL('clicked()'),self.pauseDownload)
		self.connect(self.resume,QtCore.SIGNAL('clicked()'),self.resumeDownload)
		self.connect(cancel,QtCore.SIGNAL('clicked()'),self.cancelDownload)
		self.connect(alwaysOnTop,QtCore.SIGNAL('toggled(bool)'),self.putOnTop)		
		self.connect(minimize,QtCore.SIGNAL('clicked()'),self.minimizeToTray)

	def Clear(self) :
		''' Reinitialize the widget to reuse '''
		self.Increase = 1
		self.posMove=None
		self.flag=None
		self.T=0
		self.outFile='LDM_IIITA_DEVELOPMENT'
		self.done = 0
		self.dInfo = {}
		self.dFile={}
		self.totalTime = 0
		self.dLength = 0
		self.downloader = YTube_Download(12)
		self.progressBar.setValue(0)
		self.dWidget.removeAllElements()

	def minimizeToTray(self) :
		''' When widget is to be minimize it's information is added to the MainFrame Window which is informaed by setting a bit '''
		if not(self.packet == None) :
			self.packet.flag=self.packet.flag | 0x0001
			self.hide()
		
	def putOnTop(self,bool) :
		if bool :
			self.setWindowFlags(QtCore.Qt.Widget | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
			self.show()
		else :
			self.setWindowFlags(QtCore.Qt.Widget | QtCore.Qt.FramelessWindowHint)
			self.show()
			
	def hideDownloads(self) :
		if self.Increase == 1:
			self.Increase = 0
			self.resize(700,225)
			self.hideDL.setText("Show Downloads")
		else :
			self.Increase = 1
			if self.dWidget.index > 1:
				self.resize(700,225+(self.dWidget.index-1)*32)			
			self.hideDL.setText("Hide Downloads")					
		
	def pauseDownload(self) :
		self.dFlag.value  =self.dFlag.value | 0x0002
		self.pause.setEnabled(False)

	def resumeDownload(self) :
		if self.dFlag.value & 0x0010 :
			self.downloader.resume()
			self.pause.setEnabled(True)
			self.resume.setEnabled(False)
			self.dFlag.value = self.dFlag.value & 0xffef
	
	def cancelDownload(self) :
		if self.downloader.paused==0 :
			self.dFlag.value = self.dFlag.value | 0x0004
		else :
			if self.isHidden() :
				self.show()
			ok = QtGui.QMessageBox(QtGui.QMessageBox.Warning,'',"You can't cancel while pause",QtGui.QMessageBox.Ok,self, QtCore.Qt.FramelessWindowHint)
			ok.exec_()
		
	def keyPressEvent(self,event) :
		if event.key() == QtCore.Qt.Key_Escape :
			self.hide()
			
	def mousePressEvent(self,event) :
		self.posMove = event.pos()
	
	def mouseMoveEvent(self,event) :
		if self.posMove :
			self.move(self.pos().x()+event.pos().x()-self.posMove.x(),self.pos().y()+event.pos().y()-self.posMove.y())
	
	def mouseReleaseEvent(self,event) :
		self.posMove=None
		
	def getPartDownload(self,obj,packet,wMutex,bit) :
		''' When a download to be resumes it's partial information is fetched & download is resumed '''
		self.wMutex=wMutex
		self.packet=packet
		self.urlLabel.setText(str(obj.url)[0:80])
		self.recv = Queue()
		self.setWindowTitle(str(obj.url))
		
		self.outFile=obj.fileName
		self.dLength=int(obj.length)
		info = Info()
		info.url=obj.url
		info.fileName=obj.fileName
		info.date=obj.date
		info.time=obj.time
		info.length=obj.length
		
		obj=dLoadInfo().getSpecificInformation(obj)
		if obj==None :
			raise urllib2.URLError
			
		info.partition=obj.partition
		for i in range(len(info.partition)) :
			self.dFile[obj.partition[i][0]]=None
			
		if obj == None :
			return 0
		else :
			if bit==1 :
				fName,length,cmtd=self.downloader.YTubePartition(info,self.recv,self.PARTS,wMutex,self.dFlag,bit)
				self.PARTS=self.PARTS-cmtd
				if fName==None  :
					self.dLength=int(obj.length)-length		
					self.timer.start(1000)
					return 1
				else :
					self.packet.fileName=fName
					self.packet.length=length
					self.dLength=length
					self.fileName=fName
					self.outFile = fName
					self.dLength=length
					self.timer.start(1000)
					return 2
		self.timer.start(1000)
		return 1
			
	def getDownload(self,url,packet,wMutex,bit=0) :
		self.wMutex=wMutex
		self.packet = packet
		self.urlLabel.setText(str(url)[0:80])
		self.recv = Queue()
		self.setWindowTitle(url)
		info = Info()
		info.url=url			
		info.date=self.packet.dt
		info.time=self.packet.tm
		if bit == 0 :
			self.outFile,self.dLength = self.downloader.YTubeDownload(url,self.recv,self.PARTS,info,wMutex,self.dFlag)
		else :
			self.outFile,self.dLength = self.downloader.Download(url,self.recv,self.PARTS,info,wMutex,self.dFlag)
			
		info.fileName=str(self.outFile)
		info.length=self.dLength
		self.info=info		
		
		self.Remaining.setText('Remaining : '+str(self.dLength)+' Bytes')
		self.timer.start(1000)
		return self.outFile,self.dLength

	def getTime(self,t) :	
		z=''
		if t/60 > 0 :
			z=str(t/60)+'min '+str(t%60)+'sec'
		else :
			z=str(t)+'sec'
		return z
		
	def updateInfo(self,t,speed,size,remaining) :
		self.t.setText('Time Elapsed: '+self.getTime(t))
		if speed/1024 > 0 :
			self.Speed.setText('Avg. Speed : '+str(speed/1024)+' MBPS')
		else :
			self.Speed.setText('Avg. Speed : '+str(speed)+' KBPS')
		self.Size.setText('Downloaded Size: '+str(size)+' Bytes')
		self.Remaining.setText('Remaining : '+str(remaining)+' Bytes')
		
	def Watch(self) :
		''' continously monitors the flags bits & checks if any signal is send & performs corresponding actions '''
		if self.packet.flag & 0x0080 :
			self.cancelDownload()
		if self.packet.flag & 0x0001 :
			if self.isVisible() :
				self.hide()
			self.packet.flag=self.packet.flag & 0xfffe
		if self.packet.flag & 0x0010 :
			if self.isHidden() :
				self.show()
			self.packet.flag=self.packet.flag & 0xffef
				
		if self.dFlag.value & 0x0010 :
			self.resume.setEnabled(True)
		if self.dFlag.value & 0x0008 :
			self.packet.flag=self.packet.flag | 0x0002
			ok = QtGui.QMessageBox(QtGui.QMessageBox.Information,'Cancel',"Download canceled",QtGui.QMessageBox.Ok,self,QtCore.Qt.FramelessWindowHint)
			ok.exec_()
			self.dFlag.value = self.dFlag.value & 0xfff7
		if self.dFlag.value & 0x0100 :
			self.timer.stop()
			ok = QtGui.QMessageBox(QtGui.QMessageBox.Information,'Info..',"Download complete",QtGui.QMessageBox.Ok,self,QtCore.Qt.FramelessWindowHint)
			ok.exec_()
			self.dFlag.value=self.dFlag.value & 0xfeff
			self.packet.flag = self.packet.flag | 0x0002			
			
	def UpdateInterface(self) :
		''' If data is fetched progress bar & other information is updated '''
		self.totalTime=self.totalTime+1
		total=0
		length=0

		for key in self.dInfo :
			obj=self.dInfo[key]
			obj.timeElapsed=obj.timeElapsed+1
			total+=obj.downloadTillNow
			length+=obj.justDownload
			if obj.refresh == 1 :
				self.dWidget.updateTable(obj.index,(100*obj.downloadTillNow)/(obj.UL-obj.LL),obj.justDownload/(1024*obj.timeElapsed),str(self.dInfo[key].LL)+' to '+str(self.dInfo[key].UL))
				obj.timeElapsed = 0
				obj.refresh = 0
			obj.justDownload=0			
		if total == 0:
			self.packet.timeLeft='inf'
		else :
			self.packet.timeLeft=str((self.dLength-total)*self.totalTime/total)
		self.packet.downloaded=total
		
		if self.dLength > 0:
			self.progressBar.setValue((100*total)/self.dLength)
		self.updateInfo(self.totalTime,length/1024,total,self.dLength-total)
		self.Tracker()
		if not(self.done==1) :
			self.timer.start(1000)
		else :
			self.timer.stop()
		self.Watch()
		
	def Tracker(self) :
		'''Monitors the progress of download from this function '''
		length = 0
		i=0
		if not(self.T==self.PARTS) :
			while not(self.recv.empty()) and i <= 20 :
				data = self.recv.get()
				if not(data == None) :
					data=data.split(':')
					if data[0] == 'Init' : # If initialize add entry to the download window
						self.pause.setEnabled(True)
						obj = DownloadInfo()
						obj.index = self.dWidget.index
						obj.LL = int(data[1])
						obj.UL = int(data[2])
						self.dInfo[int(data[1])]=obj
						self.dWidget.addDownloadProcess()
						if self.dWidget.index > 1 and self.Increase :
							self.resize(700,225+(self.dWidget.index-1)*32)
					elif data[0] == 'Done': # if done download increase commited process number
						self.T=self.T+1
					else : # else just add entry to process it by other functions
						obj = self.dInfo[int(data[1])]
						obj.justDownload += int(data[0])-obj.downloadTillNow
						length+=int(data[0])-obj.downloadTillNow						
						obj.downloadTillNow = int(data[0])			
						obj.refresh = 1
					i=i+1					
					
		else : # if all downloads complete check if file avail & createfinaloutput
			ok=QtGui.QMessageBox.information(self,'Hello User',"Download Complete")
			if len(self.dFile) > 0 :
				thread.start_new_thread(self.createFinalOutput,(self.dFile,self.outFile))
			else :
				thread.start_new_thread(self.createFinalOutput,(self.dInfo,self.outFile))
			self.done = 1
			self.packet.free=1
			if self.isHidden() :
				self.show()
			
	def createFinalOutput(self,dI,fileName) :
		''' it reads the given sufficient input & builds the final output file at the destination '''
		key=[]
		for k in dI :
			key.append(k)
		key.sort()


		outFile=fileName
		temp=fileName
		i=0
		try :
			if os.path.exists(self.packet.dLocation) :
				while os.path.exists(self.packet.dLocation+'/'+outFile) :
					outFile=temp+'_'+str(i)
					i=i+1
			f = open(self.packet.dLocation+'/'+outFile,'wb')
		except IOError :
			f = open(self.packet.dLocation+'/'+outFile,'w')
			f.close()
			f = open(self.packet.dLocation+'/'+outFile,'wb')
	
		for k in key :
			f1=open(os.getcwd()+'/Download/'+fileName+'_LDM'+'/'+'LDM_'+str(k))
			data = f1.read()
			f.write(data)
			f1.close()
			os.remove(os.getcwd()+'/Download/'+fileName+'_LDM'+'/'+'LDM_'+str(k))
		
		os.rmdir(os.getcwd()+'/Download/'+fileName+'_LDM')
		f.close()	
		self.dFile={}

		self.packet.flag = self.packet.flag | 0x0004 # update the flag information to say that download complete
