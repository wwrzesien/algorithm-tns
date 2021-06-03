import pickle
import logging
import tweepy
import numpy as np

# log = logging.getLogger("tns")
log = logging.getLogger("erminer")
log.setLevel(logging.DEBUG)
log.propagate = False

# Twitter API credentials

class TwitterDatabase(object):
    def __init__(self, hashtag, tweets_num):
        self.hashtag = hashtag
        self.tweets_num = tweets_num
        self.map_to_words = {}
        self.database = []
        self.database_words = []
        self.min_item = 1
        self.max_item = 1

        self.stats = {"seq_count": 0, "dist_item_count": 0, "avg_seq_len": []}
    
    def retrieve_tweets(self, filename):
        """Call Twitter API, create words database"""
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth, wait_on_rate_limit=True)

        tweets = tweepy.Cursor(
            api.search, 
            q=self.hashtag,
            lang="en",
            # tweet_mode='extended'
        ).items(self.tweets_num)
        for tweet in tweets:
            data = []
            if len(tweet.entities['hashtags']) != 0:
                for h in tweet.entities['hashtags']:
                    data.append(h['text'].lower())
                self.database_words.append(data)

        log.debug(self.database_words[0])
        save = {'data': self.database_words, 'min_item': self.min_item, 'max_item': self.max_item, 'mapping':self.map_to_words, "stats": self.stats}
        self.save_pickle(save, filename)

    def mapping(self, filename):
        """Create map int-word and int database"""
        temp = {}
        for seq in self.database_words:
            self.stats["seq_count"] += 1
            self.stats["avg_seq_len"].append(len(seq))
            seq_new = []
            for word in seq:
                if "@" in word or (word is seq[-1] and '...' in word):
                    continue

                if word not in self.map_to_words.values():
                    self.map_to_words[self.max_item] = word
                    temp[word] = self.max_item
                    self.max_item += 1
                seq_new.append([temp[word]])
            self.database.append(seq_new)

        self.stats['avg_seq_len'] = np.mean(self.stats['avg_seq_len'])
        self.stats['dist_item_count'] = len(self.map_to_words)
        log.debug(self.database[0])
        save = {'data': self.database, 'min_item': self.min_item, 'max_item': self.max_item, 'mapping':  self.map_to_words, "stats": self.stats}
        self.save_pickle(save, filename)
    
    def print_stats(self, results):
        """Display final stats"""

        log.info("Sequence count: {}".format(self.stats["seq_count"]))
        log.info("Distinct item count: {}".format(self.stats['dist_item_count']))
        log.info("Avg sequence length: {}".format(self.stats['avg_seq_len']))
        log.info("")
        for result in results:
            i_words = [self.map_to_words[num] for num in result["i"]]
            j_words = [self.map_to_words[num] for num in result["j"]]

            string = "{} -> {}, sup: {}, conf: {}".format(
                i_words, j_words, result["sup"], result["conf"]
            )
            # log.info(string)

    def save_pickle(self, data, filename):
        """Save data to picke"""
        with open(filename, 'wb') as file:
            pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)
        log.info("Queries saved to {}".format(filename))

    def load_pickle(self, filename):
        """Load data from pickle"""
        log.info("Load: {}".format(filename))
        with open(filename, "rb") as file:
            data = pickle.load(file)
        self.min_item = data['min_item']
        self.max_item = data['max_item']
        self.map_to_words = data['mapping']
        self.stats = data["stats"]
        if 'int' in filename:
            self.database = data['data']
        else:
            self.database_words = data['data']

if __name__ == "__main__":
    twr = TwitterDatabase("covid", 10)
    twr.retrieve_tweets()
    # twr.load_pickle("./data_words.pickle", twr.database_words)
    print(twr.database_words)
    twr.mapping()



    

    
