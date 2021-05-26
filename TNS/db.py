from rule import Rule
import copy

class Database(object):
    def __init__(self, *args):
        self.db = []
        self.min_rule = None
        self.max_rule = None
        self.size = 0
    
    def is_empty(self):
        return len(self.db) == 0
    
    def add(self, rule):
        if self.min_rule is None:
            self.min_rule = rule
        elif rule.compare(self.min_rule) < 0:
            self.min_rule = rule
        
        if self.max_rule is None:
            self.max_rule = rule
        elif rule.compare(self.max_rule) > 0:
            self.max_rule = rule

        self.db.append(rule)
        self.size += 1
    
    def remove(self, rule):
        if rule not in self.db:
            return
        else:
            self.db.remove(rule)
        self.size -= 1
    
    def minimum(self):
        return self.min_rule
    
    def maximum(self):
        return self.max_rule
    
    def pop_minimum(self):
        v = self.min_rule
        self.db.remove(self.min_rule)
        self.size -= 1
        if len(self.db) == 0:
            self.min_rule = None
        else:
            self.min_rule = self.db[0]
            for rule in self.db:
                if rule.compare(self.min_rule) < 0:
                    self.min_rule = rule
        return v

    def pop_maximum(self):
        v = self.max_rule
        self.db.remove(self.max_rule)
        self.size -= 1
        if len(self.db) == 0:
            self.max_rule = None
        else:
            self.max_rule = self.db[0]
            for rule in self.db:
                if rule.compare(self.max_rule) > 0:
                    self.max_rule = rule
        return v

    def lower_node(self, rule):
        lower_rules = []
        for rule_db in self.db:
            if rule.compare(rule_db) >= 0:
                if rule_db is not rule:
                    lower_rules.append(rule_db)
        return lower_rules

    def pre_order(self):
        for rule in self.db:
            rule.print_stats()



        


        