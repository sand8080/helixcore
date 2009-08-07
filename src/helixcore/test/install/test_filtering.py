import unittest

from helixcore.install.filtering import in_diapasone, filter_patches, filter_backward

class FilteringTestCase(unittest.TestCase):
    def test_in_diapasone(self):
        self.assertTrue(in_diapasone('1', '5', '4-6-7'))
        self.assertTrue(in_diapasone('1', None, '5'))
        self.assertTrue(in_diapasone(None, '7', '5'))
        self.assertTrue(in_diapasone('4', '7', '5'))
        self.assertTrue(in_diapasone('1', '47', '2-3'))
        self.assertFalse(in_diapasone('4', '7', '2-3'))
        self.assertFalse(in_diapasone('4', None, '2-3'))
        self.assertFalse(in_diapasone(None, '2', '2-3'))
        self.assertFalse(in_diapasone('1', '20', '34'))

    def test_filter_patches(self):
        patches = ['1', '2-2', '37', '4', '4-1', '4-1-0', '35', '35-0']
        self.assertEqual(
            ['2-2', '4', '4-1', '4-1-0'],
            filter_patches('2', '7-9-1', patches, reverse=False)
        )
        self.assertEqual(
            ['4', '4-1', '4-1-0'],
            filter_patches('2-2', '7-9-1', patches, reverse=False)
        )
        self.assertEqual(
            ['4', '4-1'],
            filter_patches('2-2', '4-1', patches, reverse=False)
        )
        self.assertEqual(
            ['1', '2-2', '4', '4-1', '4-1-0', '35'],
            filter_patches(None, '35', patches, reverse=False)
        )
        self.assertEqual(
            ['4-1-0', '4-1', '4', '2-2', '1'],
            filter_patches(None, '7-9-1', patches, reverse=True)
        )
        self.assertEqual(
            ['4-1', '4', '2-2', '1'],
            filter_patches(None, '4-1', patches, reverse=True)
        )
        
    def test_filter_backward(self):
        patches = ['1', '2-2', '3', '7-9-9', '6']
        self.assertEqual(
            ['7-9-9', '6', '3', '2-2', '1'],
            filter_backward(None, None, patches)
        )

if __name__ == '__main__':
    unittest.main()