"""
Implementation based on 
http://www.philippe-fournier-viger.com/spmf/ERMiner.php
"""
import logging
import math
# from db import Database
from expand_left_store import ExpandLeftStore
from sparse_matrix import SparseMatrix

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
        self.min_supp_relative = math.ceil(min_supp * len(database))
        self.map_item_count = {} # item: {tid: occurence}
        self.expand_left_store = ExpandLeftStore()
        self.matrix = {1:{}} #SparseMatrix()
        self.total_candidate_count = 0
        self.candidate_prune_count = 0

    def run_algorithm(self):
        """Main method"""
        if self.min_supp_relative == 0:
            self.min_supp_relative = 1
        
        self.calc_frequency_of_items()
        self.generate_matrix()

        e_class_left = {} # item on the right: list of rules
        e_class_right = {} # item on the left: list of rules


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
                    self.register_rule(key_i, key_j, )


    def calc_frequency_of_items(self):
        pass

    def generate_matrix(self):
        pass

    def calc_tidset_ij_and_ji(self, occurs_i, occurs_j, tids_ij, tids_ji):
        pass