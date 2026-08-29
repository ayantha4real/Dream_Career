import os
import sqlite3
from datetime import datetime, timezone

import sys

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
)

from app.services.text_cleaner import clean_html_text


class SQLiteJobPipeline:

    def open_spider(self, spider):

        base_dir = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                ".."
            )
        )

        database_folder = os.path.join(
            base_dir,
            "database"
        )

        os.makedirs(
            database_folder,
            exist_ok=True
        )

        self.database_path = os.path.join(
            database_folder,
            "dreamcareer.db"
        )

        self.connection = sqlite3.connect(
            self.database_path
        )

        self.cursor = self.connection.cursor()

    def process_item(self, item, spider):

        scraped_at = datetime.now(
            timezone.utc
        ).isoformat()

        if item.get("description"):
            item["description"] = clean_html_text(
                item["description"]
            )

        source = item.get("source")
        job_id = item.get("job_id")

        existing_id = None

        if source and job_id:
            self.cursor.execute(
                """
                SELECT id
                FROM jobs
                WHERE source = ?
                AND job_id = ?
                """,
                (
                    source,
                    job_id
                )
            )

            result = self.cursor.fetchone()

            if result:
                existing_id = result[0]

        if existing_id:

            self.cursor.execute(
                """
                UPDATE jobs
                SET
                    title = ?,
                    company = ?,
                    location = ?,
                    category = ?,
                    description = ?,
                    education = ?,
                    experience = ?,
                    salary = ?,
                    job_type = ?,
                    url = ?,
                    posted_date = ?,
                    expiry_date = ?,
                    scraped_at = ?
                WHERE id = ?
                """,
                (
                    item.get("title"),
                    item.get("company"),
                    item.get("location"),
                    item.get("category"),
                    item.get("description"),
                    item.get("education"),
                    item.get("experience"),
                    item.get("salary"),
                    item.get("job_type"),
                    item.get("url"),
                    item.get("posted_date"),
                    item.get("expiry_date"),
                    scraped_at,
                    existing_id
                )
            )

        else:

            self.cursor.execute(
                """
                INSERT INTO jobs (
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
                    job_id,
                    item.get("title"),
                    item.get("company"),
                    item.get("location"),
                    item.get("category"),
                    item.get("description"),
                    item.get("education"),
                    item.get("experience"),
                    item.get("salary"),
                    item.get("job_type"),
                    source,
                    item.get("url"),
                    item.get("posted_date"),
                    item.get("expiry_date"),
                    scraped_at
                )
            )

        self.connection.commit()

        return item

    def close_spider(self, spider):

        self.connection.close()