"""Reads the CSV file and turns each valid row into a Tweet object."""
import csv
import os

from models import Tweet, EXPECTED_COLUMNS, VALID_SENTIMENTS
from text_utils import mask_handles, one_line, clean_text


def parse_row(row):
    """Convert one CSV row (list of str) into a Tweet.
    Returns None when the row cannot be used."""
    if len(row) != EXPECTED_COLUMNS:
        return None
    id_text, entity, sentiment, text = row
    id_text = id_text.strip()
    if not id_text.isdigit():
        return None
    entity = entity.strip()
    text = one_line(text)
    if entity == "" or text == "":
        return None
    # match sentiment ignoring capitals/spaces, store the official spelling
    matched = None
    for valid in VALID_SENTIMENTS:
        if clean_text(sentiment) == valid.lower():
            matched = valid
    if matched is None:
        return None
    return Tweet(int(id_text), entity, matched, mask_handles(text))


def load_tweets(path):
    """Read the CSV (it has NO header row).
    Returns (list_of_tweets, skipped_count)."""
    tweets = []
    skipped = 0
    if not os.path.exists(path):
        raise FileNotFoundError(f"Data file not found: {path}")
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as file:
        reader = csv.reader(file)
        for row in reader:
            if not row:               # completely empty line: ignore
                continue
            tweet = parse_row(row)
            if tweet is None:
                skipped += 1
            else:
                tweets.append(tweet)
    return tweets, skipped
