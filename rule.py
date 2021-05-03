"""
Sequential rule as a output by the TNS algorithm
https://www.philippe-fournier-viger.com/spmf/TopKNonRedundantSequentialRules.php
"""

class Rule(object):
    def __init__(self, *args):
        # antecedent
        self.itemset1 = []
        # consequent
        self.itemset2 = []
        # absolute support
        self.transaction_count = None
        # transaction IDS of the antecedent
        self.tids_i = set()
        # transaction IDS of the consequent
        self.tids_j = set()
        # transaction IDs of the sequences where the antecedent appears before the consequent
        self.tids_ij = set()
        # maps of first occurrences of the antecedent
        self.occurrences_i_first = {}
        # maps of last occurrences of the antecedent
        self.occurrences_j_last = {}
        # flag indicating if both left and right expansion should be explored from this rule
        self.expand_lr = False
        # confidence of the rule
        self.confidence = None

    def rule(self, itemset1, itemset2, confidence, transaction_count, tids_i, tids_j, tids_ij, occurrences_i_first, occurrences_j_last):
        self.itemset1 = itemset1
        self.itemset2 = itemset2
        self.transaction_count = transaction_count
        self.tids_i = tids_i
        self.tids_j = tids_j
        self.tids_ij = tids_ij
        self.occurrences_i_first = occurrences_i_first
        self.occurrences_j_last = occurrences_j_last
        self.confidence = confidence
    
    def get_absolute_support(self):
        """Return absolute support (number of sequences)"""
        return self.transaction_count

    def get_relative_support(self, sequence_count):
        """Return relative support (percentage)"""
        return self.transaction_count / sequence_count
        