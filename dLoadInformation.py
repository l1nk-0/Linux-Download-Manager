'''**********************************************************************************************************************************
 * LDM :- dLoadInformation.py
 * -Anand Kumar
 * 
 * All information about downloads when application is closed o any download completes is stored in an XML file.
 * dLoadInformation process & builds an understandable (to programme) objects out of them.
 * Description :-
 *		Info :- A dta-structure to store individual information.
 * 		dLoadInfo :- A class that contains all routines to process XML file.
***********************************************************************************************************************************'''

import os,sys,time
from xml.dom import minidom
from xml.dom.minidom import Document

class Info :
	''' Data-structure to store information '''
	def __init__(self) :
		self.url=''
		self.fileName=''
		self.date=''
		self.time=''
		self.length=''
		self.partition={}
		
class dLoadInfo :
	def __init__(self) :
		self.fileName='CheckFile.xml'
		if not(os.path.isdir(os.getcwd()+'/Locale')) :
			os.mkdir(os.getcwd()+'/Locale')
			
	def generateElement(self,name,Info,doc) :
		node = doc.createElement(name)
		if len(str(Info)) > 0 :
			ptext = doc.createTextNode(str(Info))
			node.appendChild(ptext)
		
		return node
		
	def CreateDownloadNode(self,doc,ldm,obj) :
		dLoad = doc.createElement('Download')	

		node = self.generateElement('url',obj.url,doc)
		dLoad.appendChild(node)
		node = self.generateElement('fileName',obj.fileName,doc)
		dLoad.appendChild(node)
		node = self.generateElement('date',obj.date,doc)
		dLoad.appendChild(node)
		node = self.generateElement('time',obj.time,doc)
		dLoad.appendChild(node)
		node = self.generateElement('length',obj.length,doc)
		dLoad.appendChild(node)
		node = self.generateElement('partition','',doc)
		
		for key in obj.partition :
			part = self.generateElement('part','',doc)
			dData = obj.partition[key]
			dNode = self.generateElement('lower',dData[0],doc)
			part.appendChild(dNode)
			dNode = self.generateElement('upper',dData[1],doc)
			part.appendChild(dNode)
			dNode = self.generateElement('downloaded',dData[2],doc)
			part.appendChild(dNode)
			
			node.appendChild(part)

		dLoad.appendChild(node)			
		
		return dLoad
		
	def CreateDFile(self,data) :		
		doc = Document()
		ldm = doc.createElement('LDM')
		ldm.setAttribute('DESC','A DOWNLOAD MANAGER FOR LINUX DFILE')
		
		for key in data :
			obj = data[key]
			node = self.CreateDownloadNode(doc,ldm,obj)
			ldm.appendChild(node)
			
		doc.appendChild(ldm)	
		
		f = open(self.fileName, 'w')
		doc.writexml(f)
		f.close()
			
	def WriteInformation(self,obj) :
		if not(os.path.exists(os.getcwd()+'/Locale/'+self.fileName)) :
			data={}
			data[0]=obj
			self.CreateDFile(data)
		else :
			try :
				doc = minidom.parse(self.fileName)
				ldm = doc.firstChild
				node=self.CreateDownloadNode(doc,ldm,obj)
				ldm.appendChild(node)
		
				f = open(os.getcwd()+'/Locale/'+self.fileName, 'w')
				doc.writexml(f)
				f.close()			
			except :
				data={}
				data[0]=obj
				self.CreateDFile(data)
			
			
	def ifMatch(self,dNode,obj) :
		i=1
		node = dNode.getElementsByTagName('url')[0]
		if not(str(node.firstChild.data) == obj.url) :
			i=0
		node = dNode.getElementsByTagName('fileName')[0]
		if not(str(node.firstChild.data) == obj.fileName) :
			i=0
		node = dNode.getElementsByTagName('date')[0]
		if not(str(node.firstChild.data) == obj.date) :
			i=0
		node = dNode.getElementsByTagName('time')[0]
		if not(str(node.firstChild.data) == obj.time) :
			i=0
		return i

	def ReplaceNode(self,obj) :
		xmldoc = minidom.parse(os.getcwd()+'/Locale/'+self.fileName)
		
		doc = xmldoc.firstChild
		i=0
		for dNode in doc.childNodes :
			if self.ifMatch(dNode,obj) :
				newNode = self.CreateDownloadNode(xmldoc,doc,obj)
				doc.replaceChild(newNode,dNode)
				i=1
				break
		
		f = open(os.getcwd()+'/Locale/'+self.fileName, 'w')
		doc.writexml(f)
		f.close()
		
		if i==1:
			return 1		
		return 0

	def DeleteNode(self,obj) :
		xmldoc = minidom.parse(os.getcwd()+'/Locale/'+self.fileName)
		
		doc = xmldoc.firstChild
		i=0
		for dNode in doc.childNodes :
			if self.ifMatch(dNode,obj) :
				doc.removeChild(dNode)
				i=1
				break
		
		f = open(os.getcwd()+'/Locale/'+self.fileName, 'w')
		doc.writexml(f)
		f.close()
		
		if i==1:
			return 1
		return 0
		
	def getData(self,dNode) :	
		obj = Info()
		data = dNode.getElementsByTagName('url')[0].firstChild.data
		obj.url=data
		
		data = dNode.getElementsByTagName('fileName')[0].firstChild.data
		obj.fileName=data
			
		data = dNode.getElementsByTagName('date')[0].firstChild.data
		obj.date=data
		data = dNode.getElementsByTagName('time')[0].firstChild.data
		obj.time=data

		data = dNode.getElementsByTagName('length')[0].firstChild.data
		obj.length=data
		
		node = dNode.getElementsByTagName('partition')[0]
		i=0
		for pNode in node.childNodes :
			lower=pNode.getElementsByTagName('lower')[0].firstChild.data
			upper=pNode.getElementsByTagName('upper')[0].firstChild.data
			downloaded=pNode.getElementsByTagName('downloaded')[0].firstChild.data
		
			obj.partition[i]=[lower,upper,downloaded]
			i=i+1

		return obj
		
	def getInformation(self) :
		dInfo={}
		try :
			xmldoc = minidom.parse(os.getcwd()+'/Locale/'+self.fileName)

			doc = xmldoc.firstChild
		
			i=0
			for dNode in doc.childNodes :
				dInfo[i]=self.getData(dNode)
				i=i+1			
		except :
			pass
		
		return dInfo
	
	def getSpecificInformation(self,obj) :
		xmldoc = minidom.parse(os.getcwd()+'/Locale/'+self.fileName)
		
		doc = xmldoc.firstChild
		
		i=0
		for dNode in doc.childNodes :	
			if self.ifMatch(dNode,obj) :
				partition=dNode.getElementsByTagName('partition')[0]
				for node in partition.childNodes :
					lower=node.getElementsByTagName('lower')[0].firstChild.data
					upper=node.getElementsByTagName('upper')[0].firstChild.data
					downloaded=node.getElementsByTagName('downloaded')[0].firstChild.data
					obj.partition[i]=[int(lower),int(upper),int(downloaded)]
					i=i+1
				return obj
				
		return None
