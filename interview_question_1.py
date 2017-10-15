"""
 First, I would like to code a function which takes a list as a input
 and print the anagrams as a output.
 Input : ['god', 'listen', 'erd', 'slient', 'dog']
 Output: all anagrams

ALGO 1 : Create a dictionary where key is the sorted word and word will stored a value
 like this { 'dgo':['dog', 'god'], 'eilnst':['silent', 'listen'] }
 Now print all values

ALGO 2 : Sort current word, then sort the copy of input list and do 1:1 compare 


FOLLOWUP : 
1) if there is duplicates like ['god', 'listen', 'erd', 'slient','dog', 'dog']
  should I ignore it or add it
  if added then output will look like this
  output: { 'dgo':['dog', 'god','dog'], 'eilnst':['silent', 'listen'] }
   
2) What is word has space like 'do g' , 'g od'
3) Will 'Dog' is anagram of 'god' ? is list case sensitive?
"""

#======================ALGO 1 =============================================

def print_anagram(input_list):
  print input_list
  op_dict = {}
  for item in input_list:
    item1 = item
    sorted_word = ''.join(sorted(item1)) # sorted() converts str into list 
    if sorted_word in op_dict.keys():
      op_dict[sorted_word].append(item)
    else:
      op_dict[sorted_word] = [item]

  print("\n final op_dict = {}".format(op_dict)) 
  for value in op_dict.keys():
    val_list = op_dict[value]
    if len(val_list) > 1:
      print("Here is anagram {}".format(val_list))  

mylist = ['god', 'listen', 'odg','erd', 'slient', 'dog'] 
#print_anagram(mylist)



#======================ALGO 2 =============================================

def sort_anagram(input_list):
  print input_list
  copy_list = []
  
  for item in input_list:
    sorted_element = ''.join(sorted(item))
    if 







mylist2 = ['god', 'listen', 'odg','erd', 'slient', 'dog'] 
sort_anagram(mylist2)

