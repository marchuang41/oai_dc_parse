import sys
import xml.sax
import MySQLdb as mdb

class ErrorHandler:
	def __init__(self, parser):
		self.parser = parser

	def fatalError(self, msg):		
		print msg

class dbController:
	def __init__(self):
		self.con = mdb.connect('localhost','cite','cite','citeseerx')
		self.con.set_character_set('utf8')
		self.cur = self.con.cursor(mdb.cursors.DictCursor)
		self.lastId = 0

	def insertPaper(self,data):
		tmp = dict([('contributor',''),('creator',''),('date',''),('description',''),('publisher',''),('source',''),('title',''),('identifier','')])
		subjectIds = []
		sql = "INSERT INTO `Papers` (`IndexId`,`contributor`,`creator`,`date`,`description`,`publisher`,`source`,`title`,`identifier`) VALUES ('%s'," % (data['IndexId'])
		rows = data.items()
		rows.sort()			
		for k, v in rows:
			k = k.replace("dc:","")			
			if k == 'date':
				if len(v[-1]) == 4:
					if v[-1].isdigit():
						if int(v[-1]) >= 1901 and int(v[-1]) <= 2155:
							tmp[k] = v[-1]
						else:
							tmp[k] = 0
					else:
						tmp[k] = 0
				else:
					tmp[k] = 0
			elif k == 'subject':
				subjectIds = self.insertSubjects(v)
			elif k == 'identifier':
				tmp[k] = v[0].split(":")[-1]
			elif k == 'creator':
				tmp[k] = ', '.join(v)
			elif k == 'IndexId':
				continue
			else:
				tmp[k] = ' '.join(v)

		sql += "'%s','%s','%s','%s','%s','%s','%s','%s');" % (tmp['contributor'],tmp['creator'],tmp['date'],self.con.escape_string(tmp['description'].encode('ascii', 'ignore')),tmp['publisher'],self.con.escape_string(tmp['source'].encode('ascii', 'ignore')),self.con.escape_string(tmp['title'].encode('ascii', 'ignore')),tmp['identifier'])
		#print sql
		with self.con:
			try:
				self.cur.execute(sql)
				self.con.commit()
			except:
				print sql
				exit()
		#get last insert id
		self.lastId = data['IndexId']
		self.addSubjectRelation(subjectIds)
		#print self.lastId
		#print subjectIds
		

	def insertSubjects(self,data):
		result = []
		for val in data:
			select = "SELECT `subjectId` FROM `Subjects` WHERE `subject` = '%s'" %(self.con.escape_string(val.encode('ascii', 'ignore')))
			try:
				self.cur.execute(select)				
			except:
				print select
				exit()
			if int(self.cur.rowcount) < 1:
				insert = "INSERT INTO `Subjects` (`subjectId`,`subject`) VALUES (NULL,'%s')" %(self.con.escape_string(val.encode('ascii', 'ignore')))
				with self.con:
					try:
						self.cur.execute(insert)
						result.append(self.cur.lastrowid)
						self.con.commit()
					except:
						print insert
						exit()						
			else:
				result.append(self.cur.fetchone()['subjectId'])
		return result
		
	def addSubjectRelation(self,subjectIds):
		for idx in subjectIds:
			sql = "INSERT INTO `Subject_relation` (`IndexId`,`subjectId`) VALUES ('%s','%s')" % (self.lastId,idx)
			self.cur.execute(sql)				

def read_record():
    try:
        with open('../dataset/block_record.txt') as f:
        	block = f.read()	        	
        	return int(block)	        	   
    except IOError:
        return 0

class CiteseerxHandler(xml.sax.ContentHandler):
	def __init__(self,dbCtrl):
		xml.sax.ContentHandler.__init__(self)
		self.filter = ['record','header','datestamp','metadata','oai_dc:dc','dc:rights','dc:identifier','dc:format','dc:language','dc:type']
		self.lock = 20000000
		self.tag = None
		self.block = 0
		self.data = dict()
		self.dbCtrl = dbCtrl
		self.record = read_record()		

	def block_record(self):	    
	    target = open('../dataset/block_record.txt','w')
	    target.write(str(self.block))
	    target.write("\n")
	    target.close()
	    #print "[System]Line record done."  

	def startDocument(self):
		print "[System] Open document"
		print "[System] Start document at block: " + str(self.record)

	def startElement(self, name, attrs):
		self.tag = name
		if name == "record":
			self.block +=1
			self.data = dict()
			if self.block < self.lock:
				print "[System] Read block: %s" % str(self.block)

		if name not in self.filter:
			#print "Tag:" + name
			#for attr in attrs.getNames():
			#	print attr + ":" + attrs.getValue(attr)
			if name not in self.data:				
				self.data[name] = []

	def characters(self, content):
		text = content.strip()
		text = text.replace("\n", "")
		if self.tag not in self.filter:
			if len(text) > 0:
				#print text
				self.data[self.tag].append(text)

	def endElement(self, name):
		self.tag = name
		#if name not in self.filter:			
			#print "Tag End"
		if self.tag == "record" and self.block < self.lock:
		#if self.tag == "record":			
			if self.block > self.record:
				self.readablePrint()
				self.data['IndexId'] = self.block
				self.dbCtrl.insertPaper(self.data)								
				self.block_record()				

	def readablePrint(self):
		rows = self.data.items()
		rows.sort()			
		for k, v in rows:
			k = k.replace("dc:","")
			#print "[" + k + "]"
			for val in v:
				if k == "identifier":
					print val.split(":")[-1]
					sys.stdout.flush()
					#identifier = val.split(":")[-1].replace(".","")
					#print "%s(%s)" % (identifier, len(identifier))					
				#elif k == "date":
				#	print v[-1]
				else:
					continue
					#print val
			

def main(sourceFile):
	dbCtrl = dbController()
	parser = xml.sax.make_parser()
	citeseerxHandeler = CiteseerxHandler(dbCtrl)
	parser.setContentHandler(citeseerxHandeler)

	errorHandler = ErrorHandler(parser)
	parser.setErrorHandler(errorHandler)
	
	source = open(sourceFile)
	parser.parse(source)

if __name__ == "__main__":
	main("../dataset/citeseerx_clean.xml")
