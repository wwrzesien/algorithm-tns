"""
Implementation of Red-Black Tree
https://www.programiz.com/dsa/red-black-tree
"""

from TNS.rule import Rule


class Node(object):
    def __init__(self, item, *args):
        self.item = item
        self.parent = None
        self.left = None
        self.right = None
        self.color = 1
        
class RedBlackTree(Rule):
    def __init__(self, *args):
        super(Rule, self).__init__(*args)
        self.TNULL = Node(None)
        self.TNULL.color = 0
        self.TNULL.left = None
        self.TNULL.right = None
        self.root = self.TNULL

        # Number of elements currently in the tree
        self.size = 0
    
    def is_empty(self):
        """Check whether tree is empty"""
        return self.root == self.TNULL

    def left_rotate(self, x):
        """Perform a left rotate of a sub-tree"""
        y = x.right
        x.right = y.left
        if y.left != self.TNULL:
            y.left.parent = x

        y.parent = x.parent
        if x.parent == None:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    def right_rotate(self, x):
        """Perform a right rotate of a sub-tree"""
        y = x.left
        x.left = y.right
        if y.right != self.TNULL:
            y.right.parent = x

        y.parent = x.parent
        if x.parent == None:
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right = x
        x.parent = y

    def add(self, key):
        """Add an element to the tree"""
        node = Node(key)
        node.item = key
        # node.parent = None
        node.left = self.TNULL
        node.right = self.TNULL
        node.color = 1
        # y = self.TNULL
        y = None
        x = self.root

        while x != self.TNULL:
            y = x
            if node.item.compare(x.item) < 0:
                x = x.left
            else:
                x = x.right
        
        node.parent = y
        # if y == self.TNULL:
        if y == None:
            node.color = 0
            self.root = node
        elif node.item.compare(y.item) < 0:
            y.left = node
        else:
            y.right = node

        self.size += 1

        if node.parent == None:
            node.color = 0
            return 
        
        if node.parent.parent == None:
            return 
        
        
        self.fix_insert(node)

    def fix_insert(self, k):
        """Balance the tree after insertion"""
        while k.parent.color == 1:
            # if k.parent.item.equals(k.parent.parent.left.item):
            if k.parent == k.parent.parent.left:
                u = k.parent.parent.right
                if u.color == 1:
                    u.color = 0
                    k.parent.color = 0
                    k.parent.parent.color = 1
                    k = k.parent.parent
                else:
                    # if k.parent.right is not None and k.item.equals(k.parent.right.item):
                    if k == k.parent.right:
                        k = k.parent
                        self.left_rotate(k)
                    k.parent.color = 0
                    k.parent.parent.color = 1
                    self.right_rotate(k.parent.parent)
            else:
                u = k.parent.parent.left
                if u.color == 1:
                    u.color = 0
                    k.parent.color = 0
                    k.parent.parent.color = 1
                    k = k.parent.parent
                else:
                    # if k.item.equals(k.parent.right.item):
                    if k == k.parent.left:
                        k = k.parent
                        self.right_rotate(k)
                    k.parent.color = 0
                    k.parent.parent.color = 1
                    self.left_rotate(k.parent.parent)
            if k == self.root:
                break
        self.root.color = 0

    def transplant(self, u, v):
        """Transplant a subtree"""
        # if u.parent == self.TNULL:
        if u.parent == None:
            self.root = v
        elif u == u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        v.parent = u.parent

    def remove(self, key):
        """Remove an element from tree"""
        z = self.search(self.root, key)
        if z == self.TNULL:
            return
        
        self.perform_remove(z)
    
    def perform_remove(self, z):
        """Perform removal of an element"""
        y = z 
        y_orinal_color = y.color
        if z.left == self.TNULL:
            x = z.right
            self.transplant(z, z.right)
        elif z.right == self.TNULL:
            x = z.left
            self.transplant(z, z.left)
        else:
            y = self.minimum(z.right)
            y_orinal_color = y.color
            x = y.right
            # if y.parent.equals(z):
            if y.parent == z:
                x.parent = y
            else:
                self.transplant(y, y.right)
                y.right = z.right
                y.right.parent = y

            self.transplant(z, y)
            y.left = z.left
            y.left.parent = y
            y.color = z.color
        if y_orinal_color == 0:
            self.delete_fix(x)
        self.size -= 1

    def minimum(self, node=None):
        """Return node with minimum value"""
        flag = 0
        if node == None:
            node = self.root
            flag = 1
        while node.left != self.TNULL:
            node = node.left

        if flag:
            return node.item
        return node

    def maximum(self, node=None):
        """Return node with maximum value"""
        if node == None:
            node = self.root
            flag = 1
        while node.right != self.TNULL:
            node = node.right
        
        if flag:
            return node.item
        return node

    def delete_fix(self, x):
        """Balancing the tree after deletion"""
        while x != self.root and x.color == 0:
            # if x.equals(x.parent.left):
            if x == x.parent.left:
                s = x.parent.right
                if s.color == 1:
                    s.color = 0
                    x.parent.color = 1
                    self.left_rotate(x.parent)
                    s = x.parent.right
                
                if s.left.color == 0 and s.right.color == 0:
                    s.color = 1
                    x = x.parent
                else:
                    if s.right.color == 0:
                        s.left.color = 0
                        s.color = 1
                        self.right_rotate(s)
                        s = x.parent.right
                    
                    s.color = x.parent.color
                    x.parent.color = 0
                    s.right.color = 0
                    self.left_rotate(x.parent)
                    x = self.root
            else:
                s = x.parent.left
                if s.color == 1:
                    s.color = 0
                    x.parent.color = 1
                    self.right_rotate(x.parent)
                    s = x.parent.left

                if s.right.color == 0 and s.left.color == 0:
                    s.color = 1
                    x = x.parent
                else:
                    if s.left.color == 0:
                        s.right.color = 0
                        s.color = 1
                        self.left_rotate(s)
                        s = x.parent.left

                    s.color = x.parent.color
                    x.parent.color = 0
                    s.left.color = 0
                    self.right_rotate(x.parent)
                    x = self.root
        x.color = 0

    def successor(self, x):
        """Return successor node of the node"""
        if x.right != self.TNULL:
            return self.minimum(x.right)
        
        y = x.parent
        # while y != self.TNULL and x.equals(y.right):
        while y != self.TNULL and x == y.right:
            x = y
            y = y.parent
        return y

    def predecessor(self, x):
        """Return predecessor node of the node"""
        if x.left != self.TNULL:
            return self.minimum(x.left)

        y = x.parent
        # while y != self.TNULL and x.equals(y.left):
        while y != self.TNULL and x == y.left:
            x = y 
            y = y.parent
        return y

    def search(self, node, k):
        """Search for element and return the node that contains this element"""
        while node != self.TNULL and k != node.item:
            if k.compare(node.item) < 0:
                node = node.left
            else:
                node = node.right
        return node

    def lower_node(self, k):
        """Return the node having the largest element having a value lower than a given element k"""
        x = self.root
        while x != self.TNULL:
            if k.compare(x.item) > 0:
                if x.right != self.TNULL:
                    x = x.right
                else:
                    return x
            else:
                if x.left != self.TNULL:
                    x = x.left
                else:
                    current = x
                    while current.parent != None and current.parent.left == current:
                        current = current.parent
                    return current.parent
        return None

    def higher_node(self, k):
        """Return the node having the largest element having a value higher than a given element k"""
        x = self.root
        while x != self.TNULL:
            if k.compare(x.item) < 0:
                if x.left != self.TNULL:
                    x = x.left
                else:
                    return x
            else:
                if x.right != self.TNULL:
                    x = x.right
                else:
                    current = x
                    while current.parent != None and current.parent.right == current:
                        current = current.parent
                    return current.parent
        return None

    def pop_minimum(self):
        """Return and remove the minimum element in the tree"""
        if self.root == self.TNULL:
            return None
        x = self.root
        while x.left != self.TNULL:
            x = x.left
        v = x.item
        self.perform_remove(x)
        return v

    def pop_maximum(self):
        """Return and remove the maximum element in the tree"""
        if self.root == self.TNULL:
            return None
        x = self.root
        while x.right != self.TNULL:
            x = x.right
        v = x.item
        self.perform_remove(x)
        return v

    def pre_order(self, node):
        if node != self.TNULL:
            node.item.print_stats()
            self.pre_order(node.left)
            self.pre_order(node.right)


if __name__ == "__main__":
    bst = RedBlackTree()

    print(bst.is_empty())

    rule1 = Rule()
    rule1.rule([1], [2], 4, 6, "w", "w", "d", "v", 7)
    bst.add(rule1)


        
        
        