#!/usr/bin/python
# -*- coding:UTF-8 -*-
# 文件名:settings.py
# 创建日期:2022/3/10 10:18
# 作者:XU
# 联系邮箱:iswongx@163.com


import time
import logging
import re

# 爬虫程序请求头集合

ua = {
    'user_agent': [
        'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Mobile Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
        'Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/1A542a Safari/419.3',
        'Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:7.0a1) Gecko/20110623 Firefox/7.0a1 Fennec/7.0a1'
        'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_0 like Mac OS X; en-us) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.0.5 Mobile/8A293 Safari/6531.22.7',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0; HTC; Titan)',
        'Mozilla/5.0 (Linux; U; Android 8.1.0; zh-cn; BLA-AL00 Build/HUAWEIBLA-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/8.9 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; U; Android 8.0.0; zh-CN; MHA-AL00 Build/HUAWEIMHA-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.108 UCBrowser/12.1.4.994 Mobile Safari/537.36',
        'User-Agent,Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5',
        'User-Agent, MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1']
}

# 正式库地址
true_sql = {
    'host': '',
    'port': 3306,
    'user': '',
    'password': '',
    'db': ''
}
# 测试库地址
test_sql = {
    'host': 'rm-2ze7q160da69ezjdnxo.mysql.rds.aliyuncs.com',
    'port': 3306,
    'user': 'pythonr_eptile',
    'password': '1qaz@WSX#EDC',
    'db': 'pythonr_eptile'
}


# 设置日志函数
def set_log():
    now = int(time.time())
    timeArray = time.localtime(now)
    otherStyleTime = time.strftime("%Y%m%d", timeArray)
    logger2 = logging.getLogger('mylogger2')
    logger2.setLevel(logging.DEBUG)
    if not logger2.handlers:
        fh = logging.FileHandler('./log/{}.txt'.format(otherStyleTime), 'a', encoding='utf-8')
        formatter = logging.Formatter(
            '%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(process)d - %(message)s')
        fh.setFormatter(formatter)
        logger2.addHandler(fh)
    return logger2


# 基础配置

set_ = {
    'max_page': 200,  # 最大页数 200

}


# import  redis
# ip = '127.0.0.1'
# password = '123456'

# r2=redis.Redis(host=ip,password=password,port=6378,db=0,decode_responses=True)#decode_responses=True 自动解码，输出的结果自动由bytes类型变为字符串类型
# r1.set('name','2345')
# print(r1.get('name'))

# conn_pool = redis.ConnectionPool(host=ip,password=password, port=6379)
# r = redis.Redis(connection_pool=conn_pool)
# r.set('name','zhangsansan')
# # r.set('name','123456')
# print(r.get('name'))

# from redis import StrictRedis
from pickle import dumps, loads

# redis = StrictRedis(host='127.0.0.1', port=6379, db=0, password='123456')
# redis.set('name', 'wangxu')
# print(redis.get('name'))

# dict = {'name': '123456', 'url': 'www.baidu.com'}
# dict = {'name': '12345687', 'url': 'www.baidu.com888'}
# redis.rpush('data',dumps(dict))
# redis.rpush('data',dumps(dict))
# print(redis.lpop('data'))

#
import redis
# # #
job_redis  = redis.Redis(host='127.0.0.1', password='123456', port=6379, db=5,
                             decode_responses=True)  # redis默认连接db0
#
# # for i in range(20):
# #     url = 'www.baidu.com'+str(i)
# #     job_redis.sadd('datas',url)
#
# dict = {'12':'122','345':'67'}
# import json
# dict = json.dumps(dict)
# # 创建key 为 datas 数据集合
# job_redis.sadd('datas', dict)
# # # key 为datas 的所有集合

print(job_redis.smembers('360s'))
print(len(job_redis.smembers('360s')))

# # # 从集合中随机跳出一个 元素 返回并从集合中删除
# sc = job_redis.spop('datas')
# # # 判断指定value是否在本集合中，成功返回1,失败返回0
# # sc = job_redis.sismember('datas', dict)
# print(sc)



