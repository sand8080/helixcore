class Tree(object):
    def __init__(self, root=None):
        self.root = TreeNode(root)

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


class TreeNode(object):
    '''
    Obj wrapped by TreeNode should implement __eq__ method
    '''
    def __init__(self, obj):
        self.obj = obj
        self.children = []

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.obj == other.obj
        else:
            return self.obj == other

    def add_child(self, child):
        if isinstance(child, self.__class__):
            self.children.append(child)
        else:
            self.children.append(TreeNode(child))

    def remove_child(self, child):
        self.children.remove(child)

