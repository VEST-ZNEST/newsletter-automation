# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


from datetime import datetime
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class SeniorNewsCleaningPipeline:
    """Pipeline for cleaning and validating senior news items."""
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Clean and validate title
        if not adapter.get('title'):
            raise DropItem(f'Missing title in {adapter.get("url")}')
        adapter['title'] = adapter['title'].strip()
        
        # Clean author
        if adapter.get('author'):
            adapter['author'] = adapter['author'].strip()
        else:
            adapter['author'] = 'Unknown'
        
        # Clean and validate publication date
        if adapter.get('publication_date'):
            try:
                # Convert to ISO format if not already
                date = datetime.fromisoformat(adapter['publication_date'].replace('Z', '+00:00'))
                adapter['publication_date'] = date.isoformat()
            except (ValueError, AttributeError):
                adapter['publication_date'] = None
        

        
        # Validate URL
        if not adapter.get('url'):
            raise DropItem('Missing URL')
        
        return item
