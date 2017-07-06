# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field

class ZhihuAnswerItem(Item):
    title = Field()
    content = Field()
    author = Field()
    vote_count = Field()
    postdate = Field()
