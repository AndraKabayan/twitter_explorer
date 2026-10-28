"""Constants and record classes for the Twitter Entity Sentiment explorer."""

# ---- Constants (fixed values, written in capital letters) ----
CSV_FILE = "twitter_validation.csv"
EXPECTED_COLUMNS = 4          # id, entity, sentiment, text
VALID_SENTIMENTS = ["Positive", "Negative", "Neutral", "Irrelevant"]
SHORT_LIMIT = 60              # tweets up to this many characters are "short"
MEDIUM_LIMIT = 140            # up to this many are "medium", above are "long"
TEXT_WIDTH = 55               # characters of tweet text shown in tables


class Tweet:
    """One row of the dataset: a single tweet about an entity."""

    def __init__(self, tweet_id, entity, sentiment, text):
        self.tweet_id = tweet_id      # int
        self.entity = entity          # str
        self.sentiment = sentiment    # str, one of VALID_SENTIMENTS
        self.text = text              # str

    @property
    def length(self):
        """Number of characters in the tweet."""
        return len(self.text)

    @property
    def word_count(self):
        """Number of words in the tweet."""
        return len(self.text.split())

    def __str__(self):
        return f"[{self.tweet_id}] {self.entity} ({self.sentiment}): {self.text[:TEXT_WIDTH]}"


class TweetCollection:
    """Holds a list of Tweet objects and offers simple helpers."""

    def __init__(self, tweets=None):
        self.tweets = list(tweets) if tweets else []

    def add(self, tweet):
        self.tweets.append(tweet)

    def __len__(self):
        return len(self.tweets)

    def entities(self):
        """Return the sorted list of distinct entity names (own loop, no sorted())."""
        names = []
        for tweet in self.tweets:
            if tweet.entity not in names:
                names.append(tweet.entity)
        # simple insertion sort, case-insensitive
        for i in range(1, len(names)):
            current = names[i]
            j = i - 1
            while j >= 0 and names[j].lower() > current.lower():
                names[j + 1] = names[j]
                j -= 1
            names[j + 1] = current
        return names

    def __str__(self):
        return f"TweetCollection with {len(self.tweets)} tweets"
