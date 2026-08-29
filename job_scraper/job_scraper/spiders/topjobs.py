import re

import scrapy


JS_URL_PATTERN = re.compile(
    r"openSizeWindow\('([^']+JobAdvertismentServlet[^']*)'"
)

JOB_CODE_PATTERN = re.compile(r"jc=(\d+)")

FA_CODE_PATTERN = re.compile(r"FA=([A-Z]+)")


class TopJobsSpider(scrapy.Spider):

    name = "topjobs"
    allowed_domains = ["topjobs.lk", "www.topjobs.lk"]

    base_url = "https://www.topjobs.lk"

    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
        },
    }

    max_category_pages = 14

    async def start(self):

        yield scrapy.Request(
            url=f"{self.base_url}/recentjobs.jsp",
            callback=self.parse_listing,
            meta={"crawl_categories": True},
            errback=self.skip_error,
        )

    def skip_error(self, failure):
        self.logger.warning("Request failed: %s", failure.request.url)

    def parse_listing(self, response):

        crawl_categories = response.meta.get(
            "crawl_categories", False
        )

        links = response.css("div.recent-job a")

        if not links:
            links = response.css("span.job-link a")

        seen_codes = set(
            code for code in response.meta.get("seen_codes", [])
        )

        self.logger.info(
            "%s -> found %d vacancy links",
            response.url,
            len(links),
        )

        for link in links:

            href = link.attrib.get("href", "")

            match = JS_URL_PATTERN.search(href)

            if not match:
                continue

            relative_url = match.group(1).replace("&amp;", "&")

            absolute_url = response.urljoin(relative_url)

            code_match = JOB_CODE_PATTERN.search(absolute_url)

            if not code_match:
                continue

            job_code = code_match.group(1)

            if job_code in seen_codes:
                continue

            seen_codes.add(job_code)

            title = " ".join(
                fragment.strip()
                for fragment in link.xpath("./text()").getall()
                if fragment.strip()
            )

            company = self._extract_company(link)

            category_label = self._extract_category(link)

            yield scrapy.Request(
                url=absolute_url,
                callback=self.parse_job_detail,
                cb_kwargs={
                    "job_id": job_code,
                    "title": title[:250],
                    "company": (company or "")[:200],
                    "category_label": (category_label or "")[:120],
                },
                dont_filter=True,
                priority=1,
            )

        # From the entry page only, fan out into individual
        # functional-area listing pages for wider coverage.
        if not crawl_categories:
            return

        crawled = 0

        for cat_link in response.css("div.category a"):

            if crawled >= self.max_category_pages:
                break

            href = cat_link.attrib.get("href", "")

            fa_match = FA_CODE_PATTERN.search(href)

            if not fa_match:
                continue

            fa_code = fa_match.group(1)

            crawled += 1

            fa_url = (
                f"{self.base_url}"
                f"/applicant/vacancybyfunctionalarea.jsp?FA={fa_code}"
            )

            yield scrapy.Request(
                url=fa_url,
                callback=self.parse_listing,
                meta={"crawl_categories": False},
                dont_filter=True,
            )

    def _extract_company(self, link):
        """
        Company appears in <h5> (hot-jobs layout) or in the
        title attribute / trailing text (recent-jobs layout).
        """

        company = link.css("h5::text").get()

        if not company:

            title_attr = link.attrib.get("title", "")

            if title_attr:
                company = title_attr.lstrip(" -").strip()

        if not company:

            trailing = link.xpath(
                "./following-sibling::text()"
            ).get()

            if trailing:
                company = trailing.replace("\xa0", " ").lstrip(" -").strip()

        return company

    def _extract_category(self, link):

        header_text = link.xpath(
            "preceding::div[contains(@class,'fa-header')][1]"
        ).xpath("string(.)").get()

        if not header_text:
            return ""

        cleaned = header_text.replace("\xa0", " ")

        cleaned = re.sub(
            r"\|?\s*show all\s*$",
            "",
            cleaned
        )

        return cleaned.strip().strip("|").strip()

    def parse_job_detail(
        self,
        response,
        job_id,
        title,
        company,
        category_label
    ):

        import json

        posted_date = None
        expiry_date = None
        location = "Sri Lanka"
        description = ""
        organization = company or None

        for script in response.css(
            "script[type='application/ld+json']"
        ):

            raw = script.css("::text").get()

            if not raw:
                continue

            try:
                data = json.loads(raw)
            except (ValueError, TypeError):
                continue

            if not isinstance(data, dict):
                continue

            if data.get("@type") != "JobPosting":
                continue

            raw_description = data.get("description") or ""

            description = re.sub(
                r"<[^>]+>",
                " ",
                str(raw_description)
            )

            description = re.sub(
                r"\s{2,}",
                "\n",
                description
            ).strip()[:6000]

            posted_date = data.get("datePosted")

            valid_through = data.get("validThrough")

            if valid_through:
                expiry_date = str(valid_through)[:10]

            org_obj = data.get("hiringOrganization")

            if isinstance(org_obj, dict) and org_obj.get("name"):
                organization = org_obj["name"].strip()

            location_objs = data.get("jobLocation")

            if isinstance(location_objs, list) and location_objs:

                address = (
                    location_objs[0]
                    .get("address", {})
                    .get("addressLocality")
                )

                if address:
                    location = f"{address}, Sri Lanka"

            break

        yield {
            "source": "topjobs",
            "job_id": int(job_id) if job_id.isdigit() else job_id,
            "title": title,
            "company": organization,
            "location": location,
            "category": category_label or None,
            "description": description,
            "education": None,
            "experience": None,
            "salary": None,
            "job_type": None,
            "url": response.url,
            "posted_date": posted_date,
            "expiry_date": expiry_date,
        }
