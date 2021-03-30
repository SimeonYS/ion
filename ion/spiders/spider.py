import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import IonItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class IonSpider(scrapy.Spider):
	name = 'ion'
	start_urls = ['https://ionbank.com/about-us/news-and-happenings/']

	def parse(self, response):
		post_links = response.xpath('//h2/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//div[@class="pagination"]/a[text()="Next ›"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		date = response.xpath('//time/@datetime').get()
		title = response.xpath('//h2/text()').get()
		content = response.xpath('//div[@class="entry clr boxed"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=IonItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
