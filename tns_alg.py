"""
Implementation based on 
https://www.philippe-fournier-viger.com/spmf/TopKNonRedundantSequentialRules.php
"""
import logging
from rbt import RedBlackTree
from rule import Rule

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
        self.db = database
        
        self.time_start = 0
        self.time_end = 0
        self.init_delta = 0
        self.min_supp_relative = 0
        self.max_candidate_count = 0
        self.item_count_first = {}
        self.item_count_last = {}

        self.total_removed_count = None
        self.not_added = None

        self.k_rules = RedBlackTree()
        self.candidates = RedBlackTree()

    def run_algorithm(self):
        "Main method"

        self.total_removed_count = 0
        self.not_added = 0

        log.info("Run algorithm")

        # set minsup = 1 (will be increased by the algorithm progressively)
        self.min_supp_relative = 1

        # scan the database to count the occurrence of each item
        self.scan_database()

        # print(self.item_count_first)
        # print(self.item_count_last)
        # print(self.k_rules.size)

        # start the algorithm
        self.start()

        # if too many rules, we remove the extra rules
        self.clean_result()

        return self.k_rules

    def scan_database(self):
        "Scan the database to count the occurrence of each item"
        for tid, sequence in enumerate(self.db.database):
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
        """Start the algorithm"""

        # We will now try to generate rules with one item in the
		# antecedent and one item in the consequent using
		# frequent items.

        # for each pair of frequent items i and j such that i != j
        # main1
        for item_i in range(self.db.min_item, self.db.max_item + 1):
            # get the map of accurences of item I
            if item_i not in self.item_count_first.keys():
                continue # continue main1 TODO Good
            occurrences_i_first = self.item_count_first[item_i]

            # get the set of sequence IDs containing I
            tids_i = set(occurrences_i_first.keys())
            # if the support of I (cardinality of the tids) is lower
            # than minsup, than it is not frequnt, so we skip this item
            if len(tids_i) < self.min_supp_relative:
                continue # continue main1 TODO Good
            
            # main2
            for item_j in range(item_i + 1, self.db.max_item + 1):
                flag = True
                # get the map of occurences of item J
                if item_j not in self.item_count_first.keys():
                    continue # continue main2 TODO Good
                occurrences_j_first = self.item_count_first[item_j]

                # get the set of sequences IDs containing J
                tids_j = set(occurrences_j_first.keys())
                # if the support of J (cardinality of the tids) is lower
                # than minsup, than it is not frequnt, so we skip this item
                if len(tids_j) < self.min_supp_relative:
                    continue # continue main2 TODO Good

                # (1) Build list of common tids and current occurences
                # of i ==> j and j ==> i
                tids_ij = set()
                tids_ji = set()

                # These maps will store the last occurence of I
                # and last occurence of J for each sequnce ID (tid)
                # key: tid   value: itemset position
                occurrences_j_last = self.item_count_last[item_j]
                occurrences_i_last = self.item_count_last[item_i]

                #  if there is less tids in J then
                # we will loop over J instead of I to calculate the tidsets
                if len(tids_i) > len(tids_j):
                    # this represents the number of itemsets left to be scanned
                    left = len(tids_j)

                    # for each tid where J appears
                    for tid in set(occurrences_j_first.keys()):
                        # get the first occurence of I
                        if tid in occurrences_i_first.keys():
                            occ_i_first = occurrences_i_first[tid]
                            # get the first and last occurences of J
                            occ_j_first = occurrences_j_first[tid]
                            occ_j_last = occurrences_j_last[tid]
                            # if the first of I appears before the last of J
                            if occ_i_first < occ_j_last:
                                tids_ij.add(tid)
                            
                            occ_i_last = occurrences_i_last[tid]
                            # if the first of J appears before the last of I
                            if occ_j_first < occ_i_last:
                                tids_ji.add(tid)

                        # go to next itemset (in backward direction)
                        left -= 1

                        # if there is not enough itemset left so that i --> j
                        # or j ==> i could be frequent then we can stop
                        if (left + len(tids_ij) < self.min_supp_relative) and (left + len(tids_ji) < self.min_supp_relative):
                            flag = False
                            break # continue main2 TODO good
                else:
                    # otherwise we will loop over I instead of J to calculate the tidsets

                    # number of itemsets left to be scanned
                    left = len(tids_i)
                    for tid in set(occurrences_i_first.keys()):
                        # get the first occurence of J
                        if tid in occurrences_j_first.keys():
                            occ_j_first = occurrences_j_first[tid]
                            # get the first and last occurences of I
                            occ_i_first = occurrences_i_first[tid]
                            occ_i_last = occurrences_i_last[tid]
                            # if the first of J appears before the ast of I
                            if occ_j_first < occ_i_last:
                                # current tid to the tidset of j ==> i
                                tids_ji.add(tid)

                            occ_j_last = occurrences_j_last[tid]
                            # if the first of I appearss before the last of J
                            if occ_i_first < occ_j_last:
                                tids_ij.add(tid)
                        
                        # go to net itemset (in backward direction)
                        left -= 1

                        # if there is not enough itemset left so that i --> j
                        # or j ==> i could be frequent then we can stop
                        if (left + len(tids_ij) < self.min_supp_relative) and (left + len(tids_ji) < self.min_supp_relative):
                            flag = False
                            break # continue main2 TODO good
                        
                # (2) check if the two itemset have enouh common tids
                # if not, we dont need to generate a rule for them
                # create rule IJ
                if flag:
                    sup_ij = len(tids_ij)
                    # if the rule I ==> J is frequent
                    print(sup_ij)
                    if sup_ij >= self.min_supp_relative:
                        # create the rule
                        conf_ij = len(tids_ij) / len(occurrences_i_first)
                        
                        rule_ij = Rule()
                        rule_ij.rule([item_i], [item_j], conf_ij, sup_ij, tids_i, tids_j, tids_ij, occurrences_i_first, occurrences_j_last)
                        print(rule_ij.itemset1)
                        # if the rule is valid
                        if conf_ij >= self.min_conf:
                            # save the rule to current top k list
                            print('przed save1')
                            self.save(rule_ij, sup_ij)
                            print('po save1')

                        # register the rule as candidate for the future left and right expansions
                        self.register_as_candidate(True, rule_ij)
                        print('po register1')

                    sup_ji = len(tids_ji)
                    # if the rule J ==> I is frequent
                    if sup_ji >= self.min_supp_relative:
                        # create the rule
                        conf_ji = len(tids_ji) / len(occurrences_j_first)

                        rule_ji = Rule()
                        rule_ji.rule([item_j], [item_i], conf_ji, sup_ji, tids_j, tids_i, tids_ji, occurrences_j_first, occurrences_i_last)

                        # ig the rule is valid
                        if conf_ji >= self.min_conf:
                            # save the rule to the current top k list
                            self.save(rule_ji, sup_ji)
                            print('po save2')
                        
                        # register the rule as candidate for the future left and right expansions
                        self.register_as_candidate(True, rule_ji)
                        print('po register2')
        print('przed while')
        # Now we have finished checking all the rules containing 1 item
	    # in the left side and 1 in the right side,
	    # the next step is to recursively expand rules in the set 
	    # "candidates" to find more rules.
        print('K-rules drzewo')
        self.k_rules.pre_order(self.k_rules.root)
        print("candidates drzewo")
        self.candidates.pre_order(self.candidates.root)
        while not self.candidates.is_empty():
            print(self.candidates.size)
            print("candidates drzewo")
            self.candidates.pre_order(self.candidates.root)
            #  take the rule with the highest support first
            rule = self.candidates.pop_maximum()
            if rule.get_absolute_support() < self.min_supp_relative:
                break
            # otherwise, we try to expand the rule
            if rule.expand_lr:
                self.expand_l(rule)
                self.expand_r(rule)
            else:
                # If the rule should only be expanded by left side to
				# avoid generating redundant rules, then we 
				# only expand the left side.
                expand_l(rule)


    def save(self, rule, support):
        """Save rule in the current top k set"""
        
        # we get a pointer to the node in the red black tree for the 
        # rule having support jus lower than support + 1
        tmp_node = Rule()
        tmp_node.rule(None, None, 0, support+1, None, None, None, None, None)
        lower_rule_node = self.k_rules.lower_node(tmp_node)

        # print("info o drzewie")
        # if self.k_rules.size > 0:
        #     self.k_rules.pre_order(self.k_rules.root)
        # print(type(lower_rule_node))
        # print(lower_rule_node is None)
        # if lower_rule_node is not None and lower_rule_node.item is not None:
        #     print(lower_rule_node)
        #     print(lower_rule_node.item.print_stats())

        # applying strategy 1 and strategy 2
        rules_to_delete = set()

        # for each rule "lower_rule_node" having the same support as the rule received as parameter
        while lower_rule_node is not None and lower_rule_node.item is not None and lower_rule_node.item.get_absolute_support() == support:
            print('while w save')
            # Strategy 1:
            # if the confidence is the same and the rule "lower_rule_node" subsume the new rule
            # then we dont add the new rule
            # print(rule.confidence)
            # print(lower_rule_node.item.confidence)
            # print(self.subsume(lower_rule_node.item, rule))
            if rule.confidence == lower_rule_node.item.confidence and self.subsume(lower_rule_node.item, rule):
                self.not_added += 1
                return

            # Strategy 2:
            # if the confidence is the same and the rule "lower_rule_node" subsume the new rule
            # then we dont add the new rule
            if rule.confidence == lower_rule_node.item.confidence and self.subsume(rule, lower_rule_node.item):
                # add rule to the set of rules to be deleted
                rules_to_delete.add(lower_rule_node.item)
                self.total_removed_count += 1
            
            # check the next rule
            lower_rule_node = self.k_rules.lower_node(lower_rule_node.item)
            # print(lower_rule_node.item.print_stats())
        
        # delete rules to be deleted
        for r in rules_to_delete:
            self.k_rules.remove(r)
        
        # now the rule has passed the test of Straategy 1 already
        # so we add it to the set of top k rules
        # print("dodajemy rule")
        # print(rule.print_stats())
        self.k_rules.add(rule)
        # if there is more than k rules
        if self.k_rules.size > self.k:
            # and if the support of the rule is higher than minsup
            if support > self.min_supp_relative:
                # recursively find the rule with the lowest support and remove it
                # until there is just k rules left
                tmp_rule = Rule()
                tmp_rule.rule(None, None, 0, self.min_supp_relative+1, None, None, None, None, None)
                
                i = 0
                while self.k_rules.size > self.k or i == 0:
                    i = 1
                    lower = self.k_rules.lower_node(tmp_rule)
                    if lower == None:
                        break
                    self.k_rules.remove(lower.item)
            
            # set the minimum support to the support of the rule having
            # the lowest support
            self.min_supp_relative = self.k_rules.minimum().get_absolute_support()

    def subsume(self, rule1, rule2):
        """Check id rule is subsumed by another"""
        # we check first the size of the itemset
        if len(rule1.itemset1) <= len(rule2.itemset1) and len(rule1.itemset2) >= len(rule2.itemset2):
            # after that we check the inclusion relationships between the iemsets
            cond1 = self.contains_or_equals(rule2.itemset1, rule1.itemset1)
            cond2 = self.contains_or_equals(rule1.itemset2, rule2.itemset2)
            # if all the conditions are met, the method returns true
            return cond1 and cond2 
        return False

    def contains_or_equals(self, array1, array2):
        """Check if an array2 of integer is contained in array1"""
        count = 0
        # for each item in the first itemset
        # loop1:
        for item2 in array2:
            # for each item in the second itemset
            for item1 in array1:
                # if the current item in itemset is equal to the one in itemset2
                # search for the next one in itemset1
                if item2 == item1:
                    count += 1
                    break
                    # continue loop1
                # if the current tem in itemset is larger
                # than the current item in itemset2, then 
                # stop because of the lexical order
                elif item1 > item2:
                    return False

        if count != len(array2):
            # means that an item was not found
            return False
        else:
            # if all items were found, return True
            return True

    def register_as_candidate(self, expand_lr, rule_lr):
        """Add a candidate to the set of candidate"""
        # add rule to candidates
        rule_lr.expand_lr = expand_lr
        self.candidates.add(rule_lr)

        # remember the maximum number of candidates reacher for stats
        if self.candidates.size >= self.max_candidate_count:
            self.max_candidate_count = self.candidates.size

    def expand_l(self, rule):
        """This method search for items for expanding left side of a rule I --> J 
        with any item c. This results in rules of the form I U{c} --> J. The method makes sure that:
        - c  is not already included in I or J
        - c appear at least minsup time in tidsIJ before last occurrence of J
	    - c is lexically bigger than all items in I"""
        # the following map will be used to count the support of each item
        # c that could potentially extend the rule.
        # the map associated a set of tids (value) to an item (key).
        frequent_items_c = {}

        # we scan the sequence where I-->J appear to search for items c that we could add.
    	# for each sequence containing I-->J
        left = len(rule.tids_ij)
        for tid in rule.tids_ij:
            # get the sequence and accurances of J in that sequence
            sequence = self.db.database[tid]
            end = rule.occurrences_j_last[tid]

            # for each itemset before the last occurence of J
            # itemloop:
            for k in range(0, end):
                itemset = sequence[k]
                # for each item
                for item_c in itemset:

                    # We will consider if we could create a rule IU{c} --> J
                    # If lexical order is not respected or c is included in the rule already,
                    # then we cannot so return.
                    if self.containsLEX(rule.itemset1, item_c) or self.containsLEX(rule.itemset2, item_c):
                        continue
                    
                    # otherwise, we get the tidset of 'c'
                    # tids_item = frequent_items_c[item]

                    # if this set is not null, which means that "c" was not seen yet
                    # when scanning the sequences from I==>J
                    if item_c not in frequent_items_c.keys():
                        # if there is less tids left in the tidset of I-->J to be scanned than
                        # the minsup, we don't consider c anymore because  IU{c} --> J
                        # could not be frequent
                        if left < self.min_supp_relative:
                            break # continue itemloop TODO
                    else:
                        tids_item_c = frequent_items_c[item_c]
                        # if "c" was seen before but there is not enough sequences left to be scanned
                        # to allow IU{c} --> J to reach the minimum support threshold
                        if len(tids_item_c) + left < self.min_supp_relative:
                            try:
                                frequent_items_c[item_c].remove(item_c)
                            except KeyError:
                                pass
                            break # continue itemloop TODO
                    
                    if item_c not in frequent_items_c.keys():
                        # otherwise, if we did not see "c" yet, create a new tidset for "c"
                        tids_item_c = set()
                        frequent_items_c[item_c] = tids_item_c

                    # add the current tid to the tidset of "c"
                    frequent_items_c[item_c].add(tid)
            left -= 1
        
        # for each item c found, we create a rule IU{c} ==> J
        for item_c, tids_ic_j in frequent_items_c.items():
            if len(tids_ic_j) >= self.min_supp_relative:
                # Calculate tids containing IU{c} which is necessary
                # to calculate the confidence
                tids_ic = set()
                for tid in rule.tids_i:
                    if tid in self.item_count_first[item_c].keys():
                        tids_ic.add(tid)

                # Create rule and calculate its confidence of IU{c} ==> J 
                # defined as:  sup(IU{c} -->J) /  sup(IU{c})
                conf_ic_j = len(tids_ic_j) / len(tids_ic)
                itemset_ic = []
                itemset_ic = rule.itemset1.copy()
                itemset_ic.append(item_c)

                # if the confidence is high enough then it is a valid rule 
                candidate = Rule()
                candidate.rule(itemset_ic, rule.itemset2, conf_ic_j, len(tids_ic_j), tids_ic, None, tids_ic_j, None, rule.occurrences_j_last)
                if conf_ic_j >= self.min_conf:
                    # save the rule
                    self.save(candidate, len(tids_ic_j))

    def containsLEX(self, itemset, item):
        """This method checks if the item "item" is in the itemset."""
        for itm in itemset:
            if itm == item:
                return True
            elif itm > item:
                return True
        return False

    def expand_r(self, rule):
        """This method search for items for expanding right side of a rule I --> J 
	    with any item c. This results in rules of the form I --> J U{c}. 
	    The method makes sure that:
	    - c  is not already included in I or J
	    - c appear at least minsup time in tidsIJ after the first occurrence of I
	    - c is lexically larger than all items in J"""
        frequent_items_c = {}

        # we scan the sequence where I-->J appear to search for items c that we could add.
        # for each sequence containing I-->J.
        left = len(rule.tids_ij)

        for tid in rule.tids_ij:
            # get the seuence and get first occurence of I in that sequence
            sequence = self.db.database[tid]
            first = rule.occurrences_i_first[tid]

            # for each itemset after the first occurence of I in that sequence
            # itemloop:
            for k in range(first+1, len(sequence)):
                itemset = sequence[k]
                # for each item
                for item_c in itemset:

                    # We will consider if we could create a rule I --> J U{c}
                    # If lexical order is not respected or c is included in the rule already,
                    # then we cannot so algorithm return.
                    if self.containsLEX(rule.itemset1, item_c) or self.containsLEX(rule.itemset2, item_c):
                        continue

                    if item_c not in frequent_items_c.keys():
                        if left < self.min_supp_relative:
                            break # continue itemloop TODO
                    else:
                        tids_item_c = frequent_items_c[item_c]
                        # if "c" was seen before but there is not enough sequences left to be scanned
                        # to allow I --> J U{c} to reach the minimum support threshold
                        # remove 'c' and continue the loop of items
                        if len(tids_item_c) + left < self.min_supp_relative:
                            try:
                                frequent_items_c[item_c].remove(item_c)
                            except KeyError:
                                pass
                            break # continue itemloop TODO
                    if item_c not in frequent_items_c:
                        # otherwise, if we did not see "c" yet, create a new tidset for "c"
                        tids_item_c = set()
                        frequent_items_c[item_c] = tids_item_c
 
                    # add the current tid to the tidset of "c"
                    frequent_items_c[item_c].add(tid)
            left -= 1
        
        # for each item c found, we create a rule I ==> JU{c}
        for item_c, tids_i_jc in frequent_items_c.items():
            # if the support of I ==> JU{c} is enough
            if len(tids_i_jc) >= self.min_supp_relative:
                # create the itemset JU{c} and calculate the occurences of JU{c}
                tids_jc = set()
                occurences_jc = {}

                # for each sequence containing J
                for tid in rule.tids_j:
                    # if there is an occurence
                    if tid in self.item_count_first[item_c].keys():
                        tids_jc.add(tid)

                        # calculate lat occurence of JU{c} depending on if 
                        # the last occurence of J is before the last occurence of c or not
                        # get the last occurence of C in that sequence
                        occurence_c_last = self.item_count_last[item_c][tid]
                        occurence_j_last = rule.occurrences_j_last[tid]
                        if occurence_c_last < occurence_j_last:
                            occurences_jc[tid] = occurence_c_last
                        else:
                            occurences_jc[tid] = occurence_j_last

                # Create rule I ==> JU{c} and calculate its confidence 
                # defined as:  sup(I -->J U{c}) /  sup(I)
                conf_i_jc = len(tids_i_jc) / len(rule.tids_i)
                itemset_jc = []
                itemset_jc = rule.itemset2.copy()
                itemset_jc.append(item_c)

                # if the confidence is high enough then it is a valid rule 
                candidate = Rule()
                candidate.rule(rule.itemset1, itemset_jc, conf_i_jc, len(tids_i_jc), rule.tids_i, tids_jc, tids_i_jc, rule.occurrences_i_first, occurences_jc)
                if conf_i_jc >= self.min_conf:
                    # save the rule
                    self.save(candidate, len(tids_i_jc))
                self.register_as_candidate(True, candidate)
                    
    def print_stats(self):
        """Print statistics about the last algorithm execution"""
        log.info("--------TNS - stats----------")
        log.info("Minsup: {}".format(self.min_supp_relative))
        log.info("Rules count: {}".format(self.k_rules.size))
        log.info("Max candidates: {}".format(self.max_candidate_count))
        log.info("Sequential rules count: {}".format(self.k_rules.size))
        log.info("Rules eliminated by strategy1: {}".format(self.not_added))
        log.info("Rules eliminated by strategy2: {}".format(self.total_removed_count))

        if self.k_rules.size > 0:
            self.k_rules.pre_order(self.k_rules.root)


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

    class Database(object):
        def __init__(self, *args):
            self.database = TEST_DB
            self.min_item = 1
            self.max_item = 7
            
    tns = ALgorithmTNS(k=k, min_conf=min_conf, delta=delta, database=Database())

    # tns.run_algorithm()

    class t():
        def __init__(self, itemset1, itemset2):
            self.itemset1 = itemset1
            self.itemset2 = itemset2

    a = t([1], [2,3,4])
    b = t([1], [2,3,4,6])

    print(tns.subsume(a, b))
    print(tns.subsume(b, a))

    # print(tns.contains_or_equals([1,2,3], [2,3, 6]))

    # for i in "12345":
    #     print(i)
    #     for a in "abcd":
    #         if a == "b":
    #             continue
    #         print(a)


