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
        # Use follow_all for batch processing of links
        if 'seniorhousingnews.com' in response.url:
            # Extract all article links at once
            article_links = response.css('article.post h2.entry-title a::attr(href)').getall()
            yield from response.follow_all(article_links, self.parse_article)

            # Handle pagination
            next_pages = response.css('a.next.page-numbers::attr(href)').getall()
            yield from response.follow_all(next_pages, self.parse)
        
        elif 'mcknightsseniorliving.com' in response.url:
            # Extract all article links at once
            article_links = response.css('div.article-preview h2 a::attr(href)').getall()
            yield from response.follow_all(article_links, self.parse_article)
            
            # Handle pagination
            next_pages = response.css('a.next::attr(href)').getall()
            yield from response.follow_all(next_pages, self.parse)
            
        elif 'seniorlivingnews.com' in response.url:
            # Extract all article links at once
            article_links = response.css('article h2 a::attr(href)').getall()
            yield from response.follow_all(article_links, self.parse_article)
            
        elif 'seniorshousingbusiness.com' in response.url:
            # Extract all article links at once
            article_links = response.css('div.article a::attr(href)').getall()
            yield from response.follow_all(article_links, self.parse_article)

    def __init__(self, *args, **kwargs):
        super(SeniorLivingNewsSpider, self).__init__(*args, **kwargs)
        from scrapy.utils.project import get_project_settings
        settings = get_project_settings()

        
        # Get date range from settings with defaults
        self.start_date = settings.get('START_DATE') or (datetime.now() - timedelta(days=7))
        self.end_date = settings.get('END_DATE') or datetime.now()
        
        # Ensure both dates have timezone info
        if self.start_date.tzinfo is None:
            self.start_date = self.start_date.replace(tzinfo=datetime.now().astimezone().tzinfo)
        if self.end_date.tzinfo is None:
            self.end_date = self.end_date.replace(tzinfo=datetime.now().astimezone().tzinfo)
            
        self.logger.info(f'Spider initialized with date range: {self.start_date} to {self.end_date}')
    
    def is_within_date_range(self, date_str):
        if not date_str:
            return False
        try:
            article_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            # Convert article_date to the same timezone as start_date
            article_date = article_date.astimezone(self.start_date.tzinfo)
            return self.start_date <= article_date <= self.end_date
        except (ValueError, AttributeError) as e:
            self.logger.error(f'Error parsing date {date_str}: {str(e)}')
            return False

    def parse_article(self, response):
        try:
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
            
            # Clean and validate the item
            if item.get('title') and item.get('url') and item.get('publication_date'):
                # Only yield the item if it's within the date range
                if self.is_within_date_range(item['publication_date']):
                    self.logger.info(f'Found recent article: {item["title"]} from {item["publication_date"]}')
                    yield item
                else:
                    self.logger.debug(f'Skipping old article: {item["title"]} from {item["publication_date"]}')
            else:
                self.logger.warning(f'Incomplete article data from {response.url}')
        
        except Exception as e:
            self.logger.error(f'Error parsing article {response.url}: {str(e)}')
