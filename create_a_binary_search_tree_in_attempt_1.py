class TreeNode:
    def __init__(self, val=0):
        self.val = val
        self.left = None
        self.right = None

class BST:
    def __init__(self):
        self.root = None
    
    def insert(self, val):
        self.root = self._insert(self.root, val)
    
    def _insert(self, node, val):
        if not node:
            return TreeNode(val)
        if val < node.val:
            node.left = self._insert(node.left, val)
        else:
            node.right = self._insert(node.right, val)
        return node
    
    def search(self, val):
        return self._search(self.root, val)
    
    def _search(self, node, val):
        if not node or node.val == val:
            return node is not None
        if val < node.val:
            return self._search(node.left, val)
        return self._search(node.right, val)

if __name__ == "__main__":
    bst = BST()
    for val in [5, 3, 7, 2, 4, 6, 8]:
        bst.insert(val)
    print(f"Search 4: {bst.search(4)}")
    print(f"Search 9: {bst.search(9)}")

import unittest

class TestBST(unittest.TestCase):
    def test_bst(self):
        bst = BST()
        bst.insert(5)
        bst.insert(3)
        bst.insert(7)
        self.assertTrue(bst.search(5))
        self.assertTrue(bst.search(3))
        self.assertFalse(bst.search(10))