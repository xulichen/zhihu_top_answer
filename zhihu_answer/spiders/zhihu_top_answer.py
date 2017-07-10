# -*- coding: utf-8 -*-
import json
import re
import scrapy
from scrapy import FormRequest, Request
from lxml.html import etree
from zhihu_answer.items import ZhihuAnswerItem


class ZhihuTopAnswerSpider(scrapy.Spider):
    name = 'zhihu_top_answer'
    allowed_domains = ['www.zhihu.com']
    start_url = 'https://www.zhihu.com/topics'

    def start_requests(self):
        yield Request(url=self.start_url, callback=self.parse_first_index)

    def parse_first_index(self, response):
        # 筛选话题名
        topic_names = response.xpath('//li[@class="zm-topic-cat-item"]/a/@href').extract()
        # 筛选话题id
        topic_ids = response.xpath('//li[@class="zm-topic-cat-item"]/@data-id').extract()
        # 构造字典并通过meta将id传递至下一级
        topic_dict = dict(zip(topic_names, topic_ids))
        for topic_name in topic_names:
            yield Request(url=self.start_url+topic_name, callback=self.parse_second_index, meta={'topic_id': topic_dict.get(topic_name)}, dont_filter=True)

    def parse_second_index(self, response):
        # print(response.meta['topic_id'])
        Xsrftoken = re.findall('name="_xsrf" value="(.*?)"' ,response.text)
        offset = 0
        headers= {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'en',
                  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                                'Chrome/58.0.3029.110 Safari/537.36 ',
                  'X-Xsrftoken': Xsrftoken}
        while offset <= 100:
            params = '{"topic_id":' + str(response.meta['topic_id']) + ',"offset":' + str(offset) + ',"hash_id": ""}'
            yield FormRequest(url="https://www.zhihu.com/node/TopicsPlazzaListV2", formdata={'method': 'next', 'params': params}, callback=self.parse_third_index, headers=headers, dont_filter=True)
            offset += 20

    def parse_third_index(self, response):
        result = json.loads(response.text)
        for msg in result['msg']:
            source = etree.HTML(msg)
            href = source.xpath('/html/body/div/div/a[1]/@href')[0]
            url = 'https://www.zhihu.com' + href + '/top-answers?page=1'
            yield Request(url=url, callback=self.parse_answer)

    def parse_answer(self, response):
        vote_counts = response.xpath('//div[@id="zh-topic-top-page-list"]/div//div[@class="zm-item-vote-info"]/@data-votecount').extract()
        items = ZhihuAnswerItem()
        for i in range(len(vote_counts)):
            # 判断点赞数是否超过10k
            if int(vote_counts[i]) >= 10000:
                # 注意：由于range是从0开始， xpath是从1开始，所以 num = i + 1
                content = response.xpath('//div[@id="zh-topic-top-page-list"]/div[{num}]//textarea/text()'.format(num=i+1)).extract_first()
                author = response.xpath('//div[@id="zh-topic-top-page-list"]/div[{num}]//a[@class="author-link"]/text()'.format(num=i+1)).extract_first()
                title = response.xpath('//div[@id="zh-topic-top-page-list"]/div[{num}]//a[@class="question_link"]/text()'.format(num=i+1)).extract_first()
                postdate = response.xpath('//div[@id="zh-topic-top-page-list"]/div[{num}]//p/a/text()'.format(num=i+1)).extract_first()
                if title is not None:
                    title = title.strip()
                vote_count = vote_counts[i]
                items['content'] = content
                items['author'] = author
                items['title'] = title
                items['vote_count'] = vote_count
                items['postdate'] = postdate
                yield items
            else:
                return None

        if '=' in response.url:
            whole_url = response.url.split('=')
            main_url, url_page = whole_url[0], whole_url[1]
            yield Request(url=main_url + '=' + str(int(url_page)+1), callback=self.parse_answer)

