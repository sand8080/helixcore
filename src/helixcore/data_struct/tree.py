from copy import deepcopy

from helixcore.error import HelixcoreException


class Tree:
    def __init__(self, root=None):
        self.root = TreeNode(root)

    def __repr__(self):
        return '<Tree> root: %s' % self.root

    def add_chain(self, chain):
        '''
        chain is collection of elements to
        addint into tree like:
        [parent -> child of parent -> child of child of parent, etc.]
        '''
        node = self.root
        for el in chain:
            if not node.has_child(el):
                node.add_child(el)
            node = node.get_child(el)

    def walk_depth(self):
        return TreeNodeWalkDepthIter(self.root)


class TreeNodeWalkDepthIter:
    def __init__(self, node):
        self.node = node
        self.depth = 0

    def __iter__(self):
        return self.next()

    def next(self): #@ReservedAssignment
        def _next(n, depth):
            yield n.obj, depth
            for ch in n.children:
                for v in _next(ch, depth + 1):
                    yield v
        return _next(self.node, 0)


class TreeNodeNotFound(HelixcoreException):
    pass


class TreeNode:
    '''
    Obj wrapped by TreeNode should implement __eq__ method
    '''
    def __init__(self, obj, copy_obj=False):
        copy_fn = deepcopy if copy_obj else lambda x: x
        if isinstance(obj, self.__class__):
            self.obj = copy_fn(obj.obj)
        else:
            self.obj = copy_fn(obj)
        self.children = []

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.obj == other.obj
        else:
            return self.obj == other

    def __repr__(self):
        return '<TreeNode> obj: %s, children: %s' % (
            self.obj, self.children)

    def add_child(self, child):
        if self.has_child(child):
            return
        self.children.append(TreeNode(child))

    def remove_child(self, child):
        try:
            self.children.remove(child)
        except ValueError:
            pass

    def has_child(self, child):
        return child in self.children

    def get_child(self, obj):
        for ch in self.children:
            if ch==obj:
                return ch
        raise TreeNodeNotFound