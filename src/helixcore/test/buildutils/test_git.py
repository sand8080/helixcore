import os
import unittest

from helixcore.buildutils.git import comments_num


class GitTestCase(unittest.TestCase):
    def test_comments_num(self):
        comments_num(os.path.join('..', '..'))
        comments_num('.')
        comments_num(os.path.dirname(__file__))
        comments_num(os.path.realpath(os.path.dirname(__file__)))


if __name__ == '__main__':
    unittest.main()
