import logging
import tweepy
from tns_alg import ALgorithmTNS
from twitter import TwitterDatabase

# Create logger
log = logging.getLogger("tns")
log.setLevel(logging.DEBUG)
log.propagate = False

# Create console handler
ch = logging.StreamHandler()
fh = logging.FileHandler('./logs.log', 'w')
ch.setLevel(logging.DEBUG)
fh.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
log.addHandler(ch)
log.addHandler(fh)

# Seguence db -> list of sequences, 
# Sequence -> list of itemsets
# Itemset -> list of elements (integers/words)
TEST_DB = [
    [[1], [1,2,3], [1,3], [4], [3,6]],
    [[1,4], [3], [2,3], [1,5]],
    [[5,6], [1,2], [4,6], [3], [2]],
    [[5], [7], [1,6], [3], [2], [3]]
]
# TEST_DB = [
#     ([1], [1,2,3], [1,3], [4], [3,6]),
#     ([1], [1,2,3], [1,3], [4], [3,6])
# ]

if __name__ == "__main__":
    log.info("Start TNS algorithm")

    k = 30
    min_conf = 0.5
    delta = 2

    # log.debug(TEST_DB)

    class Database(object):
        def __init__(self, *args):
            self.database = TEST_DB
            self.min_item = 1
            self.max_item = 7
    
    twr = Database()

    # twr = TwitterDatabase('covid', 100)
    # twr.retrieve_tweets()
    # twr.load_pickle("./data_words.pickle", twr.database_words)
    # twr.mapping()
    # twr.load_pickle("./data_int.pickle")
    # print(twr.database)
    # print(1 in twr.database)
            
    tns = ALgorithmTNS(k=k, min_conf=min_conf, delta=delta, database=twr)

    tns.run_algorithm()

    tns.print_stats()

    