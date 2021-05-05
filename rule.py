"""
Sequential rule as a output by the TNS algorithm
https://www.philippe-fournier-viger.com/spmf/TopKNonRedundantSequentialRules.php
"""

import logging

log = logging.getLogger("tns")
log.setLevel(logging.DEBUG)
log.propagate = False

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
        
    def to_string(self):
        """Get a string representation of the rule"""
        line = ""
        for idx, item in enumerate(self.itemset1):
            line += "{}".format(item)
            if idx != len(self.itemset1)-1:
                line += ","
        line += " ==> "
        for idx, item in enumerate(self.itemset2):
            line += "{}".format(item)
            if idx != len(self.itemset2)-1:
                line += ","
        return line

    def print_stats(self):
        string = "{} #SUP: {} #CONF: {}".format(self.to_string(), self.get_absolute_support(), self.confidence)
        # log.info(string)
        print(string)

    def compare(self, o):
        """Compare rules, 0 if equal, 0< if smaller, >0 if larger"""
        if o is self:
            return 0

        compare = self.transaction_count - o.transaction_count
        if compare != 0:
            return compare

        itemset1_sizeA = 0 if self.itemset1 == None else len(self.itemset1)
        itemset1_sizeB = 0 if o.itemset1 == None else len(o.itemset1)
        compare2 = itemset1_sizeA - itemset1_sizeB
        if compare2 != 0:
            return compare2

        itemset2_sizeA = 0 if self.itemset2 == None else len(self.itemset2)
        itemset2_sizeB = 0 if o.itemset2 == None else len(o.itemset2)
        compare3 = itemset2_sizeA - itemset2_sizeB
        if compare3 != 0:
            return compare3
        
        compare4 = self.confidence - o.confidence
        if compare4 != 0:
            return compare4
        
        return 0

    def equals(self, o):
        """Check if rule is equal to another (if they have the same items in their antecedent and consequent)"""
        if o is None:
            return False
        if len(o.itemset1) != len(self.itemset1):
            return False
        if len(o.itemset2) != len(self.itemset2):
            return False
        
        for idx, item in enumerate(self.itemset1):
            if item != o.itemset1[idx]:
                return False
        for idx, item in enumerate(self.itemset2):
            if item != o.itemset2[idx]:
                return False

        return True
        


if __name__ == "__main__":
    rule = Rule()
    rule.rule([1,2],[3],3, None, None, None, None, None, None)

    print(rule.to_string())
    print(rule.compare(rule))