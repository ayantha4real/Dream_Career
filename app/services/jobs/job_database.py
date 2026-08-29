
import json
import os
import re
import sqlite3


BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        ".."
    )
)

DATABASE_FOLDER = os.path.join(
    BASE_DIR,
    "database"
)

DATABASE_PATH = os.path.join(
    DATABASE_FOLDER,
    "dreamcareer.db"
)


def get_connection():
    os.makedirs(
        DATABASE_FOLDER,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


def create_jobs_table():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER,
            title TEXT NOT NULL,
            company TEXT,
            location TEXT,
            category TEXT,
            description TEXT,
            education TEXT,
            experience TEXT,
            salary TEXT,
            job_type TEXT,
            source TEXT NOT NULL,
            url TEXT UNIQUE,
            posted_date TEXT,
            expiry_date TEXT,
            scraped_at TEXT NOT NULL
        )
        """
    )

    existing_columns = [
        row["name"]
        for row in cursor.execute(
            "PRAGMA table_info(jobs)"
        ).fetchall()
    ]

    new_columns = {
        "job_id": "INTEGER",
        "education": "TEXT",
        "experience": "TEXT",
        "salary": "TEXT",
        "job_type": "TEXT"
    }

    for column, column_type in new_columns.items():
        if column not in existing_columns:
            cursor.execute(
                f"ALTER TABLE jobs ADD COLUMN {column} {column_type}"
            )

    connection.commit()
    connection.close()


def save_job(job):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO jobs (
            job_id,
            title,
            company,
            location,
            category,
            description,
            education,
            experience,
            salary,
            job_type,
            source,
            url,
            posted_date,
            expiry_date,
            scraped_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            job.get("job_id"),
            job.get("title"),
            job.get("company"),
            job.get("location"),
            job.get("category"),
            job.get("description"),
            job.get("education"),
            job.get("experience"),
            job.get("salary"),
            job.get("job_type"),
            job.get("source"),
            job.get("url"),
            job.get("posted_date"),
            job.get("expiry_date"),
            job.get("scraped_at")
        )
    )

    connection.commit()
    connection.close()


CATEGORY_MAP_FILE = os.path.join(
    BASE_DIR,
    "datasets",
    "job_category_map.json"
)


def load_category_mapping():
    with open(
        CATEGORY_MAP_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def split_category(category):
    if not category:
        return []

    return [
        token.strip()
        for token in category.split(",")
        if token.strip()
    ]


def get_category_group(category_token, mapping=None):
    if mapping is None:
        mapping = load_category_mapping()

    token_to_group = {}

    for group, tokens in mapping["groups"].items():

        for token in tokens:
            token_to_group[
                token.lower().strip()
            ] = group

    return token_to_group.get(
        str(category_token).lower().strip(),
        mapping["fallback_group"]
    )


def get_job_category_groups(job, mapping=None):
    groups = []

    for token in split_category(
        job["category"]
    ):

        group = get_category_group(
            token,
            mapping
        )

        if group not in groups:
            groups.append(group)

    return groups


def get_job_categories():
    mapping = load_category_mapping()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT category
        FROM jobs
        WHERE category IS NOT NULL
        """
    )

    rows = cursor.fetchall()
    connection.close()

    counts = {}

    for row in rows:

        for group in set(
            get_category_group(token, mapping)
            for token in split_category(row["category"])
        ):
            counts[group] = counts.get(group, 0) + 1

    return sorted(
        counts.items(),
        key=lambda item: (-item[1], item[0])
    )


def get_jobs(limit=20, search=None, category=None):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM jobs
        ORDER BY id DESC
        """
    )

    jobs = cursor.fetchall()

    connection.close()

    if search:
        needle = search.lower().strip()

        jobs = [
            job for job in jobs
            if needle in (job["title"] or "").lower()
            or needle in (job["company"] or "").lower()
            or needle in (job["description"] or "").lower()
        ]

    if category:
        mapping = load_category_mapping()

        jobs = [
            job for job in jobs
            if category in get_job_category_groups(
                job,
                mapping
            )
        ]

    return jobs[:limit]


def get_job(job_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM jobs
        WHERE id = ?
        OR job_id = ?
        LIMIT 1
        """,
        (
            job_id,
            job_id
        )
    )

    job = cursor.fetchone()

    connection.close()

    return job


