# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class Sort(scrapy.Item):
    """
    "_id":主键，mongo分配uuid
	"platform":某个网站的标识，需要统一
	"name":分类名称
	"super_sort":父分类的_id，ObjectId类型。最顶则为null
	"url":地址（如果有）
    """
    _id = scrapy.Field()
    platform = scrapy.Field()
    name = scrapy.Field()
    super_sort = scrapy.Field()
    url = scrapy.Field()

    def init_item(self, _id, platform, super_sort, name, url):
        self['_id'] = _id
        self['platform'] = platform
        self['name'] = name
        self['super_sort'] = super_sort
        self['url'] = url

class Shop(scrapy.Item):
    """
    "_id":主键，mongo分配uuid
	"platform":某个网站的标识，需要统一
	"identity":店铺id或标识(在平台能确定一个店铺)
	"name":店铺名
	"url":地址
    """
    _id = scrapy.Field()
    platform = scrapy.Field()
    identity = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()

    def init_item(self, _id, platform, identity, name, url):
        self['_id'] = _id
        self['platform'] = platform
        self['identity'] = identity
        self['name'] = name
        self['url'] = url

class Commodity(scrapy.Item):
    """
    "_id":主键，mongo分配uuid
	"platform":某个网站的标识，需要统一
	"sort":分类的_id
	"name":商品名
	"url":商品地址
	"price":价格
	"sale_num":销售量
	"comm_num":评论数
	"detail":详情
    """
    _id = scrapy.Field()
    platform = scrapy.Field()
    sort = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    price = scrapy.Field()
    sale_num = scrapy.Field()
    comm_num = scrapy.Field()
    detail = scrapy.Field()

    def init_item(self, _id, platform, sort, name, url, price, sale_num, comm_num, detail):
        self['_id'] = _id
        self['platform'] = platform
        self['sort'] = sort
        self['name'] = name
        self['url'] = url
        self['price'] = price
        self['sale_num'] = sale_num
        self['comm_num'] = comm_num
        self['detail'] = detail

class Comment(scrapy.Item):
    """
    "_id":主键，mongo分配uuid
	"author_name"::评论者昵称
	"content":评论内容
	"time":评论时间
	"commodity":关联商品
    """
    _id = scrapy.Field()
    author_name = scrapy.Field()
    content = scrapy.Field()
    time = scrapy.Field()
    commodity = scrapy.Field()

    def init_item(self, _id, author_name, content, time, commodity):
        self['_id'] = _id
        self['author_name'] = author_name
        self['content'] = content
        self['time'] = time
        self['commodity'] = commodity

if __name__ == '__main__':
    """
    item使用规范
    """
    from bson import ObjectId
    sort_item = Sort()
    sort_item.init_item(ObjectId(), "1", "分来1", ObjectId(), "http://www.baidu.com")