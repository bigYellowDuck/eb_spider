# -*- coding: utf-8 -*-
import scrapy
import re
import urllib2
import json
import eb_spider.eb_config as cfg
from bson import ObjectId
from scrapy import Request
from eb_spider.items import Sort, Shop, Comment, Commodity
from eb_spider.scrapy_redis.spiders import RedisSpider

class JingdongSpider(RedisSpider):
    name = "jingdong"
    allowed_domains = ["jd.com"]
    redis_key = 'jd:start_urls'
    # start_urls = ['https://www.jd.com/allSort.aspx']

    def parse(self, response):
        """
        目录爬取，下一层时商品列表
        :param response:
        :return:
        """
        """
        一级目录
        """
        for catalog_1 in response.xpath("//div[@class='items']//dl"):
            obj_id_1 = ObjectId()
            aim = catalog_1.xpath("dt/a")
            sort_item = Sort()
            sort_item.init_item(obj_id_1,
                                cfg.PLATFORM_JINGDONG,
                                None,
                                aim.xpath("text()").extract()[0],
                                "http:" + aim.xpath("@href").extract()[0])

            # 返回存储
            yield sort_item
            """
            二级目录
            """
            for catalog_2 in catalog_1.xpath("dd//a"):
                sort_item = Sort()
                href = "http:" + catalog_2.xpath("@href").extract()[0]
                obj_id_2 = ObjectId()
                sort_item.init_item(obj_id_2,
                                    cfg.PLATFORM_JINGDONG,
                                    obj_id_1,
                                    catalog_2.xpath("text()").extract()[0],
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
        for a in response.xpath("//div[@class='p-name']//a"):
            # 进入下一层:商品详情
            url_ = "http:"+a.xpath("@href").extract()[0]
            yield Request(url=url_, callback=self.detail_parse, meta={'sort':response.meta['sort']})
        
        # 尝试进入下一页
        nextPage = response.xpath("//a[@class='fp-next']/@href").extract()
        if len(nextPage) != 0:
            url_ = "http://list.jd.com" + nextPage[0]
            yield Request(url=url_, callback=self.list_parse)
        else:
            return

    def detail_parse(self, response):
        """
        详情爬取
        :param response:
        "return"
        """
        # 获取商品链接
        url_ = response.url
        # 获取商品标题
        #name_ = response.xpath("//li[@class='img-hover']/img/@alt").extract() 
        #if name_ is None:
        name_ = response.xpath("//title/text()").extract()[0]
        #else:
        #name_ = name_[0]
        # 获取商品ID
        pat = ".com/(.*?).html"
        jid_ = re.compile(pat).findall(response.url)[0]
        # 获取商品价格
        priceUrl = "https://p.3.cn/prices/mgets?callback=jQuery3034500&type=1&area=1_72_2799_0&pdtk=0GESY3kJiqpKtJZX86h79C7Gy8i1aDXMttLrLZn2qWd5NpvHJsTCHYF3pjWhRpLC&pduid=717198808&pdpin=&pdbp=0&skuIds=J_{jid}&source=item-pc"
        priceData = urllib2.urlopen(priceUrl.format(jid=jid_)).read().decode('utf-8', 'ignore')
        pricepat = '"p":"(.*?)"'
        price_ = re.compile(pricepat).findall(priceData)[0]
        # 获取评论数
        commentCountUrl = "https://club.jd.com/comment/productCommentSummaries.action?referenceIds={jid}";
        commentCountData = urllib2.urlopen(commentCountUrl.format(jid=jid_)).read().decode('gbk', 'ignore').encode('utf-8')
        commentCountpat = '"CommentCountStr":"(.*?)"'
        commCountpat = '"CommentCount":(.*?),'
        comm_num_ = re.compile(commentCountpat).findall(commentCountData)[0]
        #获取详细评论(先获取一页)
        k = 0
        commentDataUrl = "https://club.jd.com/productpage/p-{jid}-s-0-t-1-p-{k}.html"
        commentDataData = urllib2.urlopen(commentDataUrl.format(jid=jid_,k=k)).read().decode('gbk', 'ignore').encode('utf-8')
        comms_dict = json.loads(commentDataData)
        
        #commentDatapat = '"content":"(.*?)"'
        #commentData = re.compile(commentDatapat).findall(commentDataData)
        
        """
        获取所有评论方法
        cnt = int(comm_num_)
        L = []
        while k < (cnt/10):
            L_ = re.compile(commentDatapat).findall(commentDataData)
            L.extend(L_)
            k = k+1

        commentData = L
        """

        """ DEBUG 
        print url_
        print name_
        print price_
        print jid_
        print comm_num_
        for i in range(0, len(comms_dict['comments'])):
            print comms_dict['comments'][i]['id']
            print comms_dict['comments'][i]['content']
            print comms_dict['comments'][i]['creationTime']

        print '-----'
        """

        # 存储
        commodity_item = Commodity()
        obj_id = ObjectId()
        commodity_item.init_item(_id = obj_id,
                                platform = cfg.PLATFORM_JINGDONG,
                                sort = response.meta['sort'],
                                name  = name_,
                                url = url_,
                                price = price_,
                                sale_num = 0,
                                comm_num = comm_num_,
                                detail = None)
        yield commodity_item

        for i in range(0, len(comms_dict['comments'])):
            comm_item = Comment()
            comm_item.init_item(_id = ObjectId(),
                                author_name = comms_dict['comments'][i]['id'],
                                content = comms_dict['comments'][i]['content'],
                                time = comms_dict['comments'][i]['creationTime'],
                                commodity = obj_id)
            yield comm_item

