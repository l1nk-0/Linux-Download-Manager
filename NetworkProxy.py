import sys,os,datetime,time
from PyQt4 import QtGui,QtCore,QtNetwork
from PyQt4.QtWebKit import *
from PyQt4.QtNetwork import *
from UIXML import UIXML

class NetworkProxy(QtGui.QWidget) :
	def __init__(self,parent=None,loc=None,user=None) :
		QtGui.QWidget.__init__(self,parent)	
		self.setWindowTitle('Network Configuration')	
		self.username = user
		self.authenticated = 1
		self.posMove=None	
		
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
								
		self.uixml = UIXML(os.getcwd())
		okay = QtGui.QPushButton('Ok')
		cancel = QtGui.QPushButton('Cancel')
		
		hbox3 = QtGui.QHBoxLayout()		hbox3.addWidget(okay)
		hbox3.addWidget(cancel)
		
		lhttp = QtGui.QLabel('HTTPProxy: ')
		lport = QtGui.QLabel('Port: ')
		self.http = QtGui.QLineEdit()
		self.port = QtGui.QLineEdit()
		
		hbox1 = QtGui.QHBoxLayout()
		hbox1.addWidget(lhttp)
		hbox1.addWidget(self.http)
		hbox1.addWidget(lport)
		hbox1.addWidget(self.port)
		
		self.cbox = QtGui.QCheckBox('No Authentication')
		
		userl = QtGui.QLabel('Username: ')
		passwrdl = QtGui.QLabel('Password: ')
		self.user = QtGui.QLineEdit()
		self.passwrd = QtGui.QLineEdit()
		self.passwrd.setEchoMode(2)
		
		hbox2 = QtGui.QHBoxLayout()
		hbox2.addWidget(userl)
		hbox2.addWidget(self.user)
		hbox2.addWidget(passwrdl)
		hbox2.addWidget(self.passwrd)
		
		vbox = QtGui.QVBoxLayout()
		vbox.addLayout(hbox1)
		vbox.addWidget(self.cbox)
		vbox.addLayout(hbox2)
		vbox.addLayout(hbox3)
		
		self.setLayout(vbox)				
		self.setUsername(self.username)
			
		self.setWindowTitle('Network Proxy')
		self.connect(self.cbox,QtCore.SIGNAL('stateChanged(int)'),self.Authenticate)
		self.connect(okay,QtCore.SIGNAL('clicked()'),self.Finalize)
		self.connect(cancel,QtCore.SIGNAL('clicked()'),self,QtCore.SLOT('close()'))
	
	def mousePressEvent(self,event) :
		self.posMove = event.pos()
	
	def mouseMoveEvent(self,event) :
		if self.posMove :
			self.move(self.pos().x()+event.pos().x()-self.posMove.x(),self.pos().y()+event.pos().y()-self.posMove.y())
	
	def mouseReleaseEvent(self,event) :
		self.posMove=None
			
	def getInformation(self) :
		l=[]
		if not(len(str(self.http.text()))) or not(len(str(self.port.text()))) :			
			return []
		l.append(str(self.http.text()))
		l.append(str(self.port.text()))
		if len(str(self.user.text())) and len(str(self.passwrd.text())) :				
			l.append(str(self.user.text()))
			l.append(str(self.passwrd.text()))
		
		return l
		
	def setUsername(self,user) :
		self.username = user
		l=self.uixml.getProxyInformation(self.username)
		if len(l)==2:
			self.http.setText(str(l[0]))
			self.port.setText(str(l[1]))
		elif len(l) == 4:
			self.user.setText(str(l[2]))
			self.passwrd.setText(str(l[3]))
		else :
			self.cbox.setChecked(1)
			self.authenticated=0
			self.user.setReadOnly(1)
			self.passwrd.setReadOnly(1)
			
	def Authenticate(self,state) :		
		if state == 2:
			self.authenticated = 0
			self.user.setReadOnly(True)
			self.passwrd.setReadOnly(True)
		else :
			self.authenticated = 1
			self.user.setReadOnly(False)
			self.passwrd.setReadOnly(False)
		
	def Finalize(self) :		
		l=[]
		if not(len(str(self.http.text()))) or not(len(str(self.port.text()))) :
			QtGui.QMessageBox.information(self,'Warning','http/port field is empty')
			return				
		
		l.append(str(self.http.text()))
		l.append(str(self.port.text()))
				
		if self.authenticated :
			if not(len(str(self.user.text()))) or not(len(str(self.passwrd.text()))) :
				QtGui.QMessageBox.information(self,'Warning','login/passwrd field is empty')
				return
			else :
				l.append(str(self.user.text()))
				l.append(str(self.passwrd.text()))	
			
		if self.uixml.setProxyInformation(self.username,l):
			QtGui.QMessageBox.information(self,'Okay','Done Successfully')
		self.close()
