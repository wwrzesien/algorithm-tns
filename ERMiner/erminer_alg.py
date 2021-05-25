"""
Implementation based on 
http://www.philippe-fournier-viger.com/spmf/ERMiner.php
"""
import logging
import math

from ERMiner.expand_left_store import ExpandLeftStore
from ERMiner.sparse_matrix import SparseMatrix
from ERMiner.left_equivalence import LeftEquivalence, LeftRule
from ERMiner.right_equivalence import RightEquivalence, RightRule
from typing import List, Set, Dict

log = logging.getLogger("erminer")
log.setLevel(logging.DEBUG)
log.propagate = False

class AlgorithmERMiner(object):
    """Implementation of ERMiner algorithm"""
    def __init__(self, database, min_conf, min_supp):
        super().__init__()
        self.db = database
        self.time_start = None
        self.time_end = None
        self.rule_count = 0
        self.min_conf = min_conf
        self.min_support = min_supp
        self.min_supp_relative = math.ceil(min_supp * len(database.database))
        self.map_item_count = {} # {item: {tid: {first_itemset: , last_itemset: }}}
        self.store = ExpandLeftStore()
        self.matrix = {} #SparseMatrix()
        self.total_candidate_count = 0
        self.candidate_prune_count = 0

        self.rules

    def run_algorithm(self):
        """Main method"""
        if self.min_supp_relative == 0:
            self.min_supp_relative = 1
        
        self.calc_frequency_of_items()
        self.generate_matrix()

        e_class_left = {} # item on the right: list of left rules
        e_class_right = {} # item on the left: list of right rules


        # item I: {item J: support of {i, j}}
        for key_i, value_i in self.matrix.items():
            occurs_i = self.map_item_count[key_i]
            tids_i = occurs_i.keys()

            for key_j, value_j in value_i.items():
                if value_j < self.min_supp_relative:
                    continue
                occurs_j = self.map_item_count[key_j]

                tids_ij = set()
                tids_ji = set()

                if len(occurs_i) < len(occurs_j):
                    self.calc_tidset_ij_and_ji(occurs_i, occurs_j, tids_ij, tids_ji)
                else:
                    self.calc_tidset_ij_and_ji(occurs_j, occurs_i, tids_ji, tids_ij)

                if len(tids_ji) >= self.min_supp_relative:
                    conf_ij = len(tids_ij) / len(occurs_i)

                    itemset_i = []
                    itemset_j = []

                    tids_j = occurs_j.keys()

                    if conf_ij >= self.min_conf:
                        self.save_rule(tids_ij, conf_ij, itemset_i, itemset_j)
                    self.register_rule_11(key_i, key_j, tids_i, tids_ij, occurs_i, occurs_j, e_class_left, e_class_right)
            
                if len(tids_ji) >= self.min_supp_relative:
                    itemset_i = []
                    itemset_j = []

                    conf_ji = len(tids_ji) / len(occurs_j)

                    tids_j = occurs_j.keys()

                    if conf_ji >- self.min_conf:
                        self.save_rule(tids_ji, conf_ji, itemset_j, itemset_i)
                    self.register_rule_11(key_j, key_i, tids_j, tids_i, tids_ji, occurs_j, occurs_i, e_class_left, e_class_right)

        for left_class in e_class_left.values():
            if len(left_class.rules) != 1:
                left_class.rules.sort(key=lambda r: r.itemset_i[0])
                self.expand_left(left_class)

        e_class_left = None

        for right_class in e_class_right.values():
            if len(right_class.rules) != 1:
                right_class.sort(key=lambda r: r.itemset_j[0])
                self.expand_right(right_class, True)
        
        e_class_right = None

        # TODO



    def calc_frequency_of_items(self):
        """Calculate the frequency of each item in one db"""
        self.map_item_count = {}

        for k, sequence in enumerate(self.db.database):
            for j, itemset in enumerate(sequence):
                for item_i in itemset:
                    if item_i not in self.map_item_count.keys():
                        occurs = {}
                        occurs[k] = {"first_itemset": j, "last_itemset": j}
                        self.map_item_count[item_i] = occurs
                    else:
                        occurs = self.map_item_count[item_i]
                        if k not in occurs.keys():
                            occurs[k] = {"first_itemset": j, "last_itemset": j}
                        else:
                            occurs[k]["last_itemset"] = j

    def generate_matrix(self):
        """Generate matrix"""
        for sequence in self.db.database:
            already_processed = set()
            for itemset_j in sequence:
                for item_k in itemset_j:
                    if item_k in already_processed or len(self.map_item_count[item_k]) < self.min_supp_relative:
                        continue

                    already_processed_with_respect_to_k = {}
                    for itemset_jj in sequence:
                        for item_kk in itemset_jj:
                            if item_kk == item_k or item_kk in already_processed_with_respect_to_k or len(self.map_item_count[item_k]) < self.min_supp_relative:
                                continue
                            self.increase_count_of_pair_in_matrix(item_k, item_kk)
                            already_processed_with_respect_to_k.add(item_kk)
                    already_processed.add(item_k)
    
    def increase_count_of_pair_in_matrix(self, i: int, j: int):
        """Increase count in matrix"""
        if i not in self.matrix.keys():
            self.matrix[i] = {j: 1}
        else:
            if j not in self.matrix[i].keys():
                self.matrix[i][j] = 1
            else:
                self.matrix[i][j] += 1

    def calc_tidset_ij_and_ji(self, occurs_i: Dict, occurs_j: Dict, tids_ij: Set[int], tids_ji: Set[int]):
        for tid, occ_i in occurs_i.items():
            if tid in occurs_j.keys():
                occ_j = occurs_j[tid]
                if occ_j.first_itemset < occ_i.last_itemset:
                    tids_ji.add(tid)
                
                if occ_i.first_itemset < occ_j.last_itemset:
                    tids_ij.add(tid)

    def save_rule(self, tids_ij: Set[int], conf_ij: int, itemset_i: List, itemset_j: List):
        """Save a rule I ==> J"""
        self.rule_count += 1
        rule = '{} ==> {} #SUP: {} #CONF: {}'.format(itemset_i, itemset_j, len(tids_ij), conf_ij)

        self.rules.append(rule)

    def register_rule_11(self, int_i: int, int_j: int, tids_i: Set[int], tids_j: Set[int], tids_ij: Set[int], tids_ji: Dict, occurs_i: Dict, occurs_j: Dict, eclass_left: Dict, eclass_right: Dict):
        """Register tule in the approriate equivalence classess"""
        
        if int_j not in eclass_left.keys():
            left_class = LeftEquivalence([int_j], tids_j, occurs_j)
            eclass_left[int_j] = left_class
        
        rule_l = LeftRule([int_i], tids_i, tids_ij)

        if int_i not in eclass_right.keys():
            right_class = RightEquivalence([int_i], tids_i, occurs_i)
            eclass_right[int_i] = right_class
        rule_r = RightRule([int_j], tids_j, tids_ij, occurs_j)

    def print_stats(self):
        """Print results"""
        for rule in self.rules:
            log.info(rule)


if __name__ == "__main__":
    pass
