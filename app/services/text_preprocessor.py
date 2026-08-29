import re


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_resume_text(text):
    if not isinstance(text, str):
        return ""

    text = text.replace("\r", " ")
    text = text.replace("\n", " ")

    text = re.sub(r"\s+", " ", text)

    text = text.strip()

    return text