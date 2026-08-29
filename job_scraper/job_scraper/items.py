import scrapy


class JobItem(scrapy.Item):

    job_id = scrapy.Field()

    title = scrapy.Field()
    company = scrapy.Field()
    location = scrapy.Field()

    category = scrapy.Field()
    description = scrapy.Field()

    education = scrapy.Field()
    experience = scrapy.Field()
    salary = scrapy.Field()
    job_type = scrapy.Field()

    source = scrapy.Field()
    url = scrapy.Field()

    posted_date = scrapy.Field()
    expiry_date = scrapy.Field()

    scraped_at = scrapy.Field()