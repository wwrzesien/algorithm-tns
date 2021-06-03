from typing import List, Set, Dict


class RightEquivalence(object):
    """Right equivalence class"""
    def __init__(self, itemset_i: List, tids_i: Set, occurs_i: Dict, *args):
        self.itemset_i = itemset_i
        self.tids_i = tids_i
        self.occurs_i = occurs_i
        self.rules = [] # list of RightRule
    
    def __str__(self):
        return 'EQ: {}'.format(self.itemset_i)

    def __eq__(self, obj):
        if obj is None:
            return False
        
        return self.itemset_i == obj.itemset_i


class RightRule(object):
    """Rule member of a right equivalence class"""
    def __init__(self, itemset_j: List, tids_j: Set, tids_ij: Set, occurs_j: Dict, *args):
        self.itemset_j = itemset_j
        self.tids_j = tids_j
        self.tids_ij = tids_ij
        self.occurs_j = occurs_j
        
    def __str__(self):
        return ' ==> {}'.format(self.itemset_j) 
        