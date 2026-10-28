"""Functions behind each menu feature."""
from models import SHORT_LIMIT, MEDIUM_LIMIT, VALID_SENTIMENTS
from text_utils import clean_text


def safe_divide(top, bottom):
    """Division that returns 0.0 instead of crashing when bottom is 0."""
    if bottom == 0:
        return 0.0
    return top / bottom


def percent(part, total):
    return safe_divide(part, total) * 100


def average_length(tweets):
    """Average number of characters per tweet (0.0 for an empty list)."""
    total = 0
    for tweet in tweets:
        total += tweet.length
    return safe_divide(total, len(tweets))


def categorize_length(length):
    """Place a tweet in a length category."""
    if length <= SHORT_LIMIT:
        return "short"
    elif length <= MEDIUM_LIMIT:
        return "medium"
    else:
        return "long"


def search_tweets(tweets, keyword):
    """Tweets whose text contains the keyword (ignores capitals/extra spaces)."""
    needle = clean_text(keyword)
    results = []
    if needle == "":
        return results
    for tweet in tweets:
        if needle in clean_text(tweet.text):
            results.append(tweet)
    return results


def filter_tweets(tweets, entity=None, sentiment=None):
    """Filter by entity and/or sentiment. None means 'do not filter on this'."""
    results = []
    for tweet in tweets:
        entity_ok = entity is None or clean_text(tweet.entity) == clean_text(entity)
        sentiment_ok = sentiment is None or tweet.sentiment == sentiment
        if entity_ok and sentiment_ok:
            results.append(tweet)
    return results


def sort_descending(items, key_func):
    """Insertion sort written by hand (largest key first, stable).
    Works on a copy, so the original list is not changed."""
    result = list(items)
    for i in range(1, len(result)):
        current = result[i]
        j = i - 1
        while j >= 0 and key_func(result[j]) < key_func(current):
            result[j + 1] = result[j]
            j -= 1
        result[j + 1] = current
    return result


def top_longest(tweets, n):
    """The n longest tweets (slicing takes the first n of the ranked list)."""
    if n <= 0:
        return []
    ranked = sort_descending(tweets, lambda t: t.length)
    return ranked[:n]


def summarize_entity(tweets, entity):
    """Counts, percentages and average length for one entity."""
    subset = filter_tweets(tweets, entity=entity)
    counts = {}
    for sentiment in VALID_SENTIMENTS:
        counts[sentiment] = 0
    for tweet in subset:
        counts[tweet.sentiment] += 1
    total = len(subset)
    return {
        "entity": entity,
        "total": total,
        "positive": counts["Positive"],
        "negative": counts["Negative"],
        "neutral": counts["Neutral"],
        "irrelevant": counts["Irrelevant"],
        "positive_pct": percent(counts["Positive"], total),
        "negative_pct": percent(counts["Negative"], total),
        "avg_length": average_length(subset),
    }


def summarize_all(tweets, entities):
    """One summary per entity, ranked by % positive (highest first)."""
    summaries = []
    for entity in entities:
        summaries.append(summarize_entity(tweets, entity))
    return sort_descending(summaries, lambda s: s["positive_pct"])


def find_entity(entities, typed):
    """Match what the user typed to an entity name.
    Exact match (after cleaning) wins; otherwise a unique partial match.
    Returns the entity name or None."""
    wanted = clean_text(typed)
    if wanted == "":
        return None
    for name in entities:
        if clean_text(name) == wanted:
            return name
    partial = []
    for name in entities:
        if wanted in clean_text(name):
            partial.append(name)
    if len(partial) == 1:
        return partial[0]
    return None
