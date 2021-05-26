"""
Implementation based on 
http://www.philippe-fournier-viger.com/spmf/ERMiner.php
"""
import logging
import math
from typing import List, Set, Dict

from ERMiner.expand_left_store import ExpandLeftStore
from ERMiner.left_equivalence import LeftEquivalence, LeftRule
from ERMiner.right_equivalence import RightEquivalence, RightRule


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
        self.min_supp_relative = min_supp 
        self.map_item_count = {} # {item: {tid: {first_itemset: , last_itemset: }}}
        self.store = ExpandLeftStore()
        self.matrix = {}
        self.total_candidate_count = 0
        self.candidate_prune_count = 0

        self.rules = []

    def run_algorithm(self):
        """Main method"""
        log.info("Run algorithm")
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

                if len(tids_ij) >= self.min_supp_relative:
                    conf_ij = len(tids_ij) / len(occurs_i)

                    itemset_i = [key_i]
                    itemset_j = [key_j]

                    tids_j = occurs_j.keys()

                    if conf_ij >= self.min_conf:
                        self.save_rule(tids_ij, conf_ij, itemset_i, itemset_j)
                    self.register_rule_11(key_i, key_j, tids_i, tids_j, tids_ij, occurs_i, occurs_j, e_class_left, e_class_right)
            
                if len(tids_ji) >= self.min_supp_relative:
                    itemset_i = [key_i]
                    itemset_j = [key_j]

                    conf_ji = len(tids_ji) / len(occurs_j)

                    tids_j = occurs_j.keys()

                    if conf_ji >= self.min_conf:
                        self.save_rule(tids_ji, conf_ji, itemset_j, itemset_i)
                    self.register_rule_11(key_j, key_i, tids_j, tids_i, tids_ji, occurs_j, occurs_i, e_class_left, e_class_right)

        for left_class in e_class_left.values():
            if len(left_class.rules) != 1:
                left_class.rules.sort(key=lambda r: r.itemset_i[0])
                self.expand_left(left_class)

        e_class_left = None

        for right_class in e_class_right.values():
            if len(right_class.rules) != 1:
                right_class.rules.sort(key=lambda r: r.itemset_j[0])
                self.expand_right(right_class, True)
        
        e_class_right = None

        for m in self.store.store.values():
            for eclass_list in m.values():
                for eclass in eclass_list:
                    if len(eclass.rules) != 1:
                        eclass.rules.sort(key=lambda r: r.itemset_i[len(r.itemset_i) -1])
                        self.expand_left(eclass)

    def expand_left(self, eclass):
        for w in range(len(eclass.rules)-1):
            rule_1 = eclass.rules[w]
            d = rule_1.itemset_i[len(rule_1.itemset_i)-1]

            rules_for_recursion = LeftEquivalence(eclass.itemset_j, eclass.tids_j, eclass.occurs_j)

            for m in range(w+1, len(eclass.rules)):
                rule_2 = eclass.rules[m]
                c = rule_2.itemset_i[len(rule_2.itemset_i)-1]
                try:
                    matrix_count = self.matrix[c][d]
                except KeyError:
                    matrix_count = 0
                if matrix_count < self.min_supp_relative:
                    self.candidate_prune_count += 1
                    self.total_candidate_count += 1
                    continue
                self.total_candidate_count += 1

                tids_ic = set()
                map_c = self.map_item_count[c]

                if len(rule_1.tids_i) < len(map_c):
                    remains = len(rule_1.tids_i)
                    for tid in rule_1.tids_i:
                        if tid in map_c.keys():
                            tids_ic.add(tid)
                        remains -= 1
                        
                        if len(tids_ic) + remains < self.min_supp_relative:
                            break
                else:
                    remains = len(map_c)
                    for tid in map_c.keys():
                        if tid in rule_1.tids_i:
                            tids_ic.add(tid)
                        remains -= 1
                        
                        if len(tids_ic) + remains < self.min_supp_relative:
                            break

                tids_ic_j = set()
                if len(rule_1.tids_ij) < len(map_c):
                    for tid in rule_1.tids_ij:
                        if tid in map_c.keys():
                            occur_c = map_c[tid]
                            occur_j =  eclass.occurs_j[tid]
                            if occur_c["first_itemset"] < occur_j["last_itemset"]:
                                tids_ic_j.add(tid)
                else:
                    for tid, occur_c in map_c.items():
                        if tid in rule_1.tids_ij:
                            occur_j = eclass.occurs_j[tid]
                            if occur_c['first_itemset'] < occur_j['last_itemset']:
                                tids_ic_j.add(tid)
                
                if len(tids_ic_j) >= self.min_supp_relative:
                    conf_ic_j = len(tids_ic_j) / len(tids_ic)
                    itemset_ic = rule_1.itemset_i.copy()
                    itemset_ic.append(c)

                    new_rule = LeftRule(itemset_ic, tids_ic, tids_ic_j)

                    if conf_ic_j >= self.min_conf:
                        self.save_rule(tids_ic_j, conf_ic_j, itemset_ic, eclass.itemset_j)
                    
                    rules_for_recursion.rules.append(new_rule)
            
            if len(rules_for_recursion.rules) > 1:
                self.expand_left(rules_for_recursion)
    
    def expand_right(self, eclass, first_time):
        for w in range(len(eclass.rules)-1):
            rule_1 = eclass.rules[w]
            d = rule_1.itemset_j[len(rule_1.itemset_j)-1]
            rules_for_recursion = RightEquivalence(eclass.itemset_i, eclass.tids_i, eclass.occurs_i)

            for m in range(w+1, len(eclass.rules)):
                rule_2 = eclass.rules[m]
                c = rule_2.itemset_j[len(rule_2.itemset_j)-1]
                try:
                    matrix_count = self.matrix[c][d]
                except KeyError:
                    matrix_count = 0
                if matrix_count < self.min_supp_relative:
                    self.candidate_prune_count += 1
                    self.total_candidate_count += 1
                    continue
                self.total_candidate_count += 1

                tids_i_jc = set()
                map_c = self.map_item_count[c]

                if len(rule_1.tids_ij) < len(map_c):
                    remains = len(rule_1.tids_ij)
                    for tid in rule_1.tids_ij:
                        if tid in map_c.keys():
                            occur_c = map_c[tid]
                            occur_i = eclass.occurs_i[tid]
                            if occur_c['last_itemset'] > occur_i['first_itemset']:
                                tids_i_jc.add(tid)
                        remains -= 1
                        if len(tids_i_jc) + remains < self.min_supp_relative:
                            break
                else:
                    remains = len(map_c)
                    for tid, occur_c in map_c.items():
                        if tid in rule_1.tids_ij:
                            occur_i = eclass.occurs_i[tid]
                            if occur_c['last_itemset'] > occur_i['first_itemset']:
                                tids_i_jc.add(tid)
                    remains -= 1
                    if len(tids_i_jc) + remains < self.min_supp_relative:
                        break
                
                if len(tids_i_jc) >= self.min_supp_relative:
                    tids_jc = set()
                    occurs_jc = {}
                    if len(rule_1.tids_j) < len(map_c):
                        for tid in rule_1.tids_j:
                            if tid in map_c.keys():
                                tids_jc.add(tid)

                                occur_j = rule_1.occurs_j[tid]
                                if occur_c['last_itemset'] < occur_j['last_itemset']:
                                    occurs_jc[tid] = occur_c
                                else:
                                    occurs_jc[tid] = occur_j
                    else:
                        for tid, occur_c in map_c.items():
                            if tid in rule_1.tids_j:
                                tids_jc.add(tid)
                                occur_j = rule_1.occurs_j[tid]
                                if occur_c['last_itemset'] < occur_j['last_itemset']:
                                    occurs_jc[tid] = occur_c
                                else:
                                    occurs_jc[tid] = occur_j
                    
                    conf_i_jc = len(tids_i_jc) / len(eclass.tids_i)
                    itemset_jc = rule_1.itemset_j.copy()
                    itemset_jc.append(c)

                    if conf_i_jc >= self.min_conf:
                        self.save_rule(tids_i_jc, conf_i_jc, eclass.itemset_i, itemset_jc)
                    
                    right_rule = RightRule(itemset_jc, tids_jc, tids_i_jc, occurs_jc)

                    rules_for_recursion.rules.append(right_rule)

                    left_rule = LeftRule(eclass.itemset_i, eclass.tids_i, tids_i_jc)
                    self.store.register(left_rule, itemset_jc, tids_jc, eclass.occurs_i, occurs_jc)
            
            if len(rules_for_recursion.rules) > 1:
                self.expand_right(rules_for_recursion, False)
                            

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

                    already_processed_with_respect_to_k = set()
                    for itemset_jj in sequence:
                        for item_kk in itemset_jj:
                            if item_kk == item_k or item_kk in already_processed_with_respect_to_k or len(self.map_item_count[item_kk]) < self.min_supp_relative:
                                continue
                            self.increase_count_of_pair_in_matrix(item_k, item_kk)
                            already_processed_with_respect_to_k.add(item_kk)
                    already_processed.add(item_k)
    
    def increase_count_of_pair_in_matrix(self, i: int, j: int):
        """Increase count in matrix"""
        if i < j:
            return

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
                if occ_j['first_itemset'] < occ_i['last_itemset']:
                    tids_ji.add(tid)
                
                if occ_i['first_itemset'] < occ_j['last_itemset']:
                    tids_ij.add(tid)

    def save_rule(self, tids_ij: Set[int], conf_ij: int, itemset_i: List, itemset_j: List):
        """Save a rule I ==> J"""
        self.rule_count += 1
        rule = {
            "i": itemset_i,
            "j": itemset_j,
            "sup": len(tids_ij),
            "conf": conf_ij
        }
        self.rules.append(rule)

    def register_rule_11(self, int_i: int, int_j: int, tids_i: Set[int], tids_j: Set[int], tids_ij: Set[int], occurs_i: Dict, occurs_j: Dict, eclass_left: Dict, eclass_right: Dict):
        """Register tule in the approriate equivalence classess"""
        
        if int_j not in eclass_left.keys():
            left_class = LeftEquivalence([int_j], tids_j, occurs_j)
            eclass_left[int_j] = left_class
        else:
            left_class = eclass_left[int_j]
        rule_l = LeftRule([int_i], tids_i, tids_ij)
        left_class.rules.append(rule_l)

        if int_i not in eclass_right.keys():
            right_class = RightEquivalence([int_i], tids_i, occurs_i)
            eclass_right[int_i] = right_class
        else:
            right_class = eclass_right[int_i]
        rule_r = RightRule([int_j], tids_j, tids_ij, occurs_j)
        right_class.rules.append(rule_r)

    def print_stats(self):
        """Print results"""
        log.info("")
        log.info("------- ERMiner stats --------")
        log.info("Minsup: {}".format(self.min_support))
        log.info("Sequential rules count: {}".format(len(self.rules)))
        log.info("")
        for r in self.rules:
            rule = '{} ==> {} #SUP: {} #CONF: {}'.format(r["i"], r["j"], r["sup"], r["conf"])
            log.info('{}'.format(rule))

    def get_results(self):
        """Return results in dict form: {"i": , "j": , "sup": , "conf": }"""
        return self.rules

if __name__ == "__main__":
    pass
