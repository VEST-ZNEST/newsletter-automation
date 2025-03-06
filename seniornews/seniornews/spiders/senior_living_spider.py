import scrapy
from datetime import datetime, timedelta
from dateutil import parser
import pytz
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

    def __init__(self, start_date=None, end_date=None, *args, **kwargs):
        super(SeniorLivingNewsSpider, self).__init__(*args, **kwargs)
        from scrapy.utils.project import get_project_settings
        settings = get_project_settings()
        
        # Get date range from settings with defaults
        default_days = settings.get('DEFAULT_SCRAPE_DAYS', 30)  # Default to 30 days if not set
        
        # Priority for date parameters:
        # 1. Command line arguments (start_date/end_date)
        # 2. Settings.py START_DATE/END_DATE
        # 3. Default (now - default_days to now)
        
        # Handle start date
        if start_date:  # Command line argument
            try:
                self.start_date = datetime.strptime(start_date, '%Y-%m-%d')
                self.logger.info(f'Using command line start_date: {self.start_date}')
            except ValueError:
                self.logger.error(f'Invalid start_date format: {start_date}, using default')
                self.start_date = None
        else:
            self.start_date = None
            
        # If start_date not set via command line, check settings
        if self.start_date is None:
            settings_start_date = settings.get('START_DATE')
            if settings_start_date:
                if isinstance(settings_start_date, str):
                    try:
                        self.start_date = datetime.strptime(settings_start_date, '%Y-%m-%d')
                        self.logger.info(f'Using settings START_DATE: {self.start_date}')
                    except ValueError:
                        self.logger.error(f'Invalid settings START_DATE format: {settings_start_date}')
                        self.start_date = None
                else:
                    self.start_date = settings_start_date
                    self.logger.info(f'Using settings START_DATE object: {self.start_date}')
        
        # If still not set, use default
        if self.start_date is None:
            self.start_date = datetime.now() - timedelta(days=default_days)
            self.logger.info(f'Using default start_date (now - {default_days} days): {self.start_date}')
            
        # Handle end date with similar priority logic
        if end_date:  # Command line argument
            try:
                self.end_date = datetime.strptime(end_date, '%Y-%m-%d')
                self.logger.info(f'Using command line end_date: {self.end_date}')
            except ValueError:
                self.logger.error(f'Invalid end_date format: {end_date}, using default')
                self.end_date = None
        else:
            self.end_date = None
            
        # If end_date not set via command line, check settings
        if self.end_date is None:
            settings_end_date = settings.get('END_DATE')
            if settings_end_date:
                if isinstance(settings_end_date, str):
                    try:
                        self.end_date = datetime.strptime(settings_end_date, '%Y-%m-%d')
                        self.logger.info(f'Using settings END_DATE: {self.end_date}')
                    except ValueError:
                        self.logger.error(f'Invalid settings END_DATE format: {settings_end_date}')
                        self.end_date = None
                else:
                    self.end_date = settings_end_date
                    self.logger.info(f'Using settings END_DATE object: {self.end_date}')
        
        # If still not set, use default
        if self.end_date is None:
            self.end_date = datetime.now()
            self.logger.info(f'Using default end_date (now): {self.end_date}')
        
        # Ensure both dates have timezone info
        if self.start_date.tzinfo is None:
            self.start_date = self.start_date.replace(tzinfo=datetime.now().astimezone().tzinfo)
        if self.end_date.tzinfo is None:
            self.end_date = self.end_date.replace(tzinfo=datetime.now().astimezone().tzinfo)
            
        self.logger.info(f'Spider initialized with date range: {self.start_date} to {self.end_date}')
    
    def is_within_date_range(self, date_str):
        if not date_str:
            self.logger.debug(f'No date string provided')
            return False
        try:
            # Log the raw date string
            self.logger.info(f'Processing date string: {date_str}')
            
            # Try to parse the date string
            try:
                article_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except ValueError:
                # If ISO format fails, try parsing with dateutil
                article_date = parser.parse(date_str)
            
            # Convert article_date to the same timezone as start_date
            article_date = article_date.astimezone(self.start_date.tzinfo)
            
            # Log all the dates for comparison
            self.logger.info(f'Article date: {article_date}')
            self.logger.info(f'Start date: {self.start_date}')
            self.logger.info(f'End date: {self.end_date}')
            
            is_within = self.start_date <= article_date <= self.end_date
            self.logger.info(f'Is within range: {is_within}')
            
            return is_within
        except (ValueError, AttributeError) as e:
            self.logger.error(f'Error parsing date {date_str}: {str(e)}')
            return False

    def parse_article(self, response):
        try:
            item = SeniorNewsItem()
            
            # Extract data based on the website
            if 'seniorhousingnews.com' in response.url:
                item['title'] = response.css('h1.entry-title::text').get()
                item['author'] = response.css('span.author a::text').get()
                item['publication_date'] = response.css('time.entry-date::attr(datetime)').get()
                item['url'] = response.url
                item['content'] = ' '.join(response.css('div.entry-content p::text').getall())
            
            # McKnight's Senior Living
            elif 'mcknightsseniorliving.com' in response.url:
                item['title'] = response.css('h1::text').get()
                item['author'] = response.css('div.article-meta a::text').get()
                item['publication_date'] = response.css('time::attr(datetime)').get()
                item['url'] = response.url
                item['content'] = ' '.join(response.css('div.article-content p::text').getall())
            
            # Senior Living News
            elif 'seniorlivingnews.com' in response.url:
                item['title'] = response.css('h1::text').get()
                item['author'] = response.css('span.author::text').get()
                item['publication_date'] = response.css('span.date::text').get()
                item['url'] = response.url
                item['content'] = ' '.join(response.css('div.content p::text').getall())
            
            # Seniors Housing Business
            elif 'seniorshousingbusiness.com' in response.url:
                item['title'] = response.css('h1::text').get()
                item['author'] = response.css('div.author::text').get()
                item['publication_date'] = response.css('div.date::text').get()
                item['url'] = response.url
                item['content'] = ' '.join(response.css('div.article-body p::text').getall())
            
            # Log the extracted item data
            self.logger.info(f'Extracted item: {dict(item)}')
            
            # Check required fields
            has_title = bool(item.get('title'))
            has_url = bool(item.get('url'))
            has_date = bool(item.get('publication_date'))
            
            self.logger.info(f'Has title: {has_title}, Has URL: {has_url}, Has date: {has_date}')
            
            # Check date range
            if has_title and has_url and has_date:
                is_within_range = self.is_within_date_range(item['publication_date'])
                if is_within_range:
                    self.logger.info(f'Found recent article: {item["title"]} from {item["publication_date"]}')
                    yield item
                else:
                    self.logger.info(f'Skipping article outside date range: {item["title"]} from {item["publication_date"]}')
            else:
                self.logger.warning(f'Incomplete article data from {response.url}: Missing fields')
        
        except Exception as e:
            self.logger.error(f'Error parsing article {response.url}: {str(e)}')
