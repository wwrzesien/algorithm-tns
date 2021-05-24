import logging
import tweepy
from erminer_alg import AlgorithmERMiner
# from twitter import TwitterDatabase

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

    class Database(object):
        def __init__(self, *args):
            self.database = TEST_DB
            self.min_item = 1
            self.max_item = 7

    db = Database()

    erminer = AlgorithmERMiner(database=db)

