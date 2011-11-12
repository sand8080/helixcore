import unittest

from helixcore.data_struct.tree import TreeNode


class TreeTestCase(unittest.TestCase):
    def test_tree_node_eq(self):
        self.assertEquals(TreeNode('a'), TreeNode('a'))
        self.assertNotEquals(TreeNode('a'), TreeNode('b'))

        node = TreeNode('bbbb')
        self.assertEquals(node, node)

        class A(object):
            def __init__(self, val):
                self.val = val

            def __eq__(self, other):
                return self.val == other.val

        lh, rh = TreeNode(A('a')), TreeNode(A('b'))
        self.assertNotEquals(lh, rh)
        self.assertNotEquals(lh, TreeNode(A(1)))

    def test_compare_tree_node_with_obj(self):
        lh = TreeNode('aa')
        self.assertEquals(lh, 'aa')
        self.assertNotEquals(lh, 'aaa')

    def test_tree_node_add_child(self):
        root = TreeNode(None)
        ch_val = 'a'
        ch_num = len(root.children)
        root.add_child(ch_val)
        self.assertEquals(ch_num + 1, len(root.children))
        self.assertTrue(ch_val in root.children)
        self.assertTrue(TreeNode(ch_val) in root.children)

    def test_tree_node_remove_child(self):
        root = TreeNode(None)
        ch_val = 'a'
        root.add_child(ch_val)
        self.assertTrue(ch_val in root.children)
        self.assertTrue(TreeNode(ch_val) in root.children)

        ch_num = len(root.children)
        root.remove_child(ch_val)
        self.assertEquals(ch_num - 1, len(root.children))
        self.assertTrue(ch_val not in root.children)
        self.assertTrue(TreeNode(ch_val) not in root.children)


if __name__ == '__main__':
    unittest.main()
