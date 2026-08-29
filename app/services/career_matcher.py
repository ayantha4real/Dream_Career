import json
import os

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

CAREER_PROFILES_FILE = os.path.join(
    BASE_DIR,
    "datasets",
    "career_profiles.json"
)

_profiles_cache = None


def load_career_profiles():
    global _profiles_cache

    if _profiles_cache is None:
        with open(
            CAREER_PROFILES_FILE,
            encoding="utf-8"
        ) as f:
            _profiles_cache = json.load(f)

    return _profiles_cache


def match_careers(user_skills):

    careers = load_career_profiles()

    matches = []

    for career, info in careers.items():

        required = info["required_skills"]

        matched = list(set(user_skills) & set(required))

        missing = list(set(required) - set(user_skills))

        score = round(len(matched) / len(required) * 100)

        matches.append({
            "career": career,
            "score": score,
            "matched": matched,
            "missing": missing
        })

    matches.sort(key=lambda x: x["score"], reverse=True)

    return matches
