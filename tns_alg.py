"""
Implementation based on 
https://www.philippe-fournier-viger.com/spmf/TopKNonRedundantSequentialRules.php
"""
import logging
from rbt import RedBlackTree

log = logging.getLogger("tns")
log.setLevel(logging.DEBUG)
log.propagate = False


class ALgorithmTNS(object):
    "Implementation of k-top non-redundant sequential algorithm"
    def __init__(self, k, min_conf, delta, database, *args):
        self.k = k + delta
        self.min_conf = min_conf
        self.delta = delta
        self.init_k = k
        self.database = database
        
        self.time_start = 0
        self.time_end = 0
        self.init_delta = 0
        self.min_supp_relative = 0
        self.max_candidate_count = 0
        self.item_count_first = {}
        self.item_count_last = {}

        self.k_rules = RedBlackTree()
        self.candidates = RedBlackTree()

    def run_algorithm(self):
        "Main method"

        log.info("run_algorithm")

        # set minsup = 1 (will be increased by the algorithm progressively)
        self.min_supp_relative = 1

        # scan the database to count the occurrence of each item
        self.scan_database()

        print(self.item_count_first)
        print(self.item_count_last)
        # print(self.k_rules.size)

        # start the algorithm
        self.start()

        # if too many rules, we remove the extra rules
        # self.clean_result()

        return self.k_rules

    def scan_database(self):
        "Scan the database to count the occurrence of each item"
        for tid, sequence in enumerate(self.database):
            for j, itemset in enumerate(sequence):
                for i, item in enumerate(itemset):
                    # 
                    if item not in self.item_count_first.keys():
                        self.item_count_first[item] = {}
                        self.item_count_last[item] = {}
                    if tid not in self.item_count_first[item].keys():
                        self.item_count_first[item][tid] = j
                        self.item_count_last[item][tid] = j
                    else:
                        self.item_count_last[item][tid] = j


    def start(self):
        "Start the algorithm"
        pass        

    def clean_result(self):
        "Remove the extra rules if there are too many rules"
        while self.k_rules.size > self.init_k:
            self.k_rules.pop_minimum()
        self.min_supp_relative = self.k_rules.minimum().get_absolute_support()
        
if __name__ == "__main__":
    TEST_DB = [
        ([1], [1,2,3], [1,3], [4], [3,6]),
        ([1,4], [3], [2,3], [1,5]),
        ([5,6], [1,2], [4,6], [3], [2]),
        ([5], [7], [1,6], [3], [2], [3])
    ]
    k = 30
    min_conf = 0.5
    delta = 2

    tns = ALgorithmTNS(k=k, min_conf=min_conf, delta=delta, database=TEST_DB)

    tns.run_algorithm()

            

