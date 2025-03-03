import scrapy
from datetime import datetime, timedelta
from ..items import SeniorNewsItem

class SeniorLivingNewsSpider(scrapy.Spider):
    name = "senior_living_news"
    allowed_domains = ["seniorhousingnews.com", "seniorlivingnews.com", 
                      "seniorshousingbusiness.com", "mcknightsseniorliving.com", 
                      "argentum.org"]
    start_urls = [
        'https://www.seniorhousingnews.com/',
        'https://www.seniorlivingnews.com/',
        'https://seniorshousingbusiness.com/',
        'https://www.mcknightsseniorliving.com/',
        'https://www.argentum.org/argentummedia/argentum-e-newsletter/'
    ]

    def parse(self, response):
        # Extract links to articles from Senior Housing News
        if 'seniorhousingnews.com' in response.url:
            for article in response.css('article.post'):
                link = article.css('h2.entry-title a::attr(href)').get()
                if link:
                    yield response.follow(link, self.parse_article)

            # Follow pagination if available
            next_page = response.css('a.next.page-numbers::attr(href)').get()
            if next_page:
                yield response.follow(next_page, self.parse)
        
        # Add more website-specific parsing rules here
        elif 'mcknightsseniorliving.com' in response.url:
            for article in response.css('div.article-preview'):
                link = article.css('h2 a::attr(href)').get()
                if link:
                    yield response.follow(link, self.parse_article)

    def is_within_past_week(self, date_str):
        if not date_str:
            return False
        try:
            article_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            week_ago = datetime.now(article_date.tzinfo) - timedelta(days=7)
            return article_date >= week_ago
        except ValueError:
            return False

    def parse_article(self, response):
        item = SeniorNewsItem()
        
        # Senior Housing News
        if 'seniorhousingnews.com' in response.url:
            item['title'] = response.css('h1.entry-title::text').get()
            item['author'] = response.css('span.author a::text').get()
            item['publication_date'] = response.css('time.entry-date::attr(datetime)').get()
            item['url'] = response.url
        
        # McKnight's Senior Living
        elif 'mcknightsseniorliving.com' in response.url:
            item['title'] = response.css('h1::text').get()
            item['author'] = response.css('div.article-meta a::text').get()
            item['publication_date'] = response.css('time::attr(datetime)').get()
            item['url'] = response.url

            # Only yield the item if it's from the past week
            if self.is_within_past_week(item['publication_date']):
                yield item
