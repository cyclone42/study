#trying with classes and its ooo properties


class MyClass:
  var2 = 20
  var1 = 10

  def func1(self, var2):
    print("here is the value var2", var2)

  def func2(self):
    print("here is the value var1", self.var1)
      


myobj = MyClass()

print("in obj myobj var 1".format(myobj.var1))
print("in obj myobj var 2".format(myobj.var2))

