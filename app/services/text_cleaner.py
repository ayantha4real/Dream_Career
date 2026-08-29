"""
HTML-to-text cleaning for scraped job descriptions.

Sources like XpressJobs store Quill-editor HTML inside their API
payloads. Storing that raw markup pollutes both the UI and the
skill-matching tokenization, so every description is normalized
to plain readable text before it reaches the database.
"""

import html as html_lib
import re


_BLOCK_TAGS = re.compile(
    r"</?(?:p|div|br|h[1-6]|li|ul|ol|tr|table|blockquote)[^>]*>",
    re.IGNORECASE
)

_ANY_TAG = re.compile(r"<[^>]+>")

_EXCESS_BLANKS = re.compile(r"\n{3,}")

_SPACES = re.compile(r"[ \t]{2,}")


def clean_html_text(raw):
    """
    Convert an HTML fragment into plain text:
    - block-level tags become line breaks
    - all other tags are stripped
    - entities are unescaped
    - whitespace is normalized
    """

    if raw is None:
        return ""

    if not isinstance(raw, str):
        return str(raw)

    if "<" not in raw and "&" not in raw:
        return _normalize_whitespace(raw)

    text = _BLOCK_TAGS.sub("\n", raw)

    text = _ANY_TAG.sub(" ", text)

    text = html_lib.unescape(text)

    text = text.replace("\xa0", " ")

    text = _normalize_whitespace(text)

    return text


def _normalize_whitespace(text):

    lines = []

    for line in text.splitlines():

        line = _SPACES.sub(" ", line).strip()

        if line or (lines and lines[-1]):
            lines.append(line)

    cleaned = "\n".join(lines)

    cleaned = _EXCESS_BLANKS.sub("\n\n", cleaned)

    return cleaned.strip()
