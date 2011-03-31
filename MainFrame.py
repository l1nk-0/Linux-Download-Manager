'''**********************************************************************************************************************************
 * LDM :- LinuxDM.py
 * -Anand Kumar
 * 
 * The Central Widget that manages all activity & incorporates different modules to let &Linux Download Manager Work.
 * Description :-
 *	        Action :- A hybrid action class that tells which download process is clicked
 *		menu :-  Maintains the list of various downloads in Menu list.
 *		MainFrame :- Widget that takes all user input & performs action.
***********************************************************************************************************************************'''

import sys,os,thread
from multiprocessing import Lock
from PyQt4 import QtGui,QtCore
from NetworkProxy import NetworkProxy
from Interface import Interface
from TabWidget import TabWidget		

class Action(QtGui.QAction) :
	__pyqtSignal=("triggeredIndex(int)")
	def __init__(self,index,txt,parent=None) :
		self.index=index
		QtGui.QAction.__init__(self,parent)
		self.setText(txt)
		self.connect(self,QtCore.SIGNAL('triggered()'),self.indexClicked)
		self.connect(self,QtCore.SIGNAL("triggeredIndex(int)"),parent.runingWin);
		
	def indexClicked(self) :
		self.emit(QtCore.SIGNAL("triggeredIndex(int)"),self.index)
		
class Menu(QtGui.QMenu) :
	def __init__(self,title,parent=None) :
		QtGui.QMenu.__init__(self,parent)
		self.setTitle(title)
		
	def delAction(self,index) :
		allAction = self.actions()
		for act in allAction :
			if act.index == index :
				self.removeAction(act)
	
	def pushAction(self,index,txt,parent) :
		parent.action = Action(index,txt,parent)
		self.addAction(parent.action)
			
