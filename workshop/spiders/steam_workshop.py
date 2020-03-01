import scrapy

class WorkshopListingSpider(scrapy.Spider):
    name = "WorkshopListing"
    
    def start_requests(self):
        game_id = getattr(self, 'game_id', None)
        
        urls = [
            f"https://steamcommunity.com/workshop/browse/?appid={game_id}&browsesort=mostrecent&section=readytouseitems&actualsort=mostrecent&p=1"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
            
    def parse(self, response):
        ids = response.xpath("//div[contains(@class, 'workshopItemPreviewHolder')]/parent::*/@data-publishedfileid").getall()
        for id in ids:
            yield {
                'id' : id,
                'game_id' : getattr(self, 'game_id', None)
            }
        
        next_page = response.xpath('//div[normalize-space(@class)="workshopBrowsePagingControls"]/a/@href').getall()
        # get last item
        for page in next_page:
            yield scrapy.Request(url=page, callback=self.parse)