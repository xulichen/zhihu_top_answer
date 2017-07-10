# zhihu_top_answer
抓取知乎上点赞数大于10k的回答

# 开发环境
python == 3.6.1

scrapy == 1.4.0 

MongoDB == 3.4.4

Redis == 3.2.9

## 利用scrapy抓取知乎广场各个话题下点赞数超过10k的答案，并保存到mongo数据库。
每个主话题下，提取前100的热门子话题

在子话题的精华 -- top_answer -- 下对各个回答进行筛选，抓取点赞数高于10k的回答
提取包括：title -- content  --  author  --  edit_time  等信息

## 增加了scrapy_redis分布式爬虫分支
