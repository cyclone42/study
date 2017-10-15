# How to shuffle a peck of cards or given list  or object or any other collection
# You have a list of things, and you need them to now appear in a random order
# make sure random number doesnot get repeat

# CONDITION
# create a random number
# pick a number from unshuffled list in reverse order[ it adds more randamization]
# put this number in 'r'th index of unshuffled list and if that index is occupied than increment the random number and put it.
# if you pick a number from idx =2 in unshuffled_list than it should not be placed at idx=2 in shuffled_list.


# Its  O(N)  but inefficient in place(2l+constant) as shuffling can be done in-place too. See 2nd solution.



import random

"""
unshuffled_list = [11,12,13,14,15,16,17,18,19,110]
#unshuffled_list = [5,8,9,14,21]

alen = len(unshuffled_list)

shuffled_list = (alen)*[None]

print("\n\nunshuffled_list ={}, \nshuffled_list= {}\n".format(unshuffled_list, shuffled_list))

def get_random_number():
	r = random.randint(0, alen-1) #Generate number from 0 to alen-1
	return r


for idx in range(alen-1,-1,-1): # range(start, stop, step)
	print("\ncurrent_idx: {}".format(idx))

	r = get_random_number() 	
	print("random: {}".format(r))	
	print(shuffled_list)
	if shuffled_list[r] == None and idx != r:
		shuffled_list[r] = unshuffled_list[idx]
		#print(shuffled_list)
	else:
		random_flag = True # keep generating random
		while(random_flag):
			r = get_random_number()
			print("while r = {}".format(r))
			#print(shuffled_list)
			if shuffled_list[r] == None and idx != r:
				shuffled_list[r] = unshuffled_list[idx]
				#print(shuffled_list)
				random_flag= False
			else:
				random_flag=True


print("\n\nunshuffled_list={}, \nshuffled_list = {}\n".format(unshuffled_list, shuffled_list))
"""

#unshuffled_list=[5, 8, 9, 14, 21],
#shuffled_list = [14, 8, 9, 21, 5] Here 8, 9 are at same index, may be we can shuffle them too
# for last index just place it directly in shuffled_list.
#=================================================================

# **** 2nd SOLUTION  ******
# time O(n) and IN-PLACE SHUFFLING 


unshuffled_list = [5,8,9,14,21]
print(unshuffled_list)
alen = len(unshuffled_list)

for idx in range(0,alen, 1): # start, stop-1, step

#	print("idx= {}".format(idx))
	r = random.randint(idx, alen-1) #Generate number from 0 to alen-1
	unshuffled_list[idx], unshuffled_list[r] = unshuffled_list[r], unshuffled_list[idx] 
	
print(unshuffled_list)
































































