def normalize_text(text):
    if not text:
        return ""

    text = str(text).lower()

    text = text.replace(
        "&",
        " and "
    )

    text = text.replace(
        "’",
        "'"
    )

    text = text.replace(
        "–",
        "-"
    )

    text = text.replace(
        "—",
        "-"
    )

    text = re.sub(
        r"[^a-z0-9+#./' -]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def normalize_phrase(text):
    text = normalize_text(text)

    text = text.replace(
        "-",
        " "
    )

    text = text.replace(
        "/",
        " "
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def canonical_career_name(career_name):
    career = normalize_phrase(
        career_name
    )

    aliases = {
        "full stackdeveloper": "full stack developer",
        "full stack development": "full stack developer",
        "fullstack developer": "full stack developer",
        "frontend": "frontend developer",
        "front end developer": "frontend developer",
        "front end": "frontend developer",
        "backend": "backend developer",
        "back end developer": "backend developer",
        "back end": "backend developer",
        "data science": "data scientist",
        "data science associate": "data scientist",
        "ml engineer": "machine learning engineer",
        "machine learning": "machine learning engineer",
        "software development": "software engineer",
        "software developer": "software engineer"
    }

    return aliases.get(
        career,
        career
    )


def phrase_in_text(phrase, text):
    phrase = normalize_phrase(
        phrase
    )

    text = normalize_phrase(
        text
    )

    if not phrase or not text:
        return False

    pattern = (
        r"(?<![a-z0-9])"
        + re.escape(phrase)
        + r"(?![a-z0-9])"
    )

    return re.search(
        pattern,
        text
    ) is not None


def tokenize(text):
    text = normalize_phrase(
        text
    )

    return set(
        word
        for word in text.split()
        if len(word) > 2
    )


def extract_experience_years(experience):
    if not experience:
        return 0

    text = normalize_text(
        experience
    )

    if "no experience" in text:
        return 0

    if "intern" in text:
        return 0

    if "fresh" in text:
        return 0

    numbers = re.findall(
        r"\d+(?:\.\d+)?",
        text
    )

    if not numbers:
        return 0

    values = [
        float(number)
        for number in numbers
    ]

    return max(values)


def experience_matches(
    candidate_experience,
    job_experience
):
    if not candidate_experience:
        return True

    job_text = normalize_text(
        job_experience
    )

    if not job_text:
        return True

    if job_text in [
        "-",
        "any",
        "not specified",
        "not mentioned",
        "n/a"
    ]:
        return True

    candidate_years = extract_experience_years(
        candidate_experience
    )

    if "no experience" in job_text:
        return True

    if "fresh" in job_text:
        return candidate_years <= 1

    if "intern" in job_text:
        return candidate_years <= 1

    ranges = re.findall(
        r"(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)",
        job_text
    )

    if ranges:
        minimum = float(
            ranges[0][0]
        )

        return candidate_years >= minimum - 1

    plus_match = re.search(
        r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)",
        job_text
    )

    if plus_match:
        minimum = float(
            plus_match.group(1)
        )

        return candidate_years >= minimum - 1

    return True


def experience_score(
    candidate_experience,
    job_experience
):
    if not candidate_experience:
        return 0

    job_text = normalize_text(
        job_experience
    )

    if not job_text:
        return 3

    if job_text in [
        "-",
        "any",
        "not specified",
        "not mentioned",
        "n/a"
    ]:
        return 3

    candidate_years = extract_experience_years(
        candidate_experience
    )

    job_years = extract_experience_years(
        job_experience
    )

    if "no experience" in job_text:
        return 8

    if "fresh" in job_text:
        return 8 if candidate_years <= 1 else 5

    if "intern" in job_text:
        return 8 if candidate_years <= 1 else 5

    if candidate_years >= job_years:
        return 8

    if candidate_years >= job_years - 1:
        return 5

    return 2


def education_matches(
    candidate_education,
    job_education
):
    if not candidate_education:
        return True

    candidate_text = normalize_phrase(
        candidate_education
    )

    job_text = normalize_phrase(
        job_education
    )

    if not job_text:
        return True

    if job_text in [
        "-",
        "any",
        "not specified",
        "not mentioned",
        "n/a"
    ]:
        return True

    education_levels = {
        "ordinary level": 1,
        "o level": 1,
        "gcse": 1,
        "advanced level": 2,
        "a level": 2,
        "certificate": 3,
        "diploma": 4,
        "hnd": 5,
        "degree": 6,
        "bachelor": 6,
        "bachelors": 6,
        "bachelor degree": 6,
        "bachelors degree": 6,
        "master": 7,
        "masters": 7,
        "masters degree": 7,
        "master degree": 7,
        "phd": 8,
        "doctorate": 8
    }

    candidate_level = 0
    job_level = 0

    for keyword, level in education_levels.items():
        if keyword in candidate_text:
            candidate_level = max(
                candidate_level,
                level
            )

        if keyword in job_text:
            job_level = max(
                job_level,
                level
            )

    if job_level == 0:
        return True

    return candidate_level >= job_level


def education_score(
    candidate_education,
    job_education
):
    if not candidate_education:
        return 0

    job_text = normalize_phrase(
        job_education
    )

    if not job_text:
        return 4

    if job_text in [
        "-",
        "any",
        "not specified",
        "not mentioned",
        "n/a"
    ]:
        return 4

    if education_matches(
        candidate_education,
        job_education
    ):
        return 8

    return 0


CAREER_PROFILES = {

    "data scientist": {
        "aliases": [
            "data scientist",
            "junior data scientist",
            "data science",
            "data science associate"
        ],
        "strong_roles": [
            "data scientist",
            "junior data scientist",
            "data science associate",
            "machine learning scientist"
        ],
        "supporting_roles": [
            "data analyst",
            "business intelligence analyst",
            "ai engineer",
            "artificial intelligence engineer",
            "machine learning engineer"
        ],
        "core_skills": [
            "machine learning",
            "data science",
            "scikit-learn",
            "tensorflow",
            "pytorch",
            "deep learning",
            "artificial intelligence",
            "numpy"
        ],
        "supporting_skills": [
            "python",
            "sql",
            "statistics",
            "pandas",
            "power bi"
        ],
        "skills": [
            "python",
            "sql",
            "machine learning",
            "data science",
            "statistics",
            "pandas",
            "numpy",
            "scikit-learn",
            "tensorflow",
            "pytorch",
            "deep learning",
            "artificial intelligence",
            "power bi"
        ],
        "exclude": [
            "data entry",
            "data entry clerk",
            "data entry associate",
            "data entry operator",
            "data collection"
        ]
    },

    "data analyst": {
        "aliases": [
            "data analyst",
            "junior data analyst",
            "data analytics",
            "analytics analyst",
            "reporting analyst",
            "business intelligence analyst",
            "bi analyst"
        ],
        "strong_roles": [
            "data analyst",
            "junior data analyst",
            "data analytics",
            "reporting analyst",
            "business intelligence analyst",
            "bi analyst"
        ],
        "supporting_roles": [
            "business analyst",
            "research analyst"
        ],
        "core_skills": [
            "sql"
        ],
        "supporting_skills": [
            "python",
            "pandas",
            "excel",
            "power bi",
            "tableau",
            "statistics",
            "data analysis",
            "data visualization",
            "reporting"
        ],
        "skills": [
            "sql",
            "python",
            "pandas",
            "excel",
            "power bi",
            "tableau",
            "statistics",
            "data analysis",
            "data visualization",
            "reporting"
        ],
        "exclude": [
            "data entry",
            "data entry clerk",
            "data entry associate",
            "data entry operator",
            "accounts assistant",
            "account assistant",
            "accountant",
            "management accountant",
            "finance assistant",
            "stores assistant",
            "customer relations officer",
            "graphic designer"
        ]
    },

    "machine learning engineer": {
        "aliases": [
            "machine learning engineer",
            "ml engineer"
        ],
        "strong_roles": [
            "machine learning engineer",
            "ml engineer",
            "machine learning developer",
            "ai engineer",
            "artificial intelligence engineer"
        ],
        "supporting_roles": [
            "software engineer",
            "software developer",
            "data scientist"
        ],
        "core_skills": [
            "machine learning",
            "tensorflow",
            "pytorch",
            "scikit-learn",
            "deep learning",
            "artificial intelligence"
        ],
        "supporting_skills": [
            "python",
            "sql",
            "numpy",
            "pandas",
            "docker"
        ],
        "skills": [
            "python",
            "machine learning",
            "tensorflow",
            "pytorch",
            "scikit-learn",
            "deep learning",
            "artificial intelligence",
            "sql",
            "numpy",
            "pandas",
            "docker"
        ],
        "exclude": []
    },

    "software engineer": {
        "aliases": [
            "software engineer",
            "software developer",
            "software programmer"
        ],
        "strong_roles": [
            "software engineer",
            "software developer",
            "software programmer",
            "application developer",
            "systems developer"
        ],
        "supporting_roles": [
            "developer",
            "programmer"
        ],
        "core_skills": [
            "programming",
            "git",
            "rest api"
        ],
        "supporting_skills": [
            "python",
            "java",
            "javascript",
            "c++",
            "c#",
            "docker",
            "sql"
        ],
        "skills": [
            "python",
            "java",
            "javascript",
            "c++",
            "c#",
            "programming",
            "git",
            "rest api",
            "docker",
            "sql"
        ],
        "exclude": [
            "graphic designer",
            "data entry",
            "accounts assistant",
            "account assistant",
            "accountant"
        ]
    },

    "web developer": {
        "aliases": [
            "web developer",
            "web development",
            "website developer"
        ],
        "strong_roles": [
            "web developer",
            "website developer"
        ],
        "supporting_roles": [
            "full stack developer",
            "frontend developer",
            "front end developer",
            "backend developer",
            "back end developer"
        ],
        "core_skills": [
            "html",
            "css",
            "javascript"
        ],
        "supporting_skills": [
            "react",
            "bootstrap",
            "flask",
            "django",
            "php",
            "node.js",
            "node",
            "sql",
            "python",
            "git"
        ],
        "skills": [
            "html",
            "css",
            "javascript",
            "react",
            "bootstrap",
            "flask",
            "django",
            "php",
            "node.js",
            "node",
            "sql",
            "python",
            "git"
        ],
        "exclude": [
            "graphic designer",
            "graphic design"
        ]
    },

    "full stack developer": {
        "aliases": [
            "full stack developer",
            "full stackdeveloper",
            "fullstack developer"
        ],
        "strong_roles": [
            "full stack developer",
            "full stackdeveloper",
            "fullstack developer"
        ],
        "supporting_roles": [
            "web developer"
        ],
        "core_skills": [
            "html",
            "css",
            "javascript",
            "sql"
        ],
        "supporting_skills": [
            "react",
            "node.js",
            "node",
            "python",
            "flask",
            "django",
            "php",
            "git"
        ],
        "skills": [
            "html",
            "css",
            "javascript",
            "react",
            "node.js",
            "node",
            "python",
            "flask",
            "django",
            "php",
            "sql",
            "git"
        ],
        "exclude": [
            "graphic designer",
            "graphic design"
        ]
    },

    "backend developer": {
        "aliases": [
            "backend developer",
            "back end developer",
            "backend"
        ],
        "strong_roles": [
            "backend developer",
            "back end developer"
        ],
        "supporting_roles": [
            "software developer",
            "software engineer",
            "web developer"
        ],
        "core_skills": [
            "python",
            "sql",
            "rest api"
        ],
        "supporting_skills": [
            "java",
            "node.js",
            "node",
            "flask",
            "django",
            "php",
            "docker",
            "git"
        ],
        "skills": [
            "python",
            "java",
            "node.js",
            "node",
            "flask",
            "django",
            "php",
            "sql",
            "rest api",
            "docker",
            "git"
        ],
        "exclude": [
            "graphic designer",
            "graphic design"
        ]
    },

    "frontend developer": {
        "aliases": [
            "frontend developer",
            "front end developer",
            "frontend"
        ],
        "strong_roles": [
            "frontend developer",
            "front end developer"
        ],
        "supporting_roles": [
            "web developer"
        ],
        "core_skills": [
            "html",
            "css",
            "javascript"
        ],
        "supporting_skills": [
            "react",
            "bootstrap",
            "vue",
            "angular",
            "typescript",
            "git"
        ],
        "skills": [
            "html",
            "css",
            "javascript",
            "react",
            "bootstrap",
            "vue",
            "angular",
            "typescript",
            "git"
        ],
        "exclude": [
            "graphic designer",
            "graphic design"
        ]
    },

    "business analyst": {
        "aliases": [
            "business analyst",
            "business analysis"
        ],
        "strong_roles": [
            "business analyst",
            "business analysis"
        ],
        "supporting_roles": [
            "business intelligence analyst",
            "process analyst"
        ],
        "core_skills": [
            "business intelligence",
            "requirements"
        ],
        "supporting_skills": [
            "sql",
            "excel",
            "power bi",
            "tableau",
            "reporting",
            "data analysis",
            "analytics"
        ],
        "skills": [
            "sql",
            "excel",
            "power bi",
            "tableau",
            "business intelligence",
            "requirements",
            "reporting",
            "data analysis",
            "analytics"
        ],
        "exclude": [
            "accounts assistant",
            "account assistant",
            "accountant",
            "management accountant",
            "finance assistant",
            "stores assistant"
        ]
    },

    "project manager": {
        "aliases": [
            "project manager",
            "project management"
        ],
        "strong_roles": [
            "project manager",
            "project management"
        ],
        "supporting_roles": [
            "program manager",
            "programme manager",
            "project coordinator"
        ],
        "core_skills": [
            "project management",
            "agile",
            "scrum"
        ],
        "supporting_skills": [
            "planning",
            "coordination",
            "leadership",
            "jira",
            "communication"
        ],
        "skills": [
            "project management",
            "planning",
            "coordination",
            "leadership",
            "agile",
            "scrum",
            "jira",
            "communication"
        ],
        "exclude": []
    },

    "digital marketer": {
        "aliases": [
            "digital marketer",
            "digital marketing"
        ],
        "strong_roles": [
            "digital marketer",
            "digital marketing specialist",
            "digital marketing executive",
            "digital marketing"
        ],
        "supporting_roles": [
            "marketing executive",
            "marketing specialist",
            "seo specialist",
            "social media specialist"
        ],
        "core_skills": [
            "digital marketing",
            "marketing"
        ],
        "supporting_skills": [
            "seo",
            "social media",
            "advertising",
            "content marketing",
            "google ads",
            "analytics",
            "campaign"
        ],
        "skills": [
            "digital marketing",
            "marketing",
            "seo",
            "social media",
            "advertising",
            "content marketing",
            "google ads",
            "analytics",
            "campaign"
        ],
        "exclude": []
    },

    "graphic designer": {
        "aliases": [
            "graphic designer",
            "graphic design"
        ],
        "strong_roles": [
            "graphic designer",
            "graphic design"
        ],
        "supporting_roles": [
            "visual designer",
            "ui designer",
            "creative designer"
        ],
        "core_skills": [
            "graphic design",
            "adobe"
        ],
        "supporting_skills": [
            "photoshop",
            "illustrator",
            "figma",
            "creative",
            "indesign",
            "ui design"
        ],
        "skills": [
            "photoshop",
            "illustrator",
            "adobe",
            "graphic design",
            "figma",
            "creative",
            "indesign",
            "ui design"
        ],
        "exclude": []
    },

    "mobile developer": {
        "aliases": [
            "mobile developer",
            "mobile app developer"
        ],
        "strong_roles": [
            "mobile developer",
            "mobile app developer",
            "android developer",
            "ios developer",
            "flutter developer"
        ],
        "supporting_roles": [
            "software developer",
            "application developer"
        ],
        "core_skills": [
            "mobile development",
            "flutter",
            "kotlin",
            "swift"
        ],
        "supporting_skills": [
            "dart",
            "android",
            "java",
            "react native"
        ],
        "skills": [
            "flutter",
            "dart",
            "android",
            "kotlin",
            "java",
            "swift",
            "react native",
            "mobile development"
        ],
        "exclude": []
    }
}


def get_career_profile(
    career_name
):
    career = normalize_phrase(
        career_name
    )

    career = career.replace(
        "full stackdeveloper",
        "full stack developer"
    )

    career = career.replace(
        "fullstack developer",
        "full stack developer"
    )

    career = career.replace(
        "front end developer",
        "frontend developer"
    )

    career = career.replace(
        "back end developer",
        "backend developer"
    )

    direct_aliases = {
        "full stack developer": "full stack developer",
        "frontend developer": "frontend developer",
        "backend developer": "backend developer",
        "front end developer": "frontend developer",
        "back end developer": "backend developer",
        "web development": "web developer",
        "website developer": "web developer"
    }

    if career in direct_aliases:
        career = direct_aliases[
            career
        ]

    if career in CAREER_PROFILES:
        return CAREER_PROFILES[
            career
        ]

    for profile_name, profile in CAREER_PROFILES.items():

        normalized_profile_name = normalize_phrase(
            profile_name
        )

        if career == normalized_profile_name:
            return profile

        aliases = profile.get(
            "aliases",
            []
        )

        for alias in aliases:

            normalized_alias = normalize_phrase(
                alias
            )

            normalized_alias = normalized_alias.replace(
                "full stackdeveloper",
                "full stack developer"
            )

            normalized_alias = normalized_alias.replace(
                "fullstack developer",
                "full stack developer"
            )

            normalized_alias = normalized_alias.replace(
                "front end developer",
                "frontend developer"
            )

            normalized_alias = normalized_alias.replace(
                "back end developer",
                "backend developer"
            )

            if career == normalized_alias:
                return profile

    return {
        "aliases": [
            career
        ],
        "strong_roles": [
            career
        ],
        "supporting_roles": [],
        "skills": [],
        "exclude": []
    }




def get_career_match(
    job,
    career_name
):
    profile = get_career_profile(
        career_name
    )

    if hasattr(
        job,
        "keys"
    ):

        title = normalize_phrase(
            job["title"] or ""
        )

        category = normalize_phrase(
            job["category"] or ""
        )

        description = normalize_phrase(
            job["description"] or ""
        )

    else:

        title = normalize_phrase(
            job.get(
                "title",
                ""
            )
        )

        category = normalize_phrase(
            job.get(
                "category",
                ""
            )
        )

        description = normalize_phrase(
            job.get(
                "description",
                ""
            )
        )

    combined_text = (
        title
        + " "
        + category
        + " "
        + description
    ).strip()

    exclude_matches = []

    for excluded in profile.get(
        "exclude",
        []
    ):

        normalized_excluded = normalize_phrase(
            excluded
        )

        if phrase_in_text(
            normalized_excluded,
            title
        ):

            exclude_matches.append(
                normalized_excluded
            )

        elif phrase_in_text(
            normalized_excluded,
            category
        ):

            exclude_matches.append(
                normalized_excluded
            )

    if exclude_matches:

        return {
            "matched": False,
            "score": 0,
            "reason": "excluded",
            "matches": [],
            "matched_skills": []
        }

    strong_title_matches = []

    for role in profile.get(
        "strong_roles",
        []
    ):

        normalized_role = normalize_phrase(
            role
        )

        if phrase_in_text(
            normalized_role,
            title
        ):

            strong_title_matches.append(
                normalized_role
            )

    if strong_title_matches:

        return {
            "matched": True,
            "score": 100,
            "reason": "strong_title",
            "matches": list(
                dict.fromkeys(
                    strong_title_matches
                )
            ),
            "matched_skills": []
        }

    strong_category_matches = []

    for role in profile.get(
        "strong_roles",
        []
    ):

        normalized_role = normalize_phrase(
            role
        )

        if phrase_in_text(
            normalized_role,
            category
        ):

            strong_category_matches.append(
                normalized_role
            )

    if strong_category_matches:

        return {
            "matched": True,
            "score": 75,
            "reason": "strong_category",
            "matches": list(
                dict.fromkeys(
                    strong_category_matches
                )
            ),
            "matched_skills": []
        }

    supporting_title_matches = []

    for role in profile.get(
        "supporting_roles",
        []
    ):

        normalized_role = normalize_phrase(
            role
        )

        if phrase_in_text(
            normalized_role,
            title
        ):

            supporting_title_matches.append(
                normalized_role
            )

    if supporting_title_matches:

        return {
            "matched": True,
            "score": 60,
            "reason": "supporting_title",
            "matches": list(
                dict.fromkeys(
                    supporting_title_matches
                )
            ),
            "matched_skills": []
        }

    supporting_category_matches = []

    for role in profile.get(
        "supporting_roles",
        []
    ):

        normalized_role = normalize_phrase(
            role
        )

        if phrase_in_text(
            normalized_role,
            category
        ):

            supporting_category_matches.append(
                normalized_role
            )

    if supporting_category_matches:

        return {
            "matched": True,
            "score": 40,
            "reason": "supporting_category",
            "matches": list(
                dict.fromkeys(
                    supporting_category_matches
                )
            ),
            "matched_skills": []
        }

    career_skills = profile.get(
        "skills",
        []
    )

    core_skills = profile.get(
        "core_skills",
        []
    )

    supporting_skills = profile.get(
        "supporting_skills",
        []
    )

    matched_career_skills = []
    matched_core_skills = []
    matched_supporting_skills = []

    for skill in career_skills:

        normalized_skill = normalize_phrase(
            skill
        )

        if not normalized_skill:
            continue

        if phrase_in_text(
            normalized_skill,
            combined_text
        ):

            matched_career_skills.append(
                skill
            )

            if skill in core_skills:
                matched_core_skills.append(
                    skill
                )
            elif skill in supporting_skills:
                matched_supporting_skills.append(
                    skill
                )

    matched_career_skills = list(
        dict.fromkeys(
            matched_career_skills
        )
    )

    matched_core_skills = list(
        dict.fromkeys(
            matched_core_skills
        )
    )

    matched_supporting_skills = list(
        dict.fromkeys(
            matched_supporting_skills
        )
    )

    total_career_skills = len(
        career_skills
    )

    matched_skill_count = len(
        matched_career_skills
    )

    matched_core_count = len(
        matched_core_skills
    )

    matched_supporting_count = len(
        matched_supporting_skills
    )

    business_contradiction_keywords = [
        "business",
        "support",
        "executive",
        "management",
        "accounting",
        "account",
        "finance",
        "sales"
    ]

    title_has_contradiction = any(
        keyword in title
        for keyword in business_contradiction_keywords
    )

    data_specific_careers = [
        "data scientist",
        "data analyst",
        "machine learning engineer"
    ]

    career_normalized = normalize_phrase(
        career_name
    )

    is_data_career = any(
        data_career in career_normalized
        for data_career in data_specific_careers
    )

    if (
        matched_core_count >= 2
        and total_career_skills > 0
    ):

        skill_ratio = (
            matched_skill_count
            / total_career_skills
        )

        skill_score = 55 + (
            skill_ratio * 20
        )

        skill_score = min(
            75,
            skill_score
        )

        return {
            "matched": True,
            "score": round(
                skill_score
            ),
            "reason": "career_skills",
            "matches": matched_career_skills,
            "matched_skills": matched_career_skills
        }

    if (
        matched_core_count == 1
        and matched_supporting_count >= 4
        and total_career_skills > 0
    ):

        skill_ratio = (
            matched_skill_count
            / total_career_skills
        )

        if skill_ratio < 0.35:
            return {
                "matched": False,
                "score": 0,
                "reason": "no_match",
                "matches": [],
                "matched_skills": []
            }

        if (
            is_data_career
            and title_has_contradiction
        ):
            return {
                "matched": False,
                "score": 0,
                "reason": "no_match",
                "matches": [],
                "matched_skills": []
            }

        skill_score = 45 + (
            skill_ratio * 15
        )

        skill_score = min(
            60,
            skill_score
        )

        return {
            "matched": True,
            "score": round(
                skill_score
            ),
            "reason": "career_skills",
            "matches": matched_career_skills,
            "matched_skills": matched_career_skills
        }

    if (
        matched_skill_count >= 5
        and matched_core_count == 0
        and total_career_skills > 0
    ):

        skill_ratio = (
            matched_skill_count
            / total_career_skills
        )

        if skill_ratio < 0.45:
            return {
                "matched": False,
                "score": 0,
                "reason": "no_match",
                "matches": [],
                "matched_skills": []
            }

        skill_score = 40 + (
            skill_ratio * 10
        )

        skill_score = min(
            50,
            skill_score
        )

        return {
            "matched": True,
            "score": round(
                skill_score
            ),
            "reason": "career_skills",
            "matches": matched_career_skills,
            "matched_skills": matched_career_skills
        }

    return {
        "matched": False,
        "score": 0,
        "reason": "no_match",
        "matches": [],
        "matched_skills": []
    }







def get_skill_matches(
    job,
    skills
):
    if not skills:
        return []

    title = normalize_phrase(
        job["title"]
    )

    category = normalize_phrase(
        job["category"]
    )

    description = normalize_phrase(
        job["description"]
    )

    searchable_text = (
        title
        + " "
        + category
        + " "
        + description
    )

    matched_skills = []

    for skill in skills:

        skill_text = normalize_phrase(
            skill
        )

        if not skill_text:
            continue

        if len(skill_text) < 2:
            continue

        if phrase_in_text(
            skill_text,
            searchable_text
        ):
            matched_skills.append(
                skill
            )

    return list(
        dict.fromkeys(
            matched_skills
        )
    )


def calculate_skill_score(
    job,
    skills
):
    if not skills:
        return 0, []

    title = normalize_phrase(
        job["title"]
    )

    category = normalize_phrase(
        job["category"]
    )

    description = normalize_phrase(
        job["description"]
    )

    matched_skills = get_skill_matches(
        job,
        skills
    )

    score = 0

    for skill in matched_skills:

        skill_text = normalize_phrase(
            skill
        )

        if phrase_in_text(
            skill_text,
            title
        ):
            score += 20

        elif phrase_in_text(
            skill_text,
            category
        ):
            score += 12

        elif phrase_in_text(
            skill_text,
            description
        ):
            score += 6

    return score, matched_skills





def calculate_job_score(
    job,
    skills=None,
    careers=None,
    candidate_education="",
    candidate_experience=""
):
    skills = skills or []
    careers = careers or []

    empty_result = {
        "score": 0,
        "career_matches": [],
        "matched_skills": [],
        "career_reasons": [],
        "career_prediction_score": 0,
        "career_score": 0,
        "skill_score": 0,
        "education_score": 0,
        "experience_score": 0,
        "recommendation_type": "No Match",
        "match_explanation": "Job does not match candidate profile",
        "eligible": False
    }

    if not careers and not skills:
        return empty_result

    if candidate_education:

        if not education_matches(
            candidate_education,
            job["education"]
        ):
            return empty_result

    if candidate_experience:

        if not experience_matches(
            candidate_experience,
            job["experience"]
        ):
            return empty_result

    career_matches = []
    career_reasons = []

    best_career_prediction = 0
    best_career_match_score = 0

    for career in careers:

        if isinstance(
            career,
            dict
        ):
            career_name = career.get(
                "career",
                ""
            )

            prediction_score = float(
                career.get(
                    "score",
                    0
                ) or 0
            )

        else:
            career_name = str(
                career
            )

            prediction_score = 0

        if not career_name:
            continue

        result = get_career_match(
            job,
            career_name
        )

        if not result["matched"]:
            continue

        normalized_career = canonical_career_name(
            career_name
        )

        career_matches.append(
            normalized_career
        )

        result_reason = result.get(
            "reason",
            ""
        )

        if result_reason:

            career_reasons.append(
                result_reason
            )

        for matched_skill in result.get(
            "matched_skills",
            []
        ):

            career_reasons.append(
                "career_skill:" + matched_skill
            )

        weighted_match = (
            result["score"]
            * prediction_score
            / 100
        )

        if weighted_match > best_career_match_score:

            best_career_match_score = (
                weighted_match
            )

            best_career_prediction = (
                prediction_score
            )

    career_matches = list(
        dict.fromkeys(
            career_matches
        )
    )

    career_reasons = list(
        dict.fromkeys(
            career_reasons
        )
    )

    career_score = best_career_match_score

    skill_raw_score, matched_skills = calculate_skill_score(
        job,
        skills
    )

    if skills:

        maximum_skill_score = (
            20 * len(skills)
        )

        if maximum_skill_score > 0:

            skill_score = min(
                100,
                (
                    skill_raw_score
                    / maximum_skill_score
                ) * 100
            )

        else:
            skill_score = 0

    else:
        skill_score = 0

    if candidate_education:

        education_score = (
            100
            if education_matches(
                candidate_education,
                job["education"]
            )
            else 0
        )

    else:
        education_score = 0

    if candidate_experience:

        experience_score = (
            100
            if experience_matches(
                candidate_experience,
                job["experience"]
            )
            else 0
        )

    else:
        experience_score = 0

    has_career_match = bool(
        career_matches
    )

    has_skill_match = bool(
        matched_skills
    )

    if has_career_match and has_skill_match:

        recommendation_type = (
            "Career + Skill Match"
        )

    elif has_career_match:

        recommendation_type = (
            "Primary Career Match"
        )

    elif has_skill_match:

        recommendation_type = (
            "Skill-Based Alternative"
        )

    else:

        recommendation_type = (
            "No Match"
        )

    if not has_career_match and not has_skill_match:

        return {
            "score": 0,
            "career_matches": [],
            "matched_skills": [],
            "career_reasons": [],
            "career_prediction_score": 0,
            "career_score": 0,
            "skill_score": round(
                skill_score
            ),
            "education_score": education_score,
            "experience_score": experience_score,
            "recommendation_type": "No Match",
            "match_explanation": "No career or skill match found",
            "eligible": True
        }

    component_weights = {
        "career": 50,
        "skills": 30,
        "education": 10,
        "experience": 10
    }

    active_weight = 0
    weighted_total = 0

    boosted_career_score = career_score
    
    if careers and has_career_match:

        active_weight += component_weights[
            "career"
        ]

        boosted_career_score = career_score * (
            1 + (best_career_prediction / 100) * 0.3
        )

        weighted_total += (
            boosted_career_score
            * component_weights[
                "career"
            ]
        )

    if skills:

        active_weight += component_weights[
            "skills"
        ]

        weighted_total += (
            skill_score
            * component_weights[
                "skills"
            ]
        )

    if candidate_education:

        active_weight += component_weights[
            "education"
        ]

        weighted_total += (
            education_score
            * component_weights[
                "education"
            ]
        )

    if candidate_experience:

        active_weight += component_weights[
            "experience"
        ]

        weighted_total += (
            experience_score
            * component_weights[
                "experience"
            ]
        )

    if active_weight > 0:

        final_score = (
            weighted_total
            / active_weight
        )

    else:
        final_score = 0

    match_explanation = ""
    
    if recommendation_type == "Career + Skill Match":
        match_explanation = (
            f"Strong match: {len(career_matches)} predicted career "
            f"({'careers' if len(career_matches) > 1 else 'career'}) "
            f"found in job with {len(matched_skills)} skill "
            f"({'matches' if len(matched_skills) > 1 else 'match'})"
        )
    elif recommendation_type == "Primary Career Match":
        top_match = career_matches[0] if career_matches else "Unknown"
        match_explanation = (
            f"Career match: Job title/description matches your predicted "
            f"{top_match} career ({best_career_prediction:.0f}% confidence)"
        )
    elif recommendation_type == "Skill-Based Alternative":
        if matched_skills:
            skills_str = ", ".join(matched_skills[:3])
            if len(matched_skills) > 3:
                skills_str += f", +{len(matched_skills)-3} more"
            match_explanation = (
                f"Skills match: Your skills ({skills_str}) are found "
                f"in this job, though career does not directly match"
            )
        else:
            match_explanation = (
                "Limited skill overlap found in this role"
            )
    else:
        match_explanation = "Job matches your profile"

    return {
        "score": round(
            min(
                100,
                final_score
            )
        ),
        "career_matches": career_matches,
        "matched_skills": matched_skills,
        "career_reasons": career_reasons,
        "career_prediction_score": best_career_prediction,
        "career_score": round(
            career_score
        ),
        "skill_score": round(
            skill_score
        ),
        "education_score": education_score,
        "experience_score": experience_score,
        "recommendation_type": recommendation_type,
        "match_explanation": match_explanation,
        "eligible": True
    }



def get_recommended_jobs(
    skills=None,
    careers=None,
    candidate_education="",
    candidate_experience="",
    limit=10
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM jobs
        ORDER BY id DESC
        """
    )

    jobs = cursor.fetchall()

    connection.close()

    scored_jobs = []

    for job in jobs:

        result = calculate_job_score(
            job=job,
            skills=skills,
            careers=careers,
            candidate_education=candidate_education,
            candidate_experience=candidate_experience
        )

        if not result["eligible"]:
            continue

        if result["score"] <= 0:
            continue

        job_data = dict(
            job
        )

        job_data["match_score"] = result[
            "score"
        ]

        job_data["career_matches"] = result[
            "career_matches"
        ]

        job_data["matched_skills"] = result[
            "matched_skills"
        ]

        job_data["career_reasons"] = result[
            "career_reasons"
        ]

        job_data["career_prediction_score"] = result[
            "career_prediction_score"
        ]

        job_data["career_score"] = result[
            "career_score"
        ]

        job_data["skill_score"] = result[
            "skill_score"
        ]

        job_data["education_score"] = result[
            "education_score"
        ]

        job_data["experience_score"] = result[
            "experience_score"
        ]
        
        job_data["recommendation_type"] = result[
            "recommendation_type"
        ]
        
        job_data["match_explanation"] = result.get(
            "match_explanation",
            ""
        )

        scored_jobs.append(
            job_data
        )

    scored_jobs.sort(
        key=lambda job: (
            -job.get("match_score", 0),
            -job.get("career_prediction_score", 0),
            -job.get("career_score", 0),
            -len(job.get("career_matches", [])),
            -job.get("skill_score", 0),
            -len(job.get("matched_skills", [])),
            (
                0
                if job.get("recommendation_type") == "Career + Skill Match"
                else (
                    1
                    if job.get("recommendation_type") == "Primary Career Match"
                    else (
                        2
                        if job.get("recommendation_type") == "Skill-Based Alternative"
                        else 3
                    )
                )
            ),
            -job.get("id", 0)
        ),
        reverse=False
    )

    return scored_jobs[:limit]


create_jobs_table()

