from validol import Scheme
import unittest
import docsgenerator

class GenerateDocsTestCase(unittest.TestCase):
    def test_ping(self):
        scheme = Scheme({})
        self.assertEquals(
            docsgenerator.generate(scheme),
            ''
        )


if __name__ == '__main__':
    print '1) doctests'
    import doctest, validol
    doctest.testmod(validol)
    print 'done'

    print '2) unittests'
    unittest.main()
