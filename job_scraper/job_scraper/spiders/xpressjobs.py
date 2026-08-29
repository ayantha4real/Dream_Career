import scrapy
import json
from urllib.parse import urlencode


class XpressjobsSpider(scrapy.Spider):

    name = "xpressjobs"
    allowed_domains = ["xpress.jobs"]

    api_url = "https://xpress.jobs/api/jobs/searchJobs"
    detail_url = "https://xpress.jobs/api/jobs/publishedJob"

    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
    }

    async def start(self):

        for page in range(1, 6):

            params = {
                "page": page,
                "pageSize": 20,
                "keyword": "",
                "locations": "",
                "sectors": "",
                "jobTypes": "",
                "careerLevels": "",
                "sortBy": "SortedCreateDate DESC",
                "byCVLess": "False",
                "byWalkIn": "False",
            }

            url = f"{self.api_url}?{urlencode(params)}"

            self.logger.info(
                "Requesting XpressJobs page %s: %s",
                page,
                url
            )

            yield scrapy.Request(
                url=url,
                method="GET",
                callback=self.parse_jobs,
                meta={
                    "page": page
                }
            )

    def parse_jobs(self, response):

        page = response.meta.get(
            "page",
            1
        )

        self.logger.info(
            "XpressJobs API response status for page %s: %s",
            page,
            response.status
        )

        try:

            jobs = json.loads(
                response.text
            )

        except json.JSONDecodeError:

            self.logger.error(
                "Could not decode XpressJobs API response."
            )

            self.logger.error(
                "Response: %s",
                response.text[:1000]
            )

            return

        if not isinstance(jobs, list):

            self.logger.error(
                "Unexpected API response format on page %s",
                page
            )

            return

        self.logger.info(
            "Found %s jobs on page %s",
            len(jobs),
            page
        )

        for job in jobs:

            job_id = job.get(
                "jobId"
            )

            if not job_id:
                continue

            params = urlencode({
                "jobId": job_id
            })

            url = (
                f"{self.detail_url}?{params}"
            )

            yield scrapy.Request(
                url=url,
                method="GET",
                callback=self.parse_job_details,
                meta={
                    "job_summary": job
                }
            )

    def parse_job_details(self, response):

        self.logger.info(
            "Received details for: %s",
            response.url
        )

        try:

            data = json.loads(
                response.text
            )

        except json.JSONDecodeError:

            self.logger.error(
                "Could not decode job details response: %s",
                response.url
            )

            return

        job_summary = response.meta.get(
            "job_summary",
            {}
        )

        job_id = (
            data.get("jobId")
            or job_summary.get("jobId")
        )

        job_title = (
            data.get("jobTitle")
            or job_summary.get("jobTitle")
            or ""
        )

        organization = (
            data.get("organization")
            or {}
        )

        company = (
            organization.get(
                "organizationName"
            )
            or job_summary.get(
                "organizationName"
            )
            or ""
        )

        job_item = (
            data.get("jobItem")
            or {}
        )

        locations = (
            job_item.get("locations")
            or job_summary.get("locations")
            or ""
        )

        sectors = data.get(
            "sectors",
            []
        )

        category = ", ".join(
            sector.get(
                "sectorName",
                ""
            )
            for sector in sectors
            if sector.get(
                "sectorName"
            )
        )

        description = data.get(
            "jobInfo",
            ""
        )

        education = (
            data.get("education")
            or ""
        )

        experience = (
            data.get("experience")
            or ""
        )

        salary = (
            data.get("salaryRange")
            or ""
        )

        job_type = (
            job_item.get("jobType")
            or job_summary.get("jobType")
            or ""
        )

        expiry_date = (
            data.get("expiryDateOnWebsite")
            or job_summary.get("expiryDateOnWebsite")
            or ""
        )

        posted_date = (
            data.get("createdDate")
            or job_summary.get("createdDate")
            or ""
        )

        url = (
            f"https://xpress.jobs/jobs/view/"
            f"{job_id}/"
            f"{self.slugify(job_title)}"
        )

        yield {
            "job_id": job_id,
            "title": job_title,
            "company": company,
            "location": locations,
            "category": category,
            "description": description,
            "education": education,
            "experience": experience,
            "salary": salary,
            "job_type": job_type,
            "source": "XpressJobs",
            "url": url,
            "posted_date": posted_date,
            "expiry_date": expiry_date,
        }

    def slugify(self, text):

        import re

        text = text.lower()

        text = re.sub(
            r"[^a-z0-9]+",
            "-",
            text
        )

        text = text.strip(
            "-"
        )

        return text