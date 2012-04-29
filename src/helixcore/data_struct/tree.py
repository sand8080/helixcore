from copy import deepcopy

from helixcore.error import HelixcoreException


class Tree(object):
    def __init__(self, root=None):
        self.root = TreeNode(root)

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
        return TreeNodeDepthIter(self.root)


class TreeNodeDepthIter(object):
    def __init__(self, node):
        self.depth = 0
        self.node = node

    '''
    returns next object and current depth
    '''
    def next(self):
        pass


class TreeNodeNotFound(HelixcoreException):
    pass


class TreeNode(object):
    '''
    Obj wrapped by TreeNode should implement __eq__ method
    '''
    def __init__(self, obj):
        if isinstance(obj, self.__class__):
            self.obj = deepcopy(obj.obj)
        else:
            self.obj = deepcopy(obj)
        self.children = []

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.obj == other.obj
        else:
            return self.obj == other

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