"""Menu-driven explorer for the Twitter Entity Sentiment dataset."""
import os

from models import CSV_FILE, TEXT_WIDTH, VALID_SENTIMENTS, TweetCollection
from data_loader import load_tweets
from text_utils import shorten, clean_text
import analysis

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROWS = 10


# ---------------- input helpers (every typed value is checked) ----------------
def ask_int(prompt, low, high):
    """Keep asking until the user types a whole number between low and high."""
    while True:
        typed = input(prompt).strip()
        if typed == "":
            print("  Please type something.")
        elif not (typed.isdigit() or (typed[0] == "-" and typed[1:].isdigit())):
            print(f"  '{typed}' is not a whole number.")
        elif int(typed) < low or int(typed) > high:
            print(f"  Please type a number from {low} to {high}.")
        else:
            return int(typed)


def ask_text(prompt):
    """Keep asking until the user types something that is not blank."""
    while True:
        typed = input(prompt).strip()
        if typed != "":
            return typed
        print("  Please type something.")


def ask_entity(prompt, entities):
    """Ask for an entity name; '?' shows the list of valid names."""
    while True:
        typed = ask_text(prompt)
        if typed == "?":
            print("  Entities: " + ", ".join(entities))
            continue
        found = analysis.find_entity(entities, typed)
        if found is not None:
            return found
        print(f"  '{typed}' is not a known (or is an ambiguous) entity. Type ? to see the list.")


def ask_sentiment():
    """Ask for a sentiment; empty line means 'any'. Returns name or None."""
    while True:
        typed = input("Sentiment (Positive/Negative/Neutral/Irrelevant, Enter = any): ").strip()
        if typed == "":
            return None
        for valid in VALID_SENTIMENTS:
            if clean_text(typed) == valid.lower():
                return valid
        print(f"  '{typed}' is not a valid sentiment.")


# ---------------- output helpers (aligned columns) ----------------
def print_tweets(tweets, limit=DEFAULT_ROWS):
    """Print tweets in a table, at most `limit` rows."""
    if len(tweets) == 0:
        print("  No tweets found.")
        return
    print(f"\n{'ID':<7}{'Entity':<24}{'Sentiment':<11}{'Len':>4}  {'Text'}")
    print("-" * (7 + 24 + 11 + 4 + 2 + TEXT_WIDTH))
    for tweet in tweets[:limit]:
        entity = shorten(tweet.entity, 22)
        text = shorten(tweet.text, TEXT_WIDTH)
        print(f"{tweet.tweet_id:<7}{entity:<24}{tweet.sentiment:<11}{tweet.length:>4}  {text}")
    if len(tweets) > limit:
        print(f"... showing {limit} of {len(tweets)} tweets")
    else:
        print(f"{len(tweets)} tweet(s) shown")


def print_summary_header():
    print(f"\n{'Entity':<34}{'Total':>6}{'Pos':>5}{'Neg':>5}{'Neu':>5}{'Irr':>5}"
          f"{'Pos%':>8}{'Neg%':>8}{'AvgLen':>8}")
    print("-" * 84)


def print_summary_row(s):
    print(f"{shorten(s['entity'], 32):<34}{s['total']:>6}{s['positive']:>5}{s['negative']:>5}"
          f"{s['neutral']:>5}{s['irrelevant']:>5}{s['positive_pct']:>8.1f}"
          f"{s['negative_pct']:>8.1f}{s['avg_length']:>8.1f}")


# ---------------- menu actions ----------------
def do_search(collection):
    keyword = ask_text("Keyword to search for: ")
    results = analysis.search_tweets(collection.tweets, keyword)
    print(f"\nFound {len(results)} tweet(s) containing '{keyword.strip()}'.")
    print_tweets(results)


def do_list(collection):
    entity = ask_entity("Entity (? for list): ", collection.entities())
    sentiment = ask_sentiment()
    results = analysis.filter_tweets(collection.tweets, entity=entity, sentiment=sentiment)
    label = sentiment if sentiment else "any sentiment"
    print(f"\n{entity} / {label}: {len(results)} tweet(s)")
    print_tweets(results)


def do_top(collection):
    n = ask_int(f"How many tweets (1-{len(collection)})? ", 1, len(collection))
    results = analysis.top_longest(collection.tweets, n)
    print(f"\nTop {n} longest tweets:")
    print_tweets(results, limit=n)
    # simple category count for the shown tweets (if / elif / else inside analysis)
    counts = {"short": 0, "medium": 0, "long": 0}
    for tweet in results:
        counts[analysis.categorize_length(tweet.length)] += 1
    print(f"Length categories among these: {counts}")


def do_summary(collection):
    summaries = analysis.summarize_all(collection.tweets, collection.entities())
    print("\nSentiment summary per entity (ranked by % positive):")
    print_summary_header()
    for summary in summaries:
        print_summary_row(summary)


def do_compare(collection):
    entities = collection.entities()
    first = ask_entity("First entity (? for list): ", entities)
    second = ask_entity("Second entity (? for list): ", entities)
    if first == second:
        print("  Please choose two different entities.")
        return
    print_summary_header()
    for name in (first, second):
        print_summary_row(analysis.summarize_entity(collection.tweets, name))
    a = analysis.summarize_entity(collection.tweets, first)
    b = analysis.summarize_entity(collection.tweets, second)
    if a["positive_pct"] > b["positive_pct"]:
        print(f"\n{first} is more positive than {second}.")
    elif a["positive_pct"] < b["positive_pct"]:
        print(f"\n{second} is more positive than {first}.")
    else:
        print("\nBoth entities have the same share of positive tweets.")


MENU = """
===== Twitter Sentiment Explorer =====
1. Search tweets by keyword
2. List tweets by entity / sentiment
3. Top N longest tweets
4. Sentiment summary per entity
5. Compare two entities
6. Exit"""


def main():
    path = os.path.join(HERE, CSV_FILE)
    try:
        tweets, skipped = load_tweets(path)
    except FileNotFoundError as error:
        print(error)
        return
    collection = TweetCollection(tweets)
    print(f"Loaded {len(collection)} records, skipped {skipped} unreadable row(s).")
    if len(collection) == 0:
        print("Nothing to explore. Exiting.")
        return

    running = True
    while running:
        print(MENU)
        try:
            choice = ask_int("Choose 1-6: ", 1, 6)
            if choice == 1:
                do_search(collection)
            elif choice == 2:
                do_list(collection)
            elif choice == 3:
                do_top(collection)
            elif choice == 4:
                do_summary(collection)
            elif choice == 5:
                do_compare(collection)
            else:
                running = False
        except EOFError:
            print("\nInput closed. Goodbye!")
            running = False
    print("Goodbye!")


if __name__ == "__main__":
    main()
