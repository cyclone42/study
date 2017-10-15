#Problem 1
"""
10.0 points possible (graded)
Assume s is a string of lower case characters.

Write a program that counts up the number of vowels contained in the string s. Valid vowels are: 'a', 'e', 'i', 'o', and 'u'. For example, if s = 'azcbobobegghakl', your program should print:

"""
 
def count_vowel(input_str):
  
    s = list(input_str)
    print("Here is the input str {}".format(s))
    list_vow = ['a', 'e', 'i', 'o', 'u']

    count_vow= 0
    for i in s:
        print("here is i {}".format(i))
        if i in list_vow:
            count_vow += 1
    print("total count ={}".format(count_vow))
 

if __name__=="__main__":

    print("here is the main")
    input_str= "azcbobobegghakl"
    count_vowel(input_str)
