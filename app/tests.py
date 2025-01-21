import unittest
from script import add

class TestScripts(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(1,2), 3)
        self.assertNotEqual(add(-4,2), 0)

if __name__ == '__main__':
    unittest.main()