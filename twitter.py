import pickle
import logging
import tweepy

log = logging.getLogger("twitter")
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.NOTSET)

formatter = logging.Formatter('%(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

# Twitter API credentials
CONSUMER_KEY = "SOmoMXIHBGv1af7MSJ2ws2cag"
CONSUMER_SECRET = "3oTmNzSOuBJUzLiL2yk8SCGF5il7cnEE57Jchk5uMJONb2gtR6"
ACCESS_TOKEN = "1388823775551107083-hqQn9objB2tRrkqZIVHgcnjmLGJGBy"
ACCESS_TOKEN_SECRET = "bwZUFsqcocAuZGKg4RrTnB9mXZW0tS7e9vZ6A5eqHxkGD"

class TwitterDatabase(object):
    def __init__(self, hashtag, tweets_num):
        self.hashtag = hashtag
        self.tweets_num = tweets_num
        self.map_to_words = {}
        self.database_int = []
        self.database_words = []
    
    def retrieve_tweets(self):
        """Call Twitter API, create words database"""
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth, wait_on_rate_limit=True)

        tweets = tweepy.Cursor(
            api.search, 
            q=self.hashtag,
            lang="en",
            tweet_mode='extended'
        ).items(self.tweets_num)
        self.database_words = [tweet.full_text.lower().split() for tweet in tweets]

        log.debug(self.database_words[0])
        self.save_pickle(self.database_words, "data_words.pickle")

    def mapping(self):
        """Create map int-word and int database"""
        word_id = 1
        temp = {}
        for seq in self.database_words:
            seq_new = []
            for word in seq:
                if "@" in word:
                    continue
                if word not in self.map_to_words.values():
                    self.map_to_words[word_id] = word
                    temp[word] = word_id
                seq_new.append([temp[word]])
                word_id += 1
            self.database_int.append(seq_new)

        log.debug(self.database_int[0])
        self.save_pickle(self.database_int, "data_int.pickle")
    
    def print_stats(self, results):
        """Display final stats"""
        for result in results:
            i_words = [self.map_to_words[num] for num in result.i]
            j_words = [self.map_to_words[num] for num in result.j]

            string = "{} -> {}, sup: {}, conf: {}".format(
                i_words, j_words, result.sup, result.conf
            )
            log.info(string)

    def save_pickle(self, data, filename):
        """Save data to picke"""
        with open(filename, 'wb') as file:
            pickle.dump(data, file, protocol=pickle.HIGHEST_PROTOCOL)
        log.info("Queries saved to {}".format(filename))

    def load_pickle(self, filename):
        """Load data from pickle"""
        with open(filename, "rb") as file:
            data = pickle.load(file)
        return data

if __name__ == "__main__":
    twr = TwitterDatabase("covid", 100)
    # twr.retrieve_tweets()
    # tweets = twr.load_pickle("./data_words.pickle")
    # # print(tweets[0])
    # twr.database_words = tweets
    # twr.mapping()
    # print(twr.database_int)



    

    
