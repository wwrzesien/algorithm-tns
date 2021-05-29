import logging
import tweepy
import time
import pickle

from ERMiner.erminer_alg import AlgorithmERMiner

from twitter import TwitterDatabase

# Create logger
log = logging.getLogger("erminer")
log.setLevel(logging.DEBUG)
log.propagate = False

# Create console handler
ch = logging.StreamHandler()
fh = logging.FileHandler('./logs_erminer.log', 'w')
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

class Database(object):
    def __init__(self, *args):
        self.database = TEST_DB
        self.min_item = 1
        self.max_item = 7

def test_algorithm(min_conf):
    # min_supp = [1, ]
    files = {"1000": "data_words_1000.pickle", "1500": "data_words_1500.pickle", "3000": "data_words_3000.pickle", "comb": "data_words_combined.pickle"}
    min_supp = [1, 5, 10, 15, 20]

    r = {"comb": [], "1000": [], "1500": [], "3000": [], "supp": min_supp}

    twr = TwitterDatabase('photography', 300)
    for key, file in files.items():
        for supp in min_supp:
            twr.load_pickle("./" + file)
            twr.mapping("data_int.pickle")

            erminer = AlgorithmERMiner(database=twr, min_conf=min_conf, min_supp=supp)

            start_time = time.time()
            erminer.run_algorithm()
            exec_time = round(time.time() - start_time, 4)
            log.info("Execution time: {}s".format(exec_time))
            
            results = erminer.get_results()

            log.info("")
            log.info("------- ERMiner stats --------")
            log.info("Minsup: {}".format(supp))
            log.info("Sequential rules count: {}".format(len(results)))
            log.info("")
            
            twr.print_stats(results)
            r[key].append(exec_time)


    with open("results.pickle", 'wb') as file:
        pickle.dump(r, file, protocol=pickle.HIGHEST_PROTOCOL)


def combine_datasets():
    files = ["data_words_500.pickle", "data_words_1000.pickle", "data_words_1500.pickle", "data_words_3000.pickle"]
    twr = TwitterDatabase('photography', 300)
    combine_db = []
    for file in files:
        twr.load_pickle("./" + file)
        combine_db += twr.database_words
    twr.database_words = combine_db
    save = {'data': twr.database_words, 'min_item': twr.min_item, 'max_item': twr.max_item, 'mapping':twr.map_to_words, "stats": twr.stats}
    twr.save_pickle(save, "data_words_combined.pickle")

if __name__ == "__main__":
    log.info("Start ERMiner algorithm")

    min_supp = 15
    min_conf = 0.5

    # combine_datasets()
    test_algorithm(min_conf)

    # test database
    # twr = Database()

    # analitical database
    # twr = TwitterDatabase('photography', 3000)
    # twr.retrieve_tweets("data_words_3000.pickle")
    # twr.load_pickle("./data_words_1000.pickle")
    # twr.mapping()
    # # twr.load_pickle("./data_int.pickle")
    # # twr.save_pickle(twr.map_to_words, "./map_to_words.pickle")

    # erminer = AlgorithmERMiner(database=twr, min_conf=min_conf, min_supp=min_supp)

    # start_time = time.time()
    # erminer.run_algorithm()
    # log.info("Execution time: {}s".format(round(time.time() - start_time, 4)))

    # results = erminer.get_results()

    # log.info("")
    # log.info("------- ERMiner stats --------")
    # log.info("Minsup: {}".format(min_supp))
    # log.info("Sequential rules count: {}".format(len(results)))
    # log.info("")
    
    # # erminer.print_stats()
    # twr.print_stats(results)

