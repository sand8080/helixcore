import unittest

from helixcore.data_struct.tree import Tree, TreeNode, TreeNodeNotFound
from helixcore.test.root_test import RootTestCase


class TreeNodeTestCase(RootTestCase):
    def test_eq(self):
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

    def test_no_copy_logic(self):
        l1 = [1, 2]
        n = TreeNode(l1)
        obj = n.obj
        self.assertEquals(l1, obj)
        l1.append(3)
        self.assertEquals(l1, obj)
        obj.append(4)
        self.assertEquals(l1, obj)

    def test_copy_logic(self):
        l1 = [1, 2]
        n = TreeNode(l1, copy_obj=True)
        obj = n.obj
        self.assertEquals(l1, obj)
        l1.append(3)
        self.assertNotEquals(l1, obj)

    def test_compare_with_obj(self):
        lh = TreeNode('aa')
        self.assertEquals(lh, 'aa')
        self.assertNotEquals(lh, 'aaa')

    def test_add_child(self):
        n = TreeNode(None)
        ch_val = 'a'
        ch_num = len(n.children)
        n.add_child(ch_val)
        self.assertEquals(ch_num + 1, len(n.children))
        self.assertTrue(ch_val in n.children)
        self.assertTrue(TreeNode(ch_val) in n.children)

    def test_add_child_no_duplicates(self):
        n = TreeNode(None)
        ch_num = len(n.children)
        ch = 'a'
        n.add_child(ch)
        self.assertEquals(ch_num + 1, len(n.children))
        n.add_child(ch)
        self.assertEquals(ch_num + 1, len(n.children))

    def test_remove_child(self):
        n = TreeNode(None)
        ch = 'a'
        n.add_child(ch)
        self.assertTrue(ch in n.children)
        self.assertTrue(TreeNode(ch) in n.children)

        ch_num = len(n.children)
        n.remove_child(ch)
        self.assertEquals(ch_num - 1, len(n.children))
        self.assertTrue(ch not in n.children)
        self.assertTrue(TreeNode(ch) not in n.children)

        ch = 'b'
        n.add_child(ch)
        ch_num = len(n.children)
        n.remove_child(TreeNode(ch))
        self.assertEquals(ch_num - 1, len(n.children))

    def test_remove_duplicate(self):
        n = TreeNode(None)
        ch = 'a'
        n.add_child(ch)
        ch_num = len(n.children)
        n.remove_child(ch)
        self.assertEquals(ch_num - 1, len(n.children))
        n.remove_child(ch)
        self.assertEquals(ch_num - 1, len(n.children))

    def test_has_child(self):
        n = TreeNode(1)
        n.add_child(1)
        n.add_child(2)
        self.assertTrue(n.has_child(1))
        self.assertTrue(n.has_child(TreeNode(1)))
        self.assertTrue(n.has_child(2))
        self.assertTrue(n.has_child(TreeNode(2)))

        self.assertFalse(n.has_child(3))
        self.assertFalse(n.has_child(TreeNode(3)))
        self.assertFalse(n.has_child(None))
        self.assertFalse(n.has_child(TreeNode(None)))

        n.add_child(None)
        self.assertTrue(n.has_child(None))
        self.assertTrue(n.has_child(TreeNode(None)))

    def test_node_get_child(self):
        t = TreeNode(None)
        t.add_child('a')
        t.add_child('b')
        t.add_child('c')
        ch = t.get_child('b')
        self.assertEquals('b', ch)
        self.assertEquals(TreeNode('b'), ch)
        self.assertEquals('b', ch.obj)

        ch = t.get_child(TreeNode('c'))
        self.assertEquals('c', ch)
        self.assertEquals(TreeNode('c'), ch)
        self.assertEquals('c', ch.obj)

        self.assertRaises(TreeNodeNotFound, t.get_child, None)
        self.assertRaises(TreeNodeNotFound, t.get_child, TreeNode(None))
        self.assertRaises(TreeNodeNotFound, t.get_child, 'd')
        self.assertRaises(TreeNodeNotFound, t.get_child, TreeNode('d'))


class TreeTestCase(RootTestCase):
    def test_add_chain(self):
        t = Tree()
        ch_0 = 'l1-1'
        ch_1 = 'l2-1'
        chain = [ch_0, ch_1]
        t.add_chain(chain)
        self.assertTrue(t.root.has_child(ch_0))
        self.assertTrue(t.root.get_child(ch_0).has_child(ch_1))


if __name__ == '__main__':
    unittest.main()
