import unittest
from predictQualitativeStatistic import State, get_random_path, verify, APOf
from pprint import pprint

class RverifyTestCase(unittest.TestCase):        

    def test_and_verify(self):
        s1 = State(1, list(), ['a','b'])
        pts = [1, s1]
        pathLength = 10
        path = get_random_path(pts, pathLength, None)
        trueLTL= ['&', 'a', 'b']
        falseLTL = ['&', 'aa', 'b']
        self.assertTrue(verify(APOf(path), trueLTL, 0))
        self.assertFalse(verify(APOf(path), falseLTL, 0))

    def test_or_verify(self):
        s1 = State(1, list(), ['a','b'])
        pts = [1, s1]
        pathLength = 10
        path = get_random_path(pts, pathLength, None)
        trueLTL = ['|', 'a', 'b']
        trueLTL2 = ['|', 'aa', 'b']
        falseLTL = ['|', 'aa', 'bb']
        self.assertTrue(verify(APOf(path), trueLTL, 0))
        self.assertTrue(verify(APOf(path), trueLTL2, 0))
        self.assertFalse(verify(APOf(path), falseLTL, 0))

    def test_until_verify(self):
        pass

if __name__ == '__main__':
    unittest.main()
