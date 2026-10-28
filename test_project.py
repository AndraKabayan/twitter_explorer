"""Unit tests (run with: python -m unittest)."""
import os
import tempfile
import unittest

from models import Tweet, TweetCollection
from text_utils import clean_text, mask_handles, shorten
from data_loader import parse_row, load_tweets
import analysis


def make_tweets():
    return [
        Tweet(1, "Google", "Positive", "I love Google maps"),
        Tweet(2, "Google", "Negative", "Google search is slow today and I am not happy about it"),
        Tweet(3, "FIFA", "Neutral", "FIFA update released"),
        Tweet(4, "FIFA", "Positive", "Great FIFA match"),
        Tweet(5, "FIFA", "Positive", "FIFA is fun"),
    ]


class TestTextUtils(unittest.TestCase):
    def test_clean_text_normal(self):
        self.assertEqual(clean_text("  Hello   WORLD "), "hello world")

    def test_clean_text_accents_hyphens(self):
        self.assertEqual(clean_text("Café-Au-Lait"), "cafe au lait")

    def test_clean_text_empty_and_none(self):
        self.assertEqual(clean_text(""), "")
        self.assertEqual(clean_text(None), "")

    def test_mask_handles(self):
        self.assertEqual(mask_handles("Hi @Bob_99, thanks"), "Hi @user, thanks")

    def test_shorten(self):
        self.assertEqual(shorten("abcdefghij", 8), "abcde...")
        self.assertEqual(shorten("abc", 8), "abc")


class TestLoader(unittest.TestCase):
    def test_parse_good_row(self):
        tweet = parse_row(["12", "Google", "positive", "Nice\nday @x"])
        self.assertEqual(tweet.tweet_id, 12)
        self.assertEqual(tweet.sentiment, "Positive")
        self.assertEqual(tweet.text, "Nice day @user")

    def test_parse_bad_rows(self):
        self.assertIsNone(parse_row(["x", "Google", "Positive", "hi"]))      # bad id
        self.assertIsNone(parse_row(["1", "Google", "Happy", "hi"]))         # bad sentiment
        self.assertIsNone(parse_row(["1", "Google", "Positive"]))            # missing column
        self.assertIsNone(parse_row(["1", "", "Positive", "hi"]))            # empty entity
        self.assertIsNone(parse_row(["1", "Google", "Positive", "   "]))     # empty text

    def test_load_counts_skipped(self):
        content = '1,Google,Positive,"good"\n2,Google,Bad,"oops"\nabc,FIFA,Neutral,"x"\n3,FIFA,Neutral,"ok"\n'
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "t.csv")
            with open(path, "w", encoding="utf-8") as file:
                file.write(content)
            tweets, skipped = load_tweets(path)
        self.assertEqual(len(tweets), 2)
        self.assertEqual(skipped, 2)

    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            load_tweets("does_not_exist.csv")


class TestAnalysis(unittest.TestCase):
    def test_search_ignores_case_and_spaces(self):
        results = analysis.search_tweets(make_tweets(), "  GOOGLE   MAPS ")
        self.assertEqual(len(results), 1)

    def test_search_empty_keyword(self):
        self.assertEqual(analysis.search_tweets(make_tweets(), "   "), [])

    def test_search_empty_list(self):
        self.assertEqual(analysis.search_tweets([], "x"), [])

    def test_filter_entity_and_sentiment(self):
        results = analysis.filter_tweets(make_tweets(), entity="fifa", sentiment="Positive")
        self.assertEqual(len(results), 2)

    def test_top_longest_and_slicing(self):
        top = analysis.top_longest(make_tweets(), 2)
        self.assertEqual(len(top), 2)
        self.assertEqual(top[0].tweet_id, 2)

    def test_top_edge_cases(self):
        self.assertEqual(analysis.top_longest(make_tweets(), 0), [])
        self.assertEqual(analysis.top_longest([], 3), [])
        self.assertEqual(len(analysis.top_longest(make_tweets(), 99)), 5)

    def test_sort_does_not_change_original(self):
        tweets = make_tweets()
        analysis.sort_descending(tweets, lambda t: t.length)
        self.assertEqual(tweets[0].tweet_id, 1)

    def test_summary_values(self):
        s = analysis.summarize_entity(make_tweets(), "FIFA")
        self.assertEqual(s["total"], 3)
        self.assertAlmostEqual(s["positive_pct"], 66.666, places=2)

    def test_summary_unknown_entity_no_zero_division(self):
        s = analysis.summarize_entity(make_tweets(), "Nobody")
        self.assertEqual(s["total"], 0)
        self.assertEqual(s["positive_pct"], 0.0)
        self.assertEqual(s["avg_length"], 0.0)

    def test_safe_divide_zero(self):
        self.assertEqual(analysis.safe_divide(5, 0), 0.0)
        self.assertEqual(analysis.average_length([]), 0.0)

    def test_categorize_length(self):
        self.assertEqual(analysis.categorize_length(10), "short")
        self.assertEqual(analysis.categorize_length(100), "medium")
        self.assertEqual(analysis.categorize_length(300), "long")

    def test_find_entity(self):
        names = ["Google", "FIFA", "GrandTheftAuto(GTA)"]
        self.assertEqual(analysis.find_entity(names, " fifa "), "FIFA")
        self.assertEqual(analysis.find_entity(names, "grand"), "GrandTheftAuto(GTA)")
        self.assertIsNone(analysis.find_entity(names, "zzz"))
        self.assertIsNone(analysis.find_entity(names, ""))


class TestModels(unittest.TestCase):
    def test_tweet_str_and_properties(self):
        t = Tweet(1, "Google", "Positive", "hello big world")
        self.assertEqual(t.word_count, 3)
        self.assertIn("Google", str(t))

    def test_collection_entities_sorted(self):
        c = TweetCollection(make_tweets())
        self.assertEqual(c.entities(), ["FIFA", "Google"])
        self.assertEqual(len(c), 5)
        self.assertEqual(len(TweetCollection()), 0)


if __name__ == "__main__":
    unittest.main()
