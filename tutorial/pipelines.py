# -*- coding: utf-8 -*-
import json


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class TutorialPipeline(object):
    # def process_item(self, item, spider):
    #     return item

    def open_spider(self, spider):
        self.file = open('new_items.json', 'wb')
        self.file.write("[\n")

    def close_spider(self, spider):
        self.file.write("\n]")
        self.file.close()

    def process_item(self, item, spider):
        # page = item["page"]
        # self.log("pipeline page: %s" % page)
        records = item.get("records", [])

        for record in records:
            # self.log("pipeline record: %s" % record)
            line = json.dumps(dict(record)) + ",\n"
            self.file.write(line)
        return item
