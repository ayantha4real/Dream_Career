"""
Skill Demand Radar — aggregates which skills appear most often
across all live job descriptions in the registry.

This is computed from real scraped listings, so it reflects the
actual Sri Lankan market captured by the scrapers.
"""

from app.services.jobs.job_database import get_connection
from app.services.skill_extractor import _compiled_patterns


def get_skill_demand(limit=12):
    """
    Returns [{"skill": str, "count": int}] sorted by demand,
    plus total number of descriptions scanned.
    """

    connection = get_connection()

    rows = connection.execute(
        "SELECT description FROM jobs "
        "WHERE description IS NOT NULL AND length(description) > 20"
    ).fetchall()

    connection.close()

    patterns = _compiled_patterns()

    counts = {}

    for row in rows:

        text = row["description"]

        for skill, pattern in patterns:

            if pattern.search(text):
                counts[skill] = counts.get(skill, 0) + 1

    ranked = sorted(
        counts.items(),
        key=lambda item: (-item[1], item[0])
    )[:limit]

    return {
        "skills": [
            {"skill": skill, "count": count}
            for skill, count in ranked
        ],
        "jobs_scanned": len(rows)
    }
