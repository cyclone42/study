# Geeks for Geeks - http://www.geeksforgeeks.org/array-rotation/
# Program for array rotation
# Write a function rotate(ar[], d, n) that rotates arr[] of size n by d elements
# -----------------------


def rotate_arr(arr1, d):
	# python makes it rediculously easy
	arr1 = arr1[d:] + arr1[:d] # arr[3:] + arr[:3]
	return arr1

arr1 = [2,4,6,9,11,15,20,25] 
rotate_num = 3 # rotate by 'rot' elements
print(arr1)
print(rotate_arr(arr1, rotate_num))

# State interesting permutations
'''
0 => arr == rotated_arr, 
3 => verify rotated_arr 
8, 16, 32 => arr == rotated_arr,
-1 => rotated_arr in reverse dir
10 => rotated_arr by 2  

'''


def rotate_arr_using_loop(arr, d):
	alen = len(arr)
	newarr = []

	print("\n")
	for i in range(d, alen, 1):
		print(i, arr[i])		
		newarr.append(arr[i])

	newarr.extend(arr[:d])
	print(newarr)


arr = [2,3,6,9,11,15,20,25] 
rotate_num = 3 # rotate by 'rot' elements
rotate_arr_using_loop(arr,rotate_num)  # [9, 11, 15, 20, 25, 2, 3, 6]








