# Define here the models for your scraped items

from scrapy.item import Item, Field

class CrawlyItem(Item):
    url = Field()
    t_host = Field()
    t_country = Field()
    t_language = Field()
    t_language_alt = Field()
    s_host = Field()
    s_country = Field()
    s_language = Field()

