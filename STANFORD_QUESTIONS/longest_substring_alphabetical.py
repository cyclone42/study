"""
Assume s is a string of lower case characters.

Write a program that prints the longest substring of s in which the letters occur in alphabetical order. For example, if s = 'azcbobobegghakl', then your program should print

Longest substring in alphabetical order is: beggh
In the case of ties, print the first substring. For example, if s = 'abcbcd', then your program should print

Longest substring in alphabetical order is: abc
"""


s = 'azcbobobegghakl'
#s = 'abcbcd'
#s = 'aabbazdabcde'
#s = 'zyxwvutsrqponmlkjihgfedcba'
#s = 'hvshulbuauu'   # auu
#s = 'abcdefghijklmnopqrstuvwxyz'  # whole string


substringList = [0,0]

for i in range(0,len(s)):
	j = i+1 
#	print("i = {}, j = {}".format(i,j)) 
	stopLoop = False
	while (stopLoop == False and i<len(s) and j<=len(s)):
		word = s[i:j]
#		print("word formed {}".format(word))
		if word == ''.join(sorted(word)):
			wordLen = len(word)
			if wordLen > substringList[0]:
				substringList[0] = wordLen
				substringList[1] = word
			j = j+ 1
		else:
			stopLoop = True
	
print("Longest substring in alphabetical order is: {}".format(substringList[1]))

