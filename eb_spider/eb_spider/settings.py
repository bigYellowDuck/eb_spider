# -*- coding: utf-8 -*-

BOT_NAME = 'eb_spider'

SPIDER_MODULES = ['eb_spider.spiders']
NEWSPIDER_MODULE = 'eb_spider.spiders'

# 不遵守ROBOT协议
ROBOTSTXT_OBEY = False

# 使用自定义的scrapy_redis调度器
SCHEDULER = "eb_spider.scrapy_redis.scheduler.Scheduler"

SCHEDULER_PERSIST = True
SCHEDULER_QUEUE_CLASS = 'eb_spider.scrapy_redis.queue.SpiderPriorityQueue'
DUPEFILTER_CLASS = "eb_spider.scrapy_redis.dupefilter.RFPDupeFilter"

REDIS_URL = None

REDIS_HOST = '127.0.0.1'

REDIS_PORT = 6379

# 开启布隆过滤器过滤
FILTER = None
FILTER_HOST = '127.0.0.1'
FILTER_PORT = 6379
FILTER_DB = 0

# 关闭COOKIE
COOKIES_ENABLED = False

# 开启中间层代理
# userAgent为用户代理
# Proxy为IP代理，开启需在ips.txt中填充可用IP
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 543,    
    'eb_spider.middlewares.UserAgentmiddleware':400,
    #'eb_spider.middlewares.ProxyMiddleware':100, 
}

#开启PIPELINES
ITEM_PIPELINES = {
    'eb_spider.pipelines.EbSpiderPipeline': 300,
}

