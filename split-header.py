import sys
count = 0
target = open('header.xml','w')
with open('../dataset/citeseerx.xml') as f:
    for line in f:        
    	count +=1
        print count
        print line
        if count > 50:
            break
        else:
            target.write(line)