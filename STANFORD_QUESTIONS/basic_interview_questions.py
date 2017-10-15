# Write a program that counts up the number of vowels contained in the string s. Valid vowels are: 'a', 'e', 'i', 'o', and 'u'. For example, if s = 'azcbobobegghakl', your program should print:

#Number of vowels: 5


#astr = 'azcbobobegghakl'
astr= "tzrxjarik"

def count_vowel(astr):
	vowelList=['a','e','i','o','u']
	vowelCount = 0

	for achar in astr:
		if achar in vowelList:
			vowelCount += 1	
			print achar ,
	print("Total vowels are {}".format(vowelCount))

#count_vowel(astr)


#Assume s is a string of lower case characters.
#Write a program that prints the number of times the string 'bob' occurs in s. For example, if s = 'azcbobobegghakl', then your program should print
#Number of times bob occurs is: 2

def count_word(s):
	word = 'bob'
	wordCount = 0

	wordLen = len(s)
	if wordLen > 2:
		for i in range(0,wordLen-2):
			if word == s[i:i+3]:
				wordCount += 1
	print("Number of times bob occurs is: {}".format(wordCount)) 
				

s = 'azcbobobegghakl'
count_word(s)















