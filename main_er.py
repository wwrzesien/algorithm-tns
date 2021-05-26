import logging
import tweepy

from ERMiner.erminer_alg import AlgorithmERMiner

from twitter import TwitterDatabase

# Create logger
log = logging.getLogger("erminer")
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

TEST_DB = [
    [[1], [1,2,3], [1,3], [4], [3,6]],
    [[1,4], [3], [2,3], [1,5]],
    [[5,6], [1,2], [4,6], [3], [2]],
    [[5], [7], [1,6], [3], [2], [3]]
]

if __name__ == "__main__":
    log.info("Start ERMiner algorithm")

    min_supp = 15
    min_conf = 0.5
    class Database(object):
        def __init__(self, *args):
            self.database = TEST_DB
            self.min_item = 1
            self.max_item = 7

    # twr = Database()

    twr = TwitterDatabase('photography', 1000)
    # twr.retrieve_tweets()
    twr.load_pickle("./data_words.pickle")
    twr.mapping()
    # twr.load_pickle("./data_int.pickle")
    # twr.save_pickle(twr.map_to_words, "./map_to_words.pickle")

    erminer = AlgorithmERMiner(database=twr, min_conf=min_conf, min_supp=min_supp)

    erminer.run_algorithm()
    results = erminer.get_results()

    log.info("")
    log.info("------- ERMiner stats --------")
    log.info("Minsup: {}".format(min_supp))
    log.info("Sequential rules count: {}".format(len(results)))
    log.info("")
    
    # erminer.print_stats()
    twr.print_stats(results)
