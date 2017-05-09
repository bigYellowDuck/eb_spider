# eb_spider
使用Python2.7编写的一个分布式电商爬虫项目<br>
框架：scrapy(scrapy_redis)<br>
数据库:mongodb<br>

## 用法
爬取京东：<br>
scrapy crawl jingdong --nolog<br>
redis-cli lpush jd:start_urls https://www.jd.com/allSort.aspx<br>
<br>
爬取苏宁：<br>
scrapy crawl suning --nolog<br>
redis-cli lpush sn:start_urls http://as.suning.com/allsort.htm<br>

## 分布式支持
一台机器作为master端，源代码不用改变<br>
其余机器的作为slave，在settings.py进行如下修改<br>
```
REDIS_HOST = 'xxx.xxx.xxx.xxx'  # 改为master端机器的IP
```

所有机器的启动命令都是scrapy crawl xx --nolog<br>
master端的redis作为爬虫队列<br>
因此master端 输入 redis-cli lpush xx:start_urls https://........<br>
<br>
因为scrapy_redis修改过，所以默认的过滤器为布隆过滤器<br>
如需关闭需要把settings.py里的`FILTER`开头的4行删除或注释<br>
