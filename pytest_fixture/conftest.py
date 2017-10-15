from __future__ import print_function
import pytest


@pytest.fixture(scope='session')
def authorize_fake():
	print("\n Authorize_fake: session scope")
	accounts_token = "abcd"
	yield accounts_token
	print("\n Logout function")



@pytest.fixture(scope='function')
def auth_setup(authorize_fake):
	print("auth_setup :class scope")
	token=authorize_fake
	print("token = {}".format(token))
	print("auth setup")
	return token
 
