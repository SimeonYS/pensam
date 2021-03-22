import scrapy


class PensamItem(scrapy.Item):
    title = scrapy.Field()
    content = scrapy.Field()
    date = scrapy.Field()
    link = scrapy.Field()
