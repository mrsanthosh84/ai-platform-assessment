def hello():
    return "Hello, World!"

if __name__ == "__main__":
    print(hello())

import unittest

class TestHello(unittest.TestCase):
    def test_hello(self):
        self.assertEqual(hello(), "Hello, World!")