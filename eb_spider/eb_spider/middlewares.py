# -*- coding: utf-8 -*-
import random
from .useragents import agents
from .ip_pool import ip_queue
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware

class UserAgentmiddleware(UserAgentMiddleware):
    def process_request(self, request, spider):
        agent = random.choice(agents)        # 随机选取用户代理
        request.headers["User-Agent"] = agent   # 赋值到请求头

class ProxyMiddleware(object):
    def __init__(self):
        self.ip_lists = ip_queue("ips.txt")    # 读取存放代理IP的文件
        self.ip_pools = self.ip_lists.find_proxy()

    def process_request(self, request, spider):
        ip = random.choice(self.ip_pools)   # 随机选取IP
        print('***********当前使用的ip**************: ', ip)
        request.meta['proxy'] = 'http://{}'.format(ip)
