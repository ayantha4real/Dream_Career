import json
import os
import re


BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

VOCABULARY_FILE = os.path.join(
    BASE_DIR,
    "datasets",
    "skill_vocabulary.json"
)


_vocabulary_cache = None
_compiled_patterns_cache = None


def load_skill_vocabulary():
    global _vocabulary_cache

    if _vocabulary_cache is None:
        with open(
            VOCABULARY_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            vocabulary = json.load(file)

        skills = []

        for category_skills in vocabulary.values():
            skills.extend(category_skills)

        _vocabulary_cache = sorted(
            set(skills),
            key=len,
            reverse=True
        )

    return _vocabulary_cache


def _compiled_patterns():
    global _compiled_patterns_cache

    if _compiled_patterns_cache is None:

        _compiled_patterns_cache = [
            (
                skill,
                re.compile(
                    r"(?<!\w)" + re.escape(skill) + r"(?!\w)",
                    re.IGNORECASE
                )
            )
            for skill in load_skill_vocabulary()
        ]

    return _compiled_patterns_cache


def extract_skills(text):

    if not isinstance(text, str):
        return []

    found = [
        skill
        for skill, pattern in _compiled_patterns()
        if pattern.search(text)
    ]

    return sorted(
        set(found),
        key=str.lower
    )
