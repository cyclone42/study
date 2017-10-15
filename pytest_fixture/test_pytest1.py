from __future__ import print_function
import pytest


#@pytest.mark.usefixture('auth_setup') 



class Testfixture2:

	class_var1 = "w2er"
	class_var2 = "r2ty"

	def test_abc(self, auth_setup):
		print('\n test_1()')
		print("class var 1 = {}".format(self.class_var1))
 


	def test_bcd(self, auth_setup):
		print('\n test_2()')
		print("class var 2 = {}".format(self.class_var2))



