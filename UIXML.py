import os,sys,hashlib
from xml.dom import minidom
from xml.dom.minidom import Document
from Crypto.Cipher import AES

class UIXML :
	def __init__(self,loc = None) :		
		self.loc = loc
		self.aes = AES.new('CRLKUTSPALMWYTDB',AES.MODE_ECB)
	
	def bringTo32(self,text) :
		if len(text) >= 32 :
			return text[0:32]
		else :
			for i in range(32-len(text)) :
				text = text+' '
		return text
	
	def crypt(self,passwrd) :		
		ciphercode=self.aes.encrypt(self.bringTo32(passwrd))
		return ciphercode
		
	def decrypt(self,passwrd) :
		data = self.aes.decrypt(passwrd)
		return data
		
	def generateXML(self) :
		doc = Document()
		ui = doc.createElement('userinfo')
		doc.appendChild(ui)
		return doc
		
	def createChild(self,doc,text) :
		ptext = doc.createTextNode(text)
		return ptext
		
	def getProxyInformation(self,user) :
		l=[]	
		try :
			xmldoc = minidom.parse(os.getcwd()+'/'+str(hashlib.sha224(user).hexdigest())+'/Uinfo')	

			doc = xmldoc.firstChild
			l.append(doc.getElementsByTagName('http')[0].firstChild.data)
			l.append(doc.getElementsByTagName('port')[0].firstChild.data)		
			try :
				passwrd = file(os.getcwd()+'/'+str(hashlib.sha224(user).hexdigest())+'/lzxxslfd','rb')
				l.append(doc.getElementsByTagName('login')[0].firstChild.data)
				password = passwrd.read()			
				l.append(self.decrypt(password))
				passwrd.close()
			except :
				pass
		except :
			return []
		return l
		
	def setProxyInformation(self,user,info) :
		try :
			if not os.path.isdir(os.getcwd()+'/'+str(hashlib.sha224(user).hexdigest())) :	
				os.mkdir(os.getcwd()+'/'+str(hashlib.sha224(user).hexdigest()))
			xmldoc = minidom.parse(os.getcwd()+'/'+str(hashlib.sha224(user).hexdigest()+'/Uinfo'))
		except :
			xmldoc = self.generateXML()
			
		doc = xmldoc.firstChild
					
		if len(info) >= 2 :
			try :
				doc.removeChild(doc.getElementsByTagName('http')[0])
			except :				pass
			child = xmldoc.createElement('http')
			child.appendChild(self.createChild(xmldoc,info[0]))
			doc.appendChild(child)
			try :
				doc.removeChild(doc.getElementsByTagName('port')[0])
			except :
				pass
			child = xmldoc.createElement('port')
			child.appendChild(self.createChild(xmldoc,info[1]))
			doc.appendChild(child)
			try :			
				doc.removeChild(doc.getElementsByTagName('login')[0])
			except :
				pass
		if len(info) == 4 :
			try :
				passwrd = open(os.getcwd()+'/'+str(hashlib.sha224(user).hexdigest())+'/lzxxslfd','wb')
				passwrd.write(self.crypt(info[3]))
				passwrd.close()
				child = xmldoc.createElement('login')
				child.appendChild(self.createChild(xmldoc,info[2]))
				doc.appendChild(child)
			except :
				pass
			
		f = open(os.getcwd()+'/'+str(hashlib.sha224(user).hexdigest())+'/Uinfo', 'w')
		xmldoc.writexml(f)
		f.close()
		return 1
		
	def getSchedule(self,user) :
		try :
			xmldoc = minidom.parse(os.getcwd()+'/'+str(hashlib.sha224(user).hexdigest())+'/Uinfo')
		except :
			return []
			
		l=[]	
		dict = {}
		schedule = xmldoc.firstChild.getElementsByTagName('schedule')
		if len(schedule) :
			schedule = schedule[0]
		else :
			return []
		sched = schedule.getElementsByTagName('sched')
		if len(sched) >= 7:
			for i in range(7) :
				l.append(sched[i].firstChild.data)
			for i in range(7,len(sched)) :	
				try :
					dict[sched[i].attributes['date'].value]=sched[i].firstChild.data
				except :
					dict[sched[i].attributes['date'].value]='  '
				
		l.append(dict)		
		return l
		
	def setSchedule(self,user,info) :
		try :
			if not os.path.isdir(os.getcwd()+'/'+str(hashlib.sha224(user).hexdigest())) :
				os.mkdir(os.getcwd()+'/'+str(hashlib.sha224(user).hexdigest()))
			xmldoc = minidom.parse(os.getcwd()+'/'+str(hashlib.sha224(user).hexdigest())+'/Uinfo')
		except :
			xmldoc = self.generateXML()
			
		if len(info) < 7:
			return 0
			
		doc = xmldoc.firstChild.getElementsByTagName('schedule')
		if len(doc) :
			doc = doc[0]
		else :
			doc = xmldoc.createElement('schedule')
			xmldoc.firstChild.appendChild(doc)
			
		days = doc.getElementsByTagName('sched')
		for node in days :
			doc.removeChild(node)			
		for i in range(7) :
			child = xmldoc.createElement('sched')
			child.appendChild(self.createChild(xmldoc,info[i]))			
			doc.appendChild(child)			
		dict = info[7]
		for key in dict :
			child = xmldoc.createElement('sched')
			child.appendChild(self.createChild(xmldoc,dict[key]))
			child.setAttribute('date',key)
			doc.appendChild(child)
		
		file = open(os.getcwd()+'/'+str(hashlib.sha224(user).hexdigest())+'/Uinfo','w')
		xmldoc.writexml(file)
		file.close()
		
		return 1
