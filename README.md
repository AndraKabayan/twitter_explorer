# Twitter Sentiment Explorer

## 1. Dataset
- **Name:** Twitter Entity Sentiment Analysis (file used: `twitter_validation.csv`)
- **Kaggle link:** TODO – paste the dataset page link here
- **License:** TODO – copy the license shown on the Kaggle page
- **Why I chose it:** TODO – write 2-3 sentences in your own words (e.g. real tweets, clean categories, good for search, filter and ranking).
- **Size:** 1,000 rows, one CSV file, one tweet per row, no header row.

### Columns
| Column | Used? | Notes |
|---|---|---|
| 1 – Tweet ID | Yes | Whole number, used to identify a tweet. |
| 2 – Entity | Yes | Game or company the tweet is about (32 values). |
| 3 – Sentiment | Yes | Positive / Negative / Neutral / Irrelevant. |
| 4 – Tweet text | Yes | Line breaks removed. `@usernames` replaced by `@user` for privacy. |

All four columns are filled in every row, so no blank cells need special handling.
(A row with a missing value would be skipped and counted.)

## 2. How to run
Only Python 3 is needed (standard library only).

    python main.py                 # start the program
    python -m unittest             # run the unit tests (23 tests)

Run both commands from inside this folder. `twitter_validation.csv` must stay next to `main.py`.

## 3. Features
1. **Search by keyword** – ignores capitals, hyphens, accents and extra spaces.
2. **List by entity / sentiment** – filter tweets; shows the first 10.
3. **Top N longest tweets** – ranked with my own insertion sort (no `sorted()`), first N taken by slicing, plus a short/medium/long category count.
4. **Sentiment summary per entity** – counts, % positive, % negative and average length, ranked by % positive.
5. **Compare two entities** – side-by-side rows and a sentence saying which is more positive.

At start-up the program prints how many records were loaded and how many rows were skipped.
Every typed value is validated; bad input gives a message and a new prompt.

## 4. Known limitations
- Sentiment labels come from the dataset and may not always match human judgement.
- Tweet text is cut to 55 characters in tables.
- The only numeric fields are the ID and values I derive (length, percentages), so the analysis is fairly simple.
- Entity names are used as written in the dataset (e.g. `WorldOfCraft`).

## 5. Video link
TODO – paste your YouTube link (Unlisted or Public, not Private).

## 6. Where each concept is used
| Concept | File | Function / place |
|---|---|---|
| Variables and data types (str, int, float, bool, list; capital constants) | `models.py` | Constants `CSV_FILE`, `VALID_SENTIMENTS`, `SHORT_LIMIT`; `Tweet.__init__` |
| Input and output (input(), validation loop, f-strings, aligned columns) | `main.py` | `ask_int`, `print_tweets`, `print_summary_row` |
| Operators (arithmetic, relational, and/or/not) | `analysis.py` | `percent`, `average_length`, `filter_tweets` |
| Conditional statements (if/elif/else) | `analysis.py` | `categorize_length`; also `ask_int` in `main.py` |
| Loops (for and while) | `main.py` / `analysis.py` | `while running` in `main()`; `for` in `search_tweets` |
| Functions | `analysis.py` | `safe_divide`, `summarize_entity`, `top_longest` |
| Lists (store, build new lists, slicing) | `analysis.py` | `filter_tweets` builds a list; `top_longest` uses `ranked[:n]` |
| String manipulation | `text_utils.py` | `clean_text`, `mask_handles`, `shorten` |
| Classes (bonus) | `models.py` | `Tweet` (`__init__`, `__str__`), `TweetCollection` |
| Unit tests | `test_project.py` | 23 tests: normal, edge and bad input |
