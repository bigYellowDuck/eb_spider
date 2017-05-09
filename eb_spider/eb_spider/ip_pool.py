# -*- coding: utf-8 -*-

class ip_queue():
    def __init__(self, filename):
        self.filename = filename

    def find_proxy(self):
        proxy_list = []  # 用来接受从文件里找到的所有代理，返回包含代理的列表
        f = open(self.filename, 'r')  # 只读方式打开
        
        while 1:
            ip = f.readline()
            if not ip:
                break
            ip = ip.strip('\n')
            proxy_list.append(ip)

        f.close()

        return proxy_list
