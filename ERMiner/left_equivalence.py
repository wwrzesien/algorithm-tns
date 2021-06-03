from typing import List, Set, Dict


class LeftEquivalence(object):
    """Left equivalence class"""
    def __init__(self, itemset_j: List, tids_j: Set, occurs_j: Dict, *args):
        self.itemset_j = itemset_j
        self.tids_j = tids_j
        self.occurs_j = occurs_j
        self.rules = [] # list of LeftRule
    
    def __str__(self):
        return 'EQ: {}'.format(self.itemset_j)

    def __eq__(self, obj: object):
        if obj is None:
            return False
        
        return self.itemset_j == obj.itemset_j


class LeftRule(object):
    """Rule member of a left equivalence class"""
    def __init__(self, itemset_i: List, tids_i: Set, tids_ij: Set, *args):
        self.itemset_i = itemset_i
        self.tids_i = tids_i
        self.tids_ij = tids_ij
        
    def __str__(self):
        return '{} ==> ...'.format(self.itemset_i) 
        