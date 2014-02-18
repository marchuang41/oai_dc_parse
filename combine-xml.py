import os
path = "../dataset/cleanxml/"
lst = os.listdir(path)
max = 0
for filename in lst:
    if filename.endswith(".xml"):		
    	basename = filename.partition('.')
    	i = basename[0].split('citeseerx')[1]    	
    	if int(i) > max:
    		max = int(i)
target = open("../dataset/cleanxml/citeseerx_clean.xml","w")
for i in range(max+1):
	filename = "citeseerx" + str(i) + ".xml"
	print "[Write file]" + filename
	with open(path+filename) as f:
		for line in f:
			target.write(line)
