
###  =================== 
x = 12
def g(x):
	print("x {}".format(x))
	x = x + 1
	def h(y):
		print("y {}".format(y))
		print("x+y {}".format(x+y))
		return x + y
	return h(6)
g(x)
###  =================== 

## RECURSION - Factorial

n = 3
def fact(n):
	if n == 1:
		print("N is 1")
		return 1
	else:
		return n*fact(n-1)			

y = fact(13)
print y
