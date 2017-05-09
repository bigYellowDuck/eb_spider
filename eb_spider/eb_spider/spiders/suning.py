#!/usr/local/bin/python
# encoding: utf-8
'''
@author: Cenbylin
'''
import scrapy
import random
import re
import requests
import json
import eb_spider.eb_config as cfg
from bson import ObjectId
from scrapy import cmdline
from scrapy import Request
from eb_spider.items import Sort,Shop,Comment,Commodity
from eb_spider.scrapy_redis.spiders import RedisSpider

class SuningSpider(RedisSpider):
    name = "suning"
    allowed_domains = ["suning.com"]
    redis_key = 'sn:start_urls'
    #start_urls = ["http://as.suning.com/allsort.htm",]

    def parse(self, response):
        """
        目录爬取，下一层是商品列表
        :param response: 
        :return: 
        """
        """
        一级目录
        """
        for catalog_1 in response.xpath('//div[@id="goodListContent"]//dl'):
            obj_id_1 = ObjectId()
            aim = catalog_1.xpath("dt/a")
            sort_item = Sort()
            sort_item.init_item(obj_id_1,
                                cfg.PLATFORM_SUNING,
                                None,
                                "".join(aim.xpath("text()").extract()),
                                response.urljoin("".join(aim.xpath("@href").extract())))
            #返回存储
            yield sort_item
            """
            二级目录
            """
            for catalog_2 in catalog_1.xpath('dd//a'):
                sort_item = Sort()
                href = response.urljoin("".join(catalog_2.xpath("@href").extract()))
                obj_id_2 = ObjectId()
                sort_item.init_item(obj_id_2,
                                    cfg.PLATFORM_SUNING,
                                    obj_id_1,
                                    "".join(catalog_2.xpath("text()").extract()),
                                    href)
                # 返回存储
                yield sort_item
                # 进入下一层：商品列表
                yield Request(href, callback=self.list_parse, meta={'sort':obj_id_2})

    def list_parse(self, response):
        """
        列表爬取，下一层是详情
        :param response: 
        :return: 
        """
        for a in response.xpath('//div[@class="img-block"]//a'):
            # 进入下一层：商品详情
            yield Request(response.urljoin("".join(a.xpath("@href").extract()).strip()), callback=self.detail_parse, meta={'sort':response.meta['sort']})

        # 下一页
        currentPage_s = "".join(re.findall('param.currentPage = "(.*?)";', response.body))
        pageNum_s = "".join(re.findall('param.pageNumbers = "(.*?)";', response.body))
        if not (currentPage_s and pageNum_s):
            #没有下一页
            return
        # 1.当前页码（2表示第三页）
        currentPage = int(currentPage_s)
        # 2.总页数
        pageNum = int(pageNum_s)
        # 3.尝试进入下一页
        page_link = response.xpath('//a[@pagenum="' + str(currentPage + 2) + '"]/@href')
        if currentPage < pageNum - 1 and page_link and len(page_link)>0:
            next_url = response.urljoin("".join(page_link.extract()))
            yield Request(next_url, callback=self.list_parse)
        else:
            return

    def detail_parse(self, response):
        """
        详情爬取
        :param response: 
        :return: 
        """
        url = response.url
        name = "".join(re.findall(ur'"itemDisplayName":"(.*?)",', response.body))
        product_detail = "".join(response.xpath('//div[@id="productDetail"]').extract())
        # 为了获得商品价格
        pattern = 'https://pas.suning.com/nspcsale_0_%s_%s_%s_190_020_0200101_20089_1000041_9041_10274_Z001__.html'
        sort_and_id = "".join(re.findall('com/(.*?)\.html', url)).split("/")
        sort_id = sort_and_id[0]
        pro_id = sort_and_id[1]
        r = requests.get(url=pattern % (str(pro_id), str(pro_id), str(sort_id)))
        price = "".join(re.findall('netPrice":"(.*?)","warrantyList', r.text))
        # 存储
        commodity_item = Commodity()
        obj_id = ObjectId()
        commodity_item.init_item(_id = obj_id,
                                 platform = cfg.PLATFORM_SUNING,
                                 sort = response.meta['sort'],
                                 name = name,
                                 url = url,
                                 price= price,
                                 sale_num=0,
                                 comm_num=0,
                                 detail = product_detail)
        yield commodity_item
        # 评价
        pattern1 = 'https://review.suning.com/ajax/review_lists/general-%s-%s-total-1-default-10-----reviewList.htm'
        r = requests.get(url=pattern1 % (str(pro_id), str(sort_id)))
        comms_dict = json.loads(r.text[11:-1])
        # 拿到一些评论
        for comm_dict in comms_dict['commodityReviews']:
            comm = Comment()
            comm.init_item(_id=ObjectId(),
                           author_name=comm_dict['userInfo']['nickName'],
                           content=comm_dict['content'],
                           time=comm_dict['publishTime'],
                           commodity=obj_id)
            yield comm

if __name__ == '__main__':
    cmdline.execute(argv=['scrapy','crawl','suning'])
