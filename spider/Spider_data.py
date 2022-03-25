#!/usr/bin/python
# -*- coding:UTF-8 -*-
# 文件名:Spider_data.py
# 创建日期:2022/3/10 10:23
# 作者:XU
# 联系邮箱:iswongx@163.com

import requests
import re
from parse import format_base_spdb
from settings import set_log
import random

list = []
logging_ = set_log()

from settings import ua


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
    def spider(self, pn, keyword):
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
            data = re.findall('data-tools=.*?(\{.*?\})', res.text)
            format_base_spdb.format_text(first_data=data, keyword=keyword, ssin=self.ssin)
