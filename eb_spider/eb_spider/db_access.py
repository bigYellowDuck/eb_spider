#!/usr/local/bin/python2.7
# encoding: utf-8
'''
Created on 2017年2月10日
用来建立可靠链接
@author: Cenbylin
'''
from pymongo import MongoClient
from items import Sort
import eb_config as cfg

class EbSpierDB:
    def __init__(self, host, port, dbname, authdb=None, username=None, password=None):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.authdb = authdb
        self.username = username
        self.password = password
        #建立链接
        self.client = MongoClient(host, port)
        if authdb:
            self.client[authdb].authenticate(username, password)
        
    def __get_client(self):
        '''
        :拿到数据库连接
        '''
        if self.client and self.client.is_primary:
            pass
        else:
            #重新建立链接
            self.client.close()
            self.client = MongoClient(self.host, self.port)
            if self.authdb:
                self.client[self.authdb].authenticate(self.username, self.password)
        return self.client

    def insert_sort_item(self, sort_item):
        client = self.__get_client()
        #数据库
        db = client[self.dbname]
        coll = db['sort']
        coll.insert(dict(sort_item))
    def insert_shop_item(self, shop_item):
        client = self.__get_client()
        #数据库
        db = client[self.dbname]
        #视频集合
        coll = db['shop']
        coll.insert(dict(shop_item))

    def insert_commodity_item(self, commodity_item):
        client = self.__get_client()
        #数据库
        db = client[self.dbname]
        #视频集合
        coll = db['commodity']
        coll.insert(dict(commodity_item))

    def insert_comment_item(self, comment_item):
        client = self.__get_client()
        #数据库
        db = client[self.dbname]
        #视频集合
        coll = db['comment']
        coll.insert(dict(comment_item))

if __name__ == '__main__':
    mongo_client = EbSpierDB(cfg.db_host, cfg.db_port, cfg.db_name)
    sort_item = Sort()
    print sort_item.__class__.__name__
    #sort_item.init_item(ObjectId(), "1", "分来1", ObjectId(), "http://www.baidu.com")
    #mongo_client.insert_sort_item(sort_item)
    