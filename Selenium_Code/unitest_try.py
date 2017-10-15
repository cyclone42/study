import unittest
import pytest



def helper_func(x, y):
    print("Here is helper function")
    sum = x+ y
    print("SUM {} is helper function".format(sum))
    return sum 
    

class TestStringMethods(unittest.TestCase):

   
    def printing(self):
        print("here is i am printing") 


    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.printing()
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        xx, yy = 4, 10
        print("before helper")
        result = helper_func(xx, yy)
        print("Afte helper ={}".format(result))

        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()
