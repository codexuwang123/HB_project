#!/usr/bin/python
# -*- coding:UTF-8 -*-
# 文件名:Spider_data.py
# 创建日期:2022/3/10 10:23
# 作者:XU
# 联系邮箱:iswongx@163.com

import requests
import re
from parse import format_base_spdb
from settings import main_set_log
import random
import time
from to_sql import save_data_to_sql

from parse import format_base_spdb
from redis_client import redis_connect
import logging
import json

conn = redis_connect.Redis_connect()
# 实例化sql链接
s_data = save_data_to_sql.Save_score_to_sql()

list = []

from settings import ua


# 设置日志函数
def set_log():
    now = int(time.time())
    timeArray = time.localtime(now)
    otherStyleTime = time.strftime("%Y%m%d", timeArray)
    logger2 = logging.getLogger('mylogger2')
    logger2.setLevel(logging.DEBUG)
    if not logger2.handlers:
        fh = logging.FileHandler('../log/{}.txt'.format(otherStyleTime), 'a', encoding='utf-8')
        formatter = logging.Formatter(
            '%(asctime)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - %(process)d - %(message)s')
        fh.setFormatter(formatter)
        logger2.addHandler(fh)
    return logger2


# 主要爬虫方法
class Spider_desc():

    # 基本请求头配置
    def __init__(self, wd):
        self.uA = ua.get('user_agent')
        self.wd = wd
        logging_.info('搜索引擎百度，正在爬取={}相关内容。'.format(self.wd))
        self.url = 'https://www.baidu.com/s?'
        self.headers = {
            'Host': 'www.baidu.com',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': random.choice(self.uA)
        }

    # 解析主函数
    def spider(self, pn, keyword, list_redis):
        params = {
            'wd': self.wd,
            'pn': pn,
            'oq': self.wd,
            'tn': 'baiduhome_pg',
            'ie': 'utf-8',
            'usm': '1',
            'rsv_idx': '2',
            'rsv_pq': 'b161436a0002d6b1',
            'rsv_t': '6085O2ISriAmrAq2E7OHkCO9Yoo2ZzW%2Bd7BC5z177LG9H8MAhPaEcT6V%2Bk4Rky377JQX'
        }
        self.ssin = requests.session()

        res = self.ssin.get(self.url, headers=self.headers, params=params)
        if res.status_code == 200:
            # print(res.text,'7777777777')
            time.sleep(2)
            data = re.findall('data-tools=.*?(\{.*?\})', res.text, re.S)
            format_base_spdb.format_text(first_data=data, keyword=keyword, ssin=self.ssin, list_redis=list_redis)


# 主函数调用
def last_mains():
    # 数据库获取关键次列表
    keyword_list = s_data.get_keyword()
    print(keyword_list)
    if keyword_list:
        for i in keyword_list:
            list_redis = []
            dict_redis = {}
            dict_redis['book_name'] = i.get('Search_Keyword')
            print(dict_redis)
            for n in range(0, 20, 10):
                spider_self = Spider_desc(wd=i.get('Search_Keyword'))
                spider_self.spider(pn=n, keyword=spider_self.wd, list_redis=list_redis)
            dict_redis['data'] = list_redis
            dict_ = json.dumps(dict_redis, ensure_ascii=False)
            print(dict_)
            conn.insert_data_redis(redis_key='baidus', values=dict_)
            print('redis 数据存放成功')
            # 更新爬虫状态
            s_data.undate_data(status_='1', keyword=i.get('Search_Keyword'))
    else:
        print('========温馨提示：没有有效关键词需要爬取=======')


if __name__ == '__main__':
    logging_ = set_log()
    # 存入将多任务 存入redis
    while True:
        last_mains()
        time.sleep(3)
