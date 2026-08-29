import json
import os


BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

QUALIFICATION_FILE = os.path.join(
    BASE_DIR,
    "datasets",
    "qualification_recommendations.json"
)


def load_qualification_data():

    with open(
        QUALIFICATION_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def recommend_qualifications(missing_skills, max_results=6):

    if not missing_skills:
        return []

    data = load_qualification_data()

    recommendations = []

    for skill in missing_skills:

        if skill not in data:
            continue

        for qualification in data[skill]:

            recommendation = qualification.copy()

            recommendation["skill"] = skill

            recommendations.append(recommendation)

    unique = []
    seen = set()

    for recommendation in recommendations:

        key = (
            recommendation["title"],
            recommendation["provider"]
        )

        if key not in seen:

            seen.add(key)
            unique.append(recommendation)

    return unique[:max_results]