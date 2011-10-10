'''**********************************************************************************************************************************
 * LDM :- TabWidget.py
 * -Anand Kumar
 * 
 * It contains the central part of the MainFrame & displays abstract download information
 * Description :-
 *		TabWidget :- A Widget to store download information. It gets all information from MainFrame 7 updates 
 *			     it's information . it also fills it's collumn from dLoadInformation.
***********************************************************************************************************************************'''

import sys
from PyQt4 import QtGui,QtCore
from dLoadInformation import Info,dLoadInfo

class TabWidget(QtGui.QTableWidget) :
	def __init__(self,wMutex,parent=None) :
		QtGui.QTabWidget.__init__(self,parent)
		self.parent = parent
		self.wMutex=wMutex
		
		self.dLI = dLoadInfo()
		
		self.setColumnCount(8)
		
		self.setColumnWidth(0,100)
		self.setColumnWidth(1,60)
		self.setColumnWidth(2,60)
		self.setColumnWidth(3,90)
		self.setColumnWidth(4,100)
		self.setColumnWidth(5,100)
		self.setColumnWidth(6,30)
		self.setColumnWidth(7,44)	
		
		self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)	
		
		hitem = QtGui.QTableWidgetItem()
		hitem.setText('File Name')
		self.setHorizontalHeaderItem(0,hitem)
		hitem = QtGui.QTableWidgetItem()
		hitem.setText('Length')
		self.setHorizontalHeaderItem(1,hitem)
		hitem = QtGui.QTableWidgetItem()
		hitem.setText('Loaded')
		self.setHorizontalHeaderItem(2,hitem)
		hitem = QtGui.QTableWidgetItem()
		hitem.setText('Time Left')
		self.setHorizontalHeaderItem(3,hitem)								
		hitem = QtGui.QTableWidgetItem()
		hitem.setText('Access Date')
		self.setHorizontalHeaderItem(4,hitem)
		hitem = QtGui.QTableWidgetItem()
		hitem.setText('Access Time')
		self.setHorizontalHeaderItem(5,hitem)
		hitem = QtGui.QTableWidgetItem()
		hitem.setText('X')
		self.setHorizontalHeaderItem(6,hitem)
		hitem = QtGui.QTableWidgetItem()
		hitem.setText('Y')
		self.setHorizontalHeaderItem(7,hitem)

		self.LoadInfo()
		self.connect(self,QtCore.SIGNAL('cellClicked(int,int)'),self.slotSectionClicked)
		
	def dumpRow(self,row) :
		obj=Info()
		obj.url=str(self.cellWidget(row,0).toolTip())
		obj.fileName=str(self.cellWidget(row,0).text())
		obj.date = str(self.cellWidget(row,4).text())		
		obj.time = str(self.cellWidget(row,5).text())
		
		self.wMutex.acquire(True)
		stat=self.dLI.DeleteNode(obj)		
		self.wMutex.release()
		self.removeRow(row)
		
	def slotSectionClicked(self,x,y) :
		if y==7 :
			data=self.cellWidget(x,2).toolTip()						
			if str(self.cellWidget(x,3).toolTip())=='Active' :
				msg=QtGui.QMessageBox(QtGui.QMessageBox.Warning,'!!',"Oops this thread is currently Downloading first kill the download",QtGui.QMessageBox.Yes,self,QtCore.Qt.FramelessWindowHint)
				ok=msg.exec_()
				return
			
			if int(data)==100 :
				msg=QtGui.QMessageBox(QtGui.QMessageBox.Question,'!!',"This finally has been compleatlty downloaded.Would you like to redownload it ?",QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,self,QtCore.Qt.FramelessWindowHint)
				ok=msg.exec_()
				if ok == QtGui.QMessageBox.Yes :
					url=str(self.cellWidget(x,0).toolTip())
					if url.startswith('http://www.youtube.com') or url.startswith('https://www.youtube.com') :
						self.parent.fetchAndSaveUrl(url,0)
					else :
						self.parent.fetchAndSaveUrl(url)
			else :
				msg=QtGui.QMessageBox(QtGui.QMessageBox.Question,'!!',"Restarting Download", QtGui.QMessageBox.Yes,self, QtCore.Qt.FramelessWindowHint)
				ok=msg.exec_()	
				self.parent.downloadPartition(str(self.cellWidget(x,0).toolTip()),str(self.cellWidget(x,0).text()), str(self.cellWidget(x,4).text()),str(self.cellWidget(x,5).text()),str(self.cellWidget(x,1).toolTip()))
		elif y==6 :
			if str(self.cellWidget(x,3).toolTip())=='Active' :
				msg=QtGui.QMessageBox(QtGui.QMessageBox.Warning,'!!',"Oops this thread is currently Downloading first kill the download",QtGui.QMessageBox.Yes,self,QtCore.Qt.FramelessWindowHint)
				ok=msg.exec_()
				return		
			data=self.cellWidget(x,2).toolTip()		
			if not(int(data)==100) :
				msg=QtGui.QMessageBox(QtGui.QMessageBox.Question,'!!',"This finally hasn't been compleatlty downloaded.Would you still like to delete this entry ?",QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,self,QtCore.Qt.FramelessWindowHint)
				ok=msg.exec_()
				if ok == QtGui.QMessageBox.Yes :
					self.dumpRow(x)	
			else :
				self.dumpRow(x)
				
	def inMB(self,data) :		
		sze='B'
		data=int(data)
		if data/1024 > 0:
			data=data/1024
			sze='KB'
		if data/1024 > 0 :		
			data=data/1024
			sze='MB'
		return str(data)+sze		
		
	def getLabel(self,info,toolTip='') :
		lbl = QtGui.QLabel(self)
		lbl.setText(str(info))
		if len(toolTip) > 0:
			lbl.setToolTip(toolTip)
		return lbl
		
	def getIconLabel(self,src,toolTip) :
		lbl=QtGui.QLabel(self)
		lbl.setPixmap(QtGui.QPixmap(src))
		lbl.setToolTip(toolTip)
		return lbl
		
	def InsertData(self,obj,status='InActive') :
		if obj == None :
			return
		row = self.rowCount()

		self.insertRow(row)
		self.setRowHeight(row,25)
		self.setCellWidget(row,0,self.getLabel(obj.fileName,obj.url))
		self.setCellWidget(row,1,self.getLabel(self.inMB(obj.length),str(obj.length)))			
		dL=0
		for i in range(len(obj.partition)) :
			dL+=int(obj.partition[i][2])
			
                if int(obj.length) == 0 :
			self.setCellWidget(row,2,self.getLabel(str(0)+'%',str(0)))
		else :
			self.setCellWidget(row,2,self.getLabel(str((100*dL)/int(obj.length))+'%',str(100*dL/int(obj.length))))
		self.setCellWidget(row,3,self.getLabel(' - ',status))
		self.setCellWidget(row,4,self.getLabel(obj.date,str(obj.date)))				
		self.setCellWidget(row,5,self.getLabel(obj.time,str(obj.time)))
		self.setCellWidget(row,6,self.getIconLabel('image/close.png','Remove this entry'))
		self.setCellWidget(row,7,self.getIconLabel('image/DLoad.png','Click to Redownload'))
		self.setCurrentCell(row,0)	
		
	def matches(self,obj,row) :
		if self.cellWidget(row,0)==None :
			return False
		if self.cellWidget(row,4)==None :
			return False
		if self.cellWidget(row,5)==None :
			return False
			
		if not(obj.url==str(self.cellWidget(row,0).toolTip())) :
			return False		
		if not(obj.fileName==str(self.cellWidget(row,0).text())) :
			return False
		if not(obj.date == str(self.cellWidget(row,4).text())) :
			return False
		if not(obj.time == str(self.cellWidget(row,5).text())) :
			return False
		return True
		
	def getTime(self,t) :	
		z=t
		try :
			x=int(t)
			if x/60 > 0 :
				z=str(x/60)+'min'+str(x%60)+'sec'
			else :
				z=z+'sec'
		except :
			z='inf'
		return z
				
	def updateEntry(self,obj,total,timeLeft,c=0) :
		for i in range(self.rowCount()) :
			if self.matches(obj,i) :
				self.cellWidget(i,2).setText(str(100*total/int(obj.length))+'%')
				self.cellWidget(i,3).setText(self.getTime(timeLeft))
				if c==1:
					self.cellWidget(i,3).setToolTip('InActive')
				return
	def LoadInfo(self) :
		data = self.dLI.getInformation()
		for key in data :
			obj = data[key]
			self.InsertData(obj)	
			
	def makeEntry(self,obj) :
		x=0
		for i in range(self.rowCount()):
			if self.matches(obj,i) :
				x=1
				break
		if x==0:
			self.InsertData(obj,'Active')		
			
class Widget(QtGui.QWidget) :
	def __init__(self,parent=None) :
		QtGui.QWidget.__init__(self,parent)
		wid=TabWidget(self)
		wid.setGeometry(0,0,700,250)