class MainFrame(QtGui.QWidget) :
	def __init__(self,parent=None) :
		self.wMutex = Lock()
		QtGui.QWidget.__init__(self,parent)
		self.setWindowTitle('&Linux Download Manager')		
		p=QtGui.QPixmap(os.getcwd()+'/image/close.png')	
		
		self.goTerminate=0

		self.PARTS=10
		self.timer = QtCore.QTimer()
		self.links=0
		self.trayIcon = QtGui.QSystemTrayIcon(self)		
		
		self.dLocation = '/home'
		loc=''		
		if os.path.exists(os.getcwd()+'/Locale/desF') :
			f=open(os.getcwd()+'/Locale/desF','r')
			loc=f.read()
			f.close()
		if len(loc) > 0:
			if os.path.exists(loc) :
				self.dLocation=loc
				
		self.dLoads = {}
		self.posMove = None
		self.setMouseTracking(1)
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		
		ldmLbl = QtGui.QLabel(self)
		
		cBox = QtGui.QComboBox(self)
		cBox.setToolTip('Fuzzy Partitioning')
		cBox.addItem('Partition')
		cBox.addItem('No Part 1')
		cBox.addItem('Few 5')
		cBox.addItem('Some 10')	
		cBox.addItem('More 15')					
		cBox.addItem('SuperSonic 20')
		
		cBox.setFrame(True)
		
		self.menuBtn = QtGui.QPushButton(self)
		minimize = QtGui.QPushButton(self)
		close = QtGui.QPushButton(self)
		YDldr = QtGui.QPushButton(self)
		ODldr = QtGui.QPushButton(self)
		Grbr = QtGui.QPushButton(self)
		credit = QtGui.QPushButton(self)
		
		self.pref = NetworkProxy(None,os.getcwd(),'&LDM')
		self.tabWidget = TabWidget(self.wMutex,self)
		
		self.createMenu()
		self.addTrayIcon()
				
		credit.setText('Credit')
		ldmLbl.setText('& Linux Download Manager')
		
		YDldr.setStyleSheet('background-image:url('+os.getcwd()+'/image/Ytdlr.png);border-width:2px;')				
		ODldr.setStyleSheet('background-image:url('+os.getcwd()+'/image/ODld.png);border-width:2px;')
		Grbr.setStyleSheet('background-image:url('+os.getcwd()+'/image/Grabber.png);border-width:2px;')						
		ldmLbl.setStyleSheet('font-size:25px;font-family:lucida calligraphy;color:grey;')
		minimize.setStyleSheet('background-image:url('+os.getcwd()+'/image/minimize.png);border-width:2px;')
		close.setStyleSheet('background-image:url('+os.getcwd()+'/image/close.png);border-width:2px;')
			
		
		ldmLbl.setGeometry(250,10,400,30)
		self.menuBtn.setGeometry(20,20,30,20)
		cBox.setGeometry(10,45,100,20)
		minimize.setGeometry(675,0,35,22)
		close.setGeometry(710,0,35,22)
		YDldr.setGeometry(10,70,100,90)
		ODldr.setGeometry(10,160,100,90)						
		Grbr.setGeometry(10,250,100,90)		
		credit.setGeometry(10,360,100,30)
		
		self.tabWidget.setGeometry(120,40,620,350)

		self.resize(760,400)
		self.trayIcon.show()
		
		self.connect(cBox,QtCore.SIGNAL('activated(int)'),self.sayIndex)
		self.connect(close,QtCore.SIGNAL('clicked()'),self.goToTray)
		self.connect(credit,QtCore.SIGNAL('clicked()'),self.creditMsg)
		self.connect(minimize,QtCore.SIGNAL('clicked()'),self.showMinimized)
		self.connect(Grbr,QtCore.SIGNAL('clicked()'),self.runSiteGrabber)
		self.connect(YDldr,QtCore.SIGNAL('clicked()'),self.YoutubeLinkDownload)
		self.connect(ODldr,QtCore.SIGNAL('clicked()'),self.fetchAndSaveUrl)
		self.connect(self.timer,QtCore.SIGNAL('timeout()'),self.regulateDownload)
		self.timer.start(2000)
		
	def sayIndex(self,index) :
		if index == 1:
			self.PARTS=1
		elif not(index==0) :
			self.PARTS=5*(index-1)
		
	def runingWin(self,index) :
		if not(self.dLoads[index] == None) :
			self.dLoads[index].flag=self.dLoads[index].flag | 0x0010
			
	def regulateDownload(self) :
		for key in self.dLoads :
			flag = self.dLoads[key].flag
			if not(self.dLoads[key].free) :
				self.tabWidget.updateEntry(self.dLoads[key].getInfo(),self.dLoads[key].downloaded,self.dLoads[key].timeLeft)
			if flag & 0x0002 :
				self.dLoads[key].free=0
				self.dLoads[key].flag=flag & 0xfffd
				self.dLoads[key].free=1
				self.dLoads[key].obj.hide()
				self.downloads.delAction(key)
				self.tabWidget.updateEntry(self.dLoads[key].getInfo(),self.dLoads[key].downloaded,'0',1)
			if flag & 0x0008 :
				self.dLoads[key].obj.show()
				self.downloads.pushAction(key,self.dLoads[key].fileName,self)
				self.dLoads[key].flag = flag & 0xfff7
				self.tabWidget.makeEntry(self.dLoads[key].getInfo())
			if flag & 0x0100 :
				self.downloads.pushAction(key,self.dLoads[key].fileName,self)						
				self.dLoads[key].obj.show()
				self.dLoads[key].flag = flag & 0xfeff
				
			if flag & 0x0004 :
				self.dLoads[key].free=0
				self.dLoads[key].obj.hide()
				self.dLoads[key].flags = flag & 0xfffb
				self.dLoads[key].free=1
				self.downloads.delAction(key)
				self.tabWidget.updateEntry(self.dLoads[key].getInfo(),int(self.dLoads[key].length),'0',1)
				self.dLoads[key].flag = flag & 0xfffb
				
			if flag & 0x0040 :
				self.dLoads[key].free=1
				self.dLoads[key].clear()
				self.downloads.delAction(key)
				ok = QtGui.QMessageBox(QtGui.QMessageBox.Information,'Oops',"Fatal Error In Download",QtGui.QMessageBox.Ok,self,QtCore.Qt.FramelessWindowHint)
				ok.exec_()
				self.dLoads[key].flag = flag & 0xffbf
						
		if self.goTerminate == 1:
			if self.freeKey()==-1:
				sys.exit(0)		
		self.timer.start(2000)
		
	def runSiteGrabber(self) :
		ok = QtGui.QMessageBox(QtGui.QMessageBox.Information,'Site Grabber',"Sorry This facility is currently unavilable .  You may contribute for it.",QtGui.QMessageBox.Ok,self,QtCore.Qt.FramelessWindowHint)
		ok.show()		
		
	def freeKey(self) :
		for key in self.dLoads :
			if self.dLoads[key].free == 1 :
				return key
		return -1
		
	def loadPartition(self,url) :
		pass
		
	def YoutubeLinkDownload(self) :
		txt,ok=QtGui.QInputDialog.getText(self,'YouTube Link','YTube Link:', QtGui.QLineEdit.Normal,'', QtCore.Qt.FramelessWindowHint )
		if ok==True :
			if txt.startsWith('https://www.youtube.com') :
				key = self.freeKey()
				if key == -1 :
					obj = Interface(self.PARTS)
				else :
					obj = self.dLoads[key]
					obj.PARTS=self.PARTS					
					obj.clear()
					del self.dLoads[key]
					
				thread.start_new_thread(obj.start_Download,(txt,self.wMutex))
				self.dLoads[self.links]=obj
				self.links=self.links+1
			else :
				msg = QtGui.QMessageBox(QtGui.QMessageBox.Warning,'Oops.',"Not a valid YTube Url ",QtGui.QMessageBox.Ok, self,QtCore.Qt.FramelessWindowHint)
				msg.show()

	def downloadPartition(self,url,fileName,dt,tm,length) :
		key = self.freeKey()
		if key == -1:
			obj=Interface(self.PARTS)
			key=self.links
			self.links=self.links+1
		else :
			obj=self.dLoads[key]
			obj.PARTS=self.PARTS			
			obj.clear()
			del self.dLoads[key]
		obj.url=url
		obj.fileName=fileName
		obj.dt=dt
		obj.tm=tm
		obj.length=length
		bit=0
		if url.startswith('http://www.youtube.com') :
			bit=1		
		thread.start_new_thread(obj.start_from_Part,(self.wMutex,bit))
		self.dLoads[key]=obj
		
	def fetchAndSaveUrl(self,url='',bit=1) :
		ok=True
		if len(url)==0 :
			url,ok=QtGui.QInputDialog.getText(self,'Link','Download Link:', QtGui.QLineEdit.Normal,'', QtCore.Qt.FramelessWindowHint)
		if ok==True :
			key = self.freeKey()
			if key == -1 :
				obj = Interface(self.PARTS)
				key=self.links			
				self.links=self.links+1
			else :
				obj = self.dLoads[key]
				obj.PARTS=self.PARTS				
				obj.clear()
				del self.dLoads[key]
				
			thread.start_new_thread(obj.start_Download,(url,self.wMutex,bit))
			self.dLoads[key]=obj
		else :
			msg = QtGui.QMessageBox(QtGui.QMessageBox.Warning,'Oops.',"Not a valid Url ",QtGui.QMessageBox.Ok,self, QtCore.Qt.FramelessWindowHint)
			msg.show()
				
	def createMenu(self) :
		menu = QtGui.QMenu(self)
		
		self.downloads = Menu("Downloads",self)
		miniToTray = QtGui.QAction("Minimize To Tray",self)
		setting = QtGui.QAction("Preference",self)
		cLoc = QtGui.QAction("Change Downloads Destination",self)
		quit = QtGui.QAction("Quit",self)
		
		miniToTray.setShortcut('Ctrl+M')
		menu.addMenu(self.downloads)
		menu.addSeparator()
		menu.addAction(miniToTray)
		menu.addAction(setting)
		menu.addSeparator()
		menu.addAction(cLoc)
		menu.addSeparator()
		menu.addAction(quit)
		
		self.menuBtn.setMenu(menu)
		self.connect(miniToTray,QtCore.SIGNAL('triggered()'),self.goToTray)
		self.connect(setting,QtCore.SIGNAL('triggered()'),self.getSetting)
		self.connect(cLoc,QtCore.SIGNAL('triggered()'),self.changeLoc)
		self.connect(quit,QtCore.SIGNAL('triggered()'),self.safeExit)		
				
	def changeLoc(self) :
		data=self.dLocation
		if not(os.path.exists(data)) :
			data='/home'			
		fD = QtGui.QFileDialog(self,'Get Download Destination',data,'')
		fD.setOption(QtGui.QFileDialog.ShowDirsOnly,True)
		fD.setFileMode(2)
		fD.resize(500,300)
		fLoc=''
		if fD.exec_() :		
			if len(fD.selectedFiles()) > 0 :
				fLoc=fD.selectedFiles()[0]
		fLoc=str(fLoc)
		if len(fLoc) > 0 :
			if os.path.exists(fLoc) :
				self.dLocation=fLoc
				f = open(os.getcwd()+'/Locale/desF','w')
				f.write(fLoc)
				f.close()
				for key in self.dLoads :
					if not(self.dLoads[key]==None) :
						self.dLoads[key].dLocation=fLoc
		
	def getSetting(self) :
		self.pref.show()
		
	def addTrayIcon(self) :
		self.trayIcon.setIcon(QtGui.QIcon('image/tray.png'))
		
		menu = QtGui.QMenu(self)
		showWin = QtGui.QAction("Show Window",self)
		quit = QtGui.QAction("Quit",self)			
		
		menu.addAction(showWin)
		menu.addMenu(self.downloads)
		menu.addAction(quit)				
		
		self.trayIcon.setContextMenu(menu)
		self.connect(showWin,QtCore.SIGNAL('triggered()'),self.getOutOfTray)
		self.connect(quit,QtCore.SIGNAL('triggered()'),self.safeExit)
		
	def mousePressEvent(self,event) :
		self.posMove = event.pos()
	
	def mouseMoveEvent(self,event) :
		if self.posMove :
			self.move(self.pos().x()+event.pos().x()-self.posMove.x(),self.pos().y()+event.pos().y()-self.posMove.y())
	
	def mouseReleaseEvent(self,event) :
		self.posMove=None			
			
	def creditMsg(self) :
		ok = QtGui.QMessageBox(QtGui.QMessageBox.Information,'LDM Community',"By using this application you are contributing to this development.Thanks a lot for it.\nHope you'll enjoy & share your experience\n-Anand Kumar\nEfficience\nSubscribe to  (linkinAnand.blogspot.com) to get all the latest information.\nDeveloper (twitter.com/EfficienceAnand)\ncurrently at IIITA",QtGui.QMessageBox.Ok,self,QtCore.Qt.FramelessWindowHint)
		ok.show()
		
	def goToTray(self) :
		if self.isVisible() :
			self.hide()

	def getOutOfTray(self) :
		if not(self.isVisible()) :
			self.show()
			
	def safeExit(self) :
		gT=True
		for key in self.dLoads :
			if self.dLoads[key].free == 0 :
				gT=False
				break
		if gT==True :
			sys.exit(0)
		else :
			msg=QtGui.QMessageBox(QtGui.QMessageBox.Question,'!!',"Some Download process are still running\nWould you still like to quit the application ?",QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,self,QtCore.Qt.FramelessWindowHint)
			ok=msg.exec_()
			if ok == QtGui.QMessageBox.Yes :
				self.goTerminate=True
				for key in self.dLoads :
					self.dLoads[key].flag | 0x0080
		
def main() :
	app = QtGui.QApplication(sys.argv)
	win = MainFrame()
	win.show()
	sys.exit(app.exec_())
