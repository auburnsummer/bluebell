# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
import dateparser
import datetime

class WorkshopPipeline(object):
    def process_item(self, item, spider):
        return item


class LastUpdatedPipeline(object):
    """
    A pipeline that gets the "Last Updated" parameter.
    We can't get this from the listing so we have to go to the page.
    """
    
    def make_workshop_url(self, id):
        return f"https://steamcommunity.com/sharedfiles/filedetails/?id={id}"
    
    def process_item(self, item, spider):
        request = scrapy.Request(url=self.make_workshop_url(item['id']))
        dfd = spider.crawler.engine.download(request, spider)
        dfd.addBoth(self.return_item, item)
        return dfd
        
    def return_item(self, response, item):
        if response.status != 200:
            return item
        date = response.xpath('//div[contains(@class, "detailsStatsContainerRight")]/div[last()]/text()').get()
        try:
            if date is not None:
                item['last_updated'] = dateparser.parse(date, ["%d %b, %Y @ %I:%M%p"])
            else:
                raise ValueError("No date found!") 
        except ValueError:
            # fallback: it was last updated today! (i.e. always refresh this one)
            item['last_updated'] = datetime.datetime.now()
        
        return item