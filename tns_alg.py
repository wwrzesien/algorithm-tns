"""
Implementation based on 
https://www.philippe-fournier-viger.com/spmf/TopKNonRedundantSequentialRules.php
"""
import logging

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

        self.k_rules = "redblacktree"
        self.candidates = "redblacktree"

    def run_algorithm(self):
        "Main method"

        log.info("run_algorithm")

        # set minsup = 1 (will be increased by the algorithm progressively)
        self.min_supp_relative = 1

        # scan the database to count the occurrence of each item
        self.scan_database()

        # start the algorithm
        self.start()

        # if too many rules, we remove the extra rules
        self.clean_result()

        return self.k_rules

    def scan_database(self):
        "Scan the database to count the occurrence of each item"
        pass

    def start(self):
        "Start the algorithm"
        pass

    def clean_result(self):
        "If too many rules, we remove the extra rules"
        


        
