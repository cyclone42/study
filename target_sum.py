# 
#num = [2,7,11,15]
#target = 9
# return other number to add up to specific target.

#assume : each input would have onr sol n not to use the same no twice

def find_other_no(inList, target):

	#verify inList is not empty
	# verify inList has unique values: either remove unique val or return error msg
	sumDict =dict() 
	
	for num in inList:
		val = target-num
		sumDict[num]=val
	print(sumDict)	 

	for key, val in sumDict.items():
		if val in sumDict.keys():
			print key,	



num = [2,7,11,15]
target = 9
x = find_other_no(num, target)
