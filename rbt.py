"""
Implementation of Red-Black Tree
https://www.programiz.com/dsa/red-black-tree
"""

import sys


class Node(object):
    def __init__(self, item, *args):
        self.item = item
        self.parent = None
        self.left = None
        self.right = None
        self.color = 1


class RedBlackTree(object):
    def __init__(self, *args):
        self.TNULL = Node(0)
        self.TNULL.color = 0
        self.TNULL.left = None
        self.TNULL.right = None
        self.root = self.TNULL

        # Number of elements currently in the tree
        self.size = 0   

    def left_rotate(self, Node: x):
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

    def right_rotate(self, Node: x):
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
        node.parent = None
        node.left = self.TNULL
        node.right = self.TNULL
        node.color = 1

        y = None
        x = self.root

        while x != self.TNULL:
            y = x
            if node.item < x.item:
                x = x.left
            else:
                x = x.right
        
        node.parent = y
        if y == None:
            self.root = node
        elif node.item < y.item:
            y.left = node
        else:
            y.right = node

        if node.parent == None:
            node.color = 0
            return 
        
        if node.parent.parent == None:
            return 

        self.fix_insert(node)

    def fix_insert(self, Node: k):
        """Balance the tree after insertion"""
        while k.parent.color == 1:
            if k.parent == k.parent.parent.right:
                u = k.parent.parent.left
                if u.color == 1:
                    u.color = 0
                    k.parent.color = 0
                    k.parent.parent.color = 1
                    k = k.parent.parent
                else:
                    if k == k.parent.left:
                        k = k.parent
                        self.right_rotate(k)
                    k.parent.color = 0
                    k.parent.parent.color = 1
                    self.left_rotate(k.parent.parent)
            else:
                u = k.parent.parent.right

                if u.color == 1:
                    u.color = 0
                    k.parent.color = 0
                    k.parent.parent.color = 1
                    k = k.parent.parent
                else:
                    if k == k.parent.right:
                        k = k.parent
                        self.left_rotate(k)
                    k.parent.color = 0
                    k.parent.parent.color = 1
                    self.right_rotate(k.parent.parent)
            if k == self.root:
                break
        self.root.color = 0

    def transplant(self, u, v):
        """Transplant a subtree"""
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
        
        y = z 
        y_orinal_color = y.color
        if z.left == self.TNULL:
            x = z.right
            self.transplant(z, z.right)
        elif z.right == self.TNULL:
            x = z.left
            self.transplant(z, z.left)
        else:
            y = self.mininum(z.right)
            y_orinal_color = y.color
            x = y.right
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
        if y_orinal_color == 0
            self.delete_fix(x)
        self.size -= 1

    def mininum(self, node):
        """Return node with minimum value"""
        while node.left != self.TNULL:
            node = node.left
        return node

    def maximum(self, node):
        """Return node with maximum value"""
        while node.right != self.TNULL:
            node = node.right
        return node

    def delete_fix(self, x):
        """Balancing the tree after deletion"""
        while x != self.root and x.color == 0:
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

                if s.right.color == 0 and s.right.color == 0:
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
        while y != self.TNULL and x == y.right:
            x = y
            y = y.parent
        return y

    def predecessor(self, x):
        """Return predecessor node of the node"""
        if x.left != self.TNULL:
            return self.minimum(x.left)

        y = x.parent
        while y != self.TNULL and x == y.left:
            x = y 
            y = y.parent
        return y

    def search(self, Node: node, key):
        """Search for element and return the node that contains this element"""
        z = self.TNULL
        while node != self.TNULL:
            if node.item == key:
                z = node
            if node.item <= key:
                node = node.right
            else:
                node = node.left
        return node



    def lower_node(self, key):
        """Return the node having the largest element having a value lower than a given element k"""
        pass

    def higher_node(sefl, k):
        """Return the node having the largest element having a value higher than a given element k"""
        pass

    def pop_minimum(self):
        """Return and remove the minimum element in the tree"""
        pass

    def pop_maximum(self):
        """Return and remove the maximum element in the tree"""
        pass





        
        
        