import logging
from typing import List, Set, Dict

from ERMiner.left_equivalence import LeftEquivalence

log = logging.getLogger("erminer")
log.setLevel(logging.DEBUG)
log.propagate = False


class ExpandLeftStore(object):
    """LeftStore structure used by the ERMiner algorithm"""
    def __init__(self):
        self.store = {}

    def register(self, leftRule, itemset_j: List, tids_j: Set[int], occurs_i: Dict, occurs_j:Dict):
        size = len(itemset_j)
        hash_itemset_j = hash(tuple(itemset_j))

        if size not in self.store.keys():
            self.store[size] = {}
        
        if hash_itemset_j not in self.store[size].keys():
            eclass = LeftEquivalence(itemset_j, tids_j, occurs_j)
            self.store[size][hash_itemset_j] = [eclass]
            eclass.rules.append(leftRule)
        else:
            for eclass in self.store[size][hash_itemset_j]:
                if eclass.itemset_j == itemset_j:
                    eclass.rules.append(leftRule)
                    return
            eclass = LeftEquivalence(itemset_j, tids_j, occurs_j)
            self.store[size][hash_itemset_j].append(eclass)
            eclass.rules.append(leftRule)

