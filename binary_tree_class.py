# Creating a binary tree class
"""
User

bst = Btree()
bst.insert(14)
bst.preorder()
bst.postorder()
bst.inorder()

"""


class Node:

  #Constructor
  def __init__(self, val):
    self.value = val
    self.leftChild = None
    self.rightChild = None

  def insert(self, val):
    if self.value == val:
      return False
    elif self.value > val:
      if self.leftChild:
        return self.leftChild.insert(val)
      else:
        self.leftChild = Node(data)
        return True
    else:     
      if self.rightChild:
        return self.rightChild.insert(val)
      else:
        self.rightChild = Node(data)
        return True
        

class Btree:
  def __init__(self):
    self.root = None

  def insert(self, data):
    if self.root:
      return self.root.insert(data)
    else:
      self.root = Node(data)
      return True




