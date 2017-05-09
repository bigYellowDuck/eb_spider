# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from db_access import EbSpierDB
import eb_config as cfg
#数据库链接
mongo_client = EbSpierDB(cfg.db_host, cfg.db_port, cfg.db_name)

class EbSpiderPipeline(object):

    def process_item(self, item, spider):
        # 接口字典
        switcher = {
            "Sort": mongo_client.insert_sort_item,
            "Shop": mongo_client.insert_shop_item,
            "Commodity": mongo_client.insert_commodity_item,
            "Comment": mongo_client.insert_comment_item
            # blablabla多个集合....
        }
        # 匹配对应集合的存储方法
        def __no_support_item():
            pass
        fun = switcher.get(item.__class__.__name__, __no_support_item)
        # 存储
        fun(item)
        return item
