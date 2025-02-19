# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SeniorNewsItem(scrapy.Item):
    """Item class for senior living news articles.
    
    Fields:
        title: The title of the article
        author: The author of the article
        publication_date: When the article was published
        url: The source URL of the article
    """
    title = scrapy.Field()
    author = scrapy.Field()
    publication_date = scrapy.Field()
    url = scrapy.Field()
