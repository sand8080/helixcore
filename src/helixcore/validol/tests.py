#from docsgenerator import format
from validol import Scheme
import unittest


class GenerateDocsTestCase(unittest.TestCase):
    def test_simple_request_doc(self):
        scheme = Scheme({})
        self.assertEquals(
            format(scheme),
            '<div class="block">'
                '<div class="brace">{</div>'
                '<div class="indent">'
                    '<div class="comment">// empty</div>'
                '</div>'
                '<div class="brace">}</div>'
            '</div>'
        )

if __name__ == '__main__':
    print '1) doctests'
    import doctest, validol
    doctest.testmod(validol)
    print 'done'

    print '2) unittests'
    unittest.main()
