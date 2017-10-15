# Replace every element with the greatest element on right side

# http://www.geeksforgeeks.org/replace-every-element-with-the-greatest-on-right-side/

# Given an array of integers, replace every element with the next greatest element 
# (greatest element on the right side) in the array. Since there is no element 
# next to the last element, replace it with -1. For example, 
# if the array is {16, 17, 4, 3, 5, 2}, then it should be modified to {17, 17, 5, 5, 5, -1}.
# [ 16, 17, 81, 32, 4, 3, 5] ==> [81, 81, 81, 32, 5, 5, -1] 

"""
Brute-force algorithm:
1) Use two for loops to traverse thru the list element and find greatest and replace it 

"""



def brute_force_replace_greatest(alist):
	alen = len(alist)
	if alen == 0:
		return False
	if alen == 1:
		return alist
	if alen == 2:
		if alist[1] > alist[0]:
			return [alist[1], -1]
		return [alist[0], -1]

	i = 0
	j = 1
	for i in range(0, alen, 1):
		
		 



alist = [ 16, 17, 81, 32, 4, 3, 5]
brute_force_replace_greatest(alist)




