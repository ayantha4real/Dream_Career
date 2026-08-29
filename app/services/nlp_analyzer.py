import re

import spacy


_nlp = None

SECTION_HEADERS = [
    "summary", "objective", "experience", "work experience",
    "education", "skills", "projects", "certifications",
    "achievements", "interests", "references"
]


def _get_nlp():
    global _nlp

    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            _nlp = False

    return _nlp or None


def analyze_resume_text(text):
    """
    spaCy-powered structural analysis of raw resume text.

    Returns entities (organizations, dates, people), noun-phrase
    keywords, detected sections and basic quality metrics.
    """

    result = {
        "organizations": [],
        "dates": [],
        "person": "",
        "keywords": [],
        "sections_found": [],
        "word_count": 0,
        "sentence_count": 0,
        "readability_ok": True
    }

    if not isinstance(text, str) or len(text.strip()) < 30:
        return result

    nlp = _get_nlp()

    if nlp is None:
        return result

    trimmed = text[:20000]

    doc = nlp(trimmed)

    sentences = list(doc.sents)

    result["sentence_count"] = len(sentences)

    organizations = []
    dates = []

    for ent in doc.ents:

        label = ent.label_

        if label in ("ORG", "COMPANY") and len(ent.text) > 2:
            organizations.append(ent.text.strip())

        elif label in ("DATE", "TIME"):
            dates.append(ent.text.strip())

    seen_orgs = set()

    for org in organizations:

        key = org.lower()

        if key not in seen_orgs:
            seen_orgs.add(key)
            result["organizations"].append(org)

    result["organizations"] = result["organizations"][:8]

    result["dates"] = list(dict.fromkeys(dates))[:10]

    for sent in sentences[:3]:

        first_line = sent.text.strip().split("\n")[0]

        words = [t for t in sent if t.is_alpha and len(t.text) > 1]

        if 1 <= len(words) <= 6 and not any(
            ch.isdigit() for ch in first_line
        ):
            result["person"] = first_line.title()
            break

    keyword_scores = {}

    for chunk in doc.noun_chunks:

        phrase = chunk.text.lower().strip(" .,|/")

        if not phrase or len(phrase) < 3 or " " not in phrase:
            continue

        if any(header in phrase for header in SECTION_HEADERS):
            continue

        keyword_scores[phrase] = keyword_scores.get(phrase, 0) + 1

    ranked = sorted(
        keyword_scores.items(),
        key=lambda item: (-item[1], item[0])
    )

    result["keywords"] = [
        phrase.title() for phrase, count in ranked[:12]
    ]

    lowered = trimmed.lower()

    result["sections_found"] = [
        header.title()
        for header in SECTION_HEADERS
        if header in lowered
    ]

    result["word_count"] = len(trimmed.split())

    result["readability_ok"] = result["word_count"] >= 80

    return result


def estimate_experience_years(text):
    """
    Heuristic experience estimation from date ranges like
    '2020 - 2023', 'Jan 2019 to Present', '5 years'.
    """

    if not isinstance(text, str):
        return None

    explicit = re.search(
        r"(\d{1,2})\+?\s*(?:years?|yrs?)",
        text,
        re.IGNORECASE
    )

    if explicit:
        years = int(explicit.group(1))

        if 0 < years <= 45:
            return years

    ranges = re.findall(
        r"(19|20)\d{2}\s*(?:-|–|to)\s*((?:19|20)\d{2}|present)",
        text,
        re.IGNORECASE
    )

    total = 0

    current_year = 2026

    for start_century, end in ranges:

        match_start = re.search(
            r"(19|20)\d{2}",
            f"{start_century}x"
        )

        span_match = re.search(
            rf"{start_century}(\d{{2}})\s*(?:-|–|to)\s*({end})",
            text,
            re.IGNORECASE
        )

        if not span_match:
            continue

        try:
            start_year = int(span_match.group(0)[:4])
        except ValueError:
            continue

        end_token = span_match.group(2).lower()

        if "present" in end_token:
            end_year = current_year
        else:
            end_year = int(end_token)

        if 1980 <= start_year <= end_year <= current_year:
            total += max(0, end_year - start_year)

    return min(total, 45) if total > 0 else None
