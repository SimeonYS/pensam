import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import PensamItem
from itemloaders.processors import TakeFirst
import datetime
import json

pattern = r'(\xa0)?'
base = 'https://www.pensam.dk/api/sitecore/newslist/news?item_ID={{7392D8A5-12D3-4747-8F7D-0AAEC9F83B3B}}&category={}&offset=1&limit=20'

class PensamSpider(scrapy.Spider):
	name = 'pensam'
	now = datetime.datetime.now()
	year = now.year
	offset = 1
	start_urls = [base.format(year)]

	def parse(self, response):

		data = json.loads(response.text)
		for index in range(len(data['body'])):
			link = data['body'][index]['link']['href']
			date = data['body'][index]['date']
			yield response.follow(link, self.parse_post, cb_kwargs=dict(date=date))
		if data['total'] == 20:
			self.offset += 20
			next_page = f'https://www.pensam.dk/api/sitecore/newslist/news?item_ID={{7392D8A5-12D3-4747-8F7D-0AAEC9F83B3B}}&category={self.year}&offset={self.offset}&limit=20'
			yield response.follow(next_page, self.parse)
		if self.year >= 2016:
			self.year -= 1
			yield response.follow(base.format(self.year), self.parse)

	def parse_post(self, response, date):

		title = response.xpath('//h1/text()').get()
		content = response.xpath('//article[@class="mCOob2 _3Yh9ko _25C0oS"]//text() | //article[@class="_1SssDh _1DtnXr aLs3Nr"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=PensamItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
