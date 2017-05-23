#!/usr/local/bin/python
# encoding: utf-8
'''
Created on 2017年5月21日
@author: boliang
'''
import sys
from _cffi_backend import callback
if sys.getdefaultencoding() != 'gbk': 
    reload(sys) 
    sys.setdefaultencoding('gbk')
import scrapy
import random
import re
import requests
import json
import eb_spider.eb_config as cfg
from bson import ObjectId
from scrapy import cmdline
from scrapy import Request
from eb_spider.items import Sort,Comment,Commodity
from eb_spider.scrapy_redis.spiders import RedisSpider

class SpiderExecuteSpider(RedisSpider):
    name = "guomei"
    allowed_domains = ["gome.com.cn"]
    #start_urls = ["https://list.gome.com.cn/"]
    redis_key = 'gm:start_urls'

    def parse(self, response):
        """
                    目录爬取
        """
        for catalog_1 in response.xpath("//div[@class='item']"):
            catalog_id = ObjectId();
            sort_item = Sort();
            sort_item.init_item(catalog_id, 
                                cfg.PLATFORM_GUOMEI, 
                                None, 
                                "".join(catalog_1.xpath('h3/text()').extract()), 
                                None);
            # 返回一级目录储存
            yield sort_item;
            
            for catalog_2 in catalog_1.xpath("div[@class='item-bd']/div[@class='in']//a"):
                sort_item = Sort();
                catalog_id2 = ObjectId();
                href = response.urljoin( "".join(catalog_2.xpath("@href").extract()));
                name = "".join( catalog_2.xpath("text()").extract() );
                sort_item.init_item(catalog_id2, cfg.PLATFORM_GUOMEI, catalog_id, name, href);
                # 返回二级目录储存
                yield sort_item;
                # 进入商品列表爬取
    
                yield Request(url=href, 
                              callback=self.list_parse,  
                              meta={"sort":catalog_id2});
            
    
    def list_parse(self, response):
        '''
                    商品列表爬取
        '''
        for link_a in response.xpath("//p[@class='item-pic']/a"):
            href =  response.urljoin( "".join(link_a.xpath("@href").extract())); 
            yield Request(url=href,
                          callback=self.detail_parse,
                          meta={"sort":response.meta["sort"]});
        
        currentPage = "".join(re.findall("currentPage.*?:(.*?),", response.body));
        totalPage = "".join(re.findall("totalPage.*?:(.*?),", response.body));
         
        if not currentPage or not totalPage:
            return;
        currentPage = int(currentPage);
        totalPage = int(totalPage);
        if currentPage >= totalPage:
            return;
         
        href = response.url + "?page=" + str(currentPage + 1);
        yield Request(url=href,
                      callback=self.list_parse,
                      meta={"sort":response.meta["sort"]});
        
    
    
    def detail_parse(self, response):
        '''
                    具体商品爬取
        '''
        #商品的链接
        url = response.url;
        #商品的名字
        name = "".join( response.xpath("//div[@class='hgroup']/h1/text()").extract() );
      
        #抓包提取价格和评论数    
        pattern = "http://ss.gome.com.cn/item/v1/d/m/store/%s/%s/N/31010100/310101001/null/flag/item/allStores";
        recordId= "".join(re.findall("com.cn/(.*?).html", url)).split("-");
        if len(recordId) < 2:
            return;
        id_1 = recordId[0];
        id_2 = recordId[1];
        #抓取json数据包, 以便提取价格和评论数
        json_bag = requests.get(url=pattern % (str(id_1), str(id_2)));
        #获取价格
        price = "".join(re.findall('"salePrice":"(.*?)"', json_bag.text));
        #获取评论数
        comm_num = "".join(re.findall('"comments":(.*?)}', json_bag.text));
        #获取详情
        detail = "".join(response.xpath("//div[@class='guigecanshu']/text()").extract());
        #创建商品对象
        commodity_item = Commodity();
        current_id = ObjectId();
        commodity_item.init_item(_id = current_id, 
                                 platform = cfg.PLATFORM_GUOMEI, 
                                 sort = response.meta["sort"], 
                                 name = name, 
                                 url = url, 
                                 price = price, 
                                 sale_num = 0, 
                                 comm_num = comm_num, 
                                 detail = detail);
        
       
        yield commodity_item;
        
        #抓包获取评价
        pattern = "http://ss.gome.com.cn/item/v1/prdevajsonp/appraiseNew/%s/1/all/0/10/flag/appraise/all";
        #获取json包
        json_bag = requests.get(url=pattern % (str(id_1)));
        comm_dict = json.loads(json_bag.text[4:-1]);
        for record in comm_dict["evaList"]["Evalist"]:
            comment_item = Comment();
            current_id = ObjectId();
            if not "loginname" in record:
                continue;
            elif not "appraiseElSum" in record:
                continue;
            elif not "post_time" in record:
                continue;
            comment_item.init_item(current_id, 
                                   record["loginname"], 
                                   record["appraiseElSum"], 
                                   record["post_time"], 
                                   commodity_item["_id"]);
            yield comment_item;

    
    

    
    
    
    
    
    
    
    
    
    
