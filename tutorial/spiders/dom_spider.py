import scrapy
from collections import OrderedDict
from scrapy.spider import CrawlSpider, Rule
from scrapy.linkextractor import LinkExtractor
import re
from urlparse import urlparse


class DomSpider(CrawlSpider):
    name = "domSpider"
    allowed_domains = ['xx.example.com']
    start_urls = ['https://xx.example.com']

    rules = (
        Rule(LinkExtractor(allow='\.html$', allow_domains=allowed_domains), callback='parse_item', follow=True),
    )

    attributes = {}
    attributeMaxSizes = {}
    defaultAttributes = OrderedDict()

    defaultAttributes["title1"] = 'h1'
    defaultAttributes["title2"] = 'h2'
    defaultAttributes["title3"] = 'h3'
    defaultAttributes["title4"] = 'h4'
    defaultAttributes["title5"] = 'h5'
    defaultAttributes["title6"] = 'h6'
    defaultAttributes["content"] = 'p,a'

    parsedObjects = []

    currentObject = {}

    currentLevel = -1;

    sharedAttributes = {}

    def init(self):
        if not self.attributes:
            self.attributes = self.defaultAttributes

        self.currentLevel = -1
        self.parsedObjects = []
        self.currentObject = self.get_new_empty_object()

    def get_new_empty_object(self):
        obj = {}
        for attr in self.attributes:
            obj[attr] = ''
        return obj

    def parse_dom(self, response):
        self.init()

    def parse_node(self, response):
        self.init()
        global_selector = self.get_global_selectors()
        # self.log("==global selector is %s=" % global_selector)
        nodes = response.css(global_selector)
        for node in nodes:
            attribute_key = self.get_matching_attribute_key(node)
            # self.log("==attribute key is %s=" % attribute_key)
            level = self.get_attribute_level(attribute_key)
            # self.log("level is %s" % level)
            attribute_value = self.get_attribute_value(node)
            # self.log("attribute_value: %s" % attribute_value)
            # self.log("current object before %s" % self.currentObject)

            if not attribute_key:
                continue

            if level <= self.currentLevel:
                self.publish_current_object()
                self.prepare_current_object(level)

            self.currentObject[attribute_key] = attribute_value
            self.currentLevel = level
            # self.log("current object %s" % self.currentObject)
            # self.log("parsed object %s" % self.parsedObjects)
        self.publish_current_object()
        return self.parsedObjects

    def publish_current_object(self):
        final_obj = dict(self.sharedAttributes, **self.currentObject.copy())

        self.parsedObjects.append(final_obj)

    '''Prepare the cuurent object
    '''

    def prepare_current_object(self, level):
        new_object = self.get_new_empty_object()
        if level == 0:
            self.currentObject = new_object
            return
        counter = 0
        for key, value in self.attributes.iteritems():
            new_object[key] = self.currentObject[key]

            ++counter
            if counter == level:
                break

        self.currentObject = new_object

    '''combine all selectors into one big seletor in orderd.
    '''

    def get_global_selectors(self):
        selectors = self.attributes.values()
        return ",".join(selectors)

    def get_matching_attribute_key(self, node):
        self.log(node)
        tag = node.xpath("local-name()").extract_first()
        for attributes_key, selectors in self.attributes.iteritems():
            trimed_selectors = selectors.replace(" ", "")
            selector_list = trimed_selectors.split(",")
            if tag in selector_list:
                return attributes_key

        return None

    def get_attribute_value(self, node):
        value = node.xpath("./text()").extract_first()
        if value is None:
            return ""
        else:
            return value

    def get_attribute_level(self, key):
        keys = self.attributes.keys()
        # self.log("+++%s" % keys)
        if key not in keys:
            self.log("ERROR couldn't find key %s in the attributes" % key)
        return keys.index(key)

    # def split_attribute_value(self, attribute_key, attribute_value):

    # def start_requests(self):
    #     urls = [
    #         'https://uk.pearson.com/about-us.html'
    #     ]
    #     for url in urls:
    #         yield scrapy.Request(url=url, callback=self.parse)


    def parse_item(self, response):

        parsed_url = urlparse(response.url)
        domain = ""

        if parsed_url is not None:
            domain = parsed_url.scheme + '//' + parsed_url.netloc

        image = response.css("figure picture img").xpath('@srcset').extract_first()
        if image is None:
            image = ""
        else:
            image = domain + image

        self.sharedAttributes = {
            "post_title": response.css("h1::text").extract_first(),
            "url": response.url,
            "post_type": self.get_post_type(response),
            "thumbnail_url": image,
            "category": self.get_category(parsed_url)
        }

        yield {"page": response.url,
               "records": self.parse_node(response)}

    def get_post_type(self, response):
        url = response.url
        match = re.search('(blog|insight)\/\d\d\d\d', url)
        if match is not None:
            return "blog"
        match = re.search('/news/\d\d\d\d', url)
        if match is not None:
            return "news"
        return "general"

    def get_category(self, parsed_url):
        path = parsed_url.path
        matches = re.search('^/(.*?)/.*html', path)
        category = ""
        self.logger.info("matches: %s" % matches)
        if matches is not None and matches.lastindex >= 1:
            category = matches.group(1)

        return category
