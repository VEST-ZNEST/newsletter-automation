# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import scrapy


class SeniorLivingNewsSpider(scrapy.Spider):
    name = "senior_living_news"
    allowed_domains = ["https://seniorhousingnews.com/",
                       "https://www.seniorlivingnews.com/",
                       "https://seniorshousingbusiness.com/",
                       "https://www.mcknightsseniorliving.com/",
                       "https://www.argentum.org/argentummedia/argentum-e-newsletter/"]
    start_urls =["https://seniorhousingnews.com/",
                 "https://www.seniorlivingnews.com/",
                 "https://seniorshousingbusiness.com/",
                 "https://www.mcknightsseniorliving.com/",
                 "https://www.argentum.org/argentummedia/argentum-e-newsletter/"]

    def parse(self, response):
        # Extract links to articles
        for article in response.css('div.article-list'):
            link = article.css('a::attr(href)').get()
            if link:
                yield response.follow(link, self.parse_article)

        # Follow pagination if available
        next_page = response.css('a.next-page::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        yield {
            'title': response.css('h1.article-title::text').get(),
            'author': response.css('span.author-name::text').get(),
            'publication_date': response.css('time::attr(datetime)').get(),
            'content': ' '.join(response.css('div.article-content p::text').getall()),
            'url': response.url
        }
