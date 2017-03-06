import scrapy
from scrapy.spider import CrawlSpider, Rule
from scrapy.linkextractor import LinkExtractor


class MySpider(CrawlSpider):
    name = "mySpider"
    allowed_domains = ['uk.pearson.com']
    start_urls = ['https://uk.pearson.com']

    rules = (
        Rule(LinkExtractor(allow='\.html$', allow_domains=allowed_domains), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        self.logger.info('Hi, this is an item page! %s', response.url)
        url = response.url
        title = response.css("h1::text").extract_first()
        # image = response.css("img").extract_first()
        # if image is not None:
        #     image = image.xpath("@src")
        content = response.css("p::text").extract()
        section = response.css("h2::text,h2::text").extract()
        self.logger.info("The title is: %s", title)
        yield {
            'url': url,
            'title': title,
            'section': section,
            'type': '',
            # 'image': image,
            'content': content
        }
