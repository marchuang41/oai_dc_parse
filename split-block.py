import sys
count = 0
head_str = "<?xml"
tail_str = "</OAI-PMH>"
file_serial = 1
path = '../dataset/cleanxml/citeseerx'
ext = '.xml'

def checkline(line):
    if line.find("<OAI-PMH") > -1:
        return 0
    elif line.find("<responseDate>") > -1:
        return 0
    elif line.find("<request") > -1:
        return 0
    elif line.find("<ListRecords>") > -1:
        return 0
    elif line.find("<resumptionToken>") > -1:
        return 0
    elif line.find("</ListRecords>") > -1:
        return 0
    else:
        return 1

with open('../dataset/citeseerx_cleanheader.xml') as f:
    for line in f:        
    	count +=1        
        if line.find(head_str) > -1:        	
        	target = open(path+str(file_serial)+ext,'w')
        	#print file_serial
        	file_serial += 1        	
        	print count
        	print line
        	#target.write(line)
        elif line.find(tail_str) > -1:
        	print count
        	print line
        	#target.write(line)
        #elif count > 30000:
        #	break
    	#elif file_serial > 3:
    	#	break
        else:
        	#print line
            #continue
            if checkline(line) == 1:
                target.write(line)