"""String helpers: cleaning for comparison, privacy masking, table formatting."""
import re
import unicodedata


def remove_accents(text):
    """'café' -> 'cafe'."""
    decomposed = unicodedata.normalize("NFKD", text)
    result = ""
    for ch in decomposed:
        if not unicodedata.combining(ch):
            result += ch
    return result


def clean_text(text):
    """Normalise text for comparison: lower case, no accents, no hyphens,
    and no extra spaces."""
    if text is None:
        return ""
    text = remove_accents(str(text)).lower()
    text = text.replace("-", " ").replace("_", " ")
    words = text.strip().split()          # split() also removes repeated spaces
    return " ".join(words)


def mask_handles(text):
    """Replace @usernames with @user so no account names are stored."""
    return re.sub(r"@\w+", "@user", text)


def one_line(text):
    """Turn line breaks and repeated spaces into single spaces."""
    return " ".join(text.replace("\r", " ").replace("\n", " ").split())


def shorten(text, width):
    """Cut text to `width` characters and add '...' when it was cut."""
    text = one_line(text)
    if width < 4:
        return text[:max(width, 0)]
    if len(text) > width:
        return text[:width - 3] + "..."
    return text
