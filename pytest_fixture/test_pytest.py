from __future__ import print_function
import pytest


#@pytest.mark.usefixture('auth_setup') 
class Testfixture1:

	class_var1 = "w1er"
	class_var2 = "r1ty"
	
	@pytest.fixture(scope='function')
	def test_12(self):
		print("Class scope - DATA_TEARDOWN")
		
	@pytest.fixture(scope='function')
	def test_11(self):
		print('\nscope- before fixture; before each test')



