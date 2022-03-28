#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 文件名: format_base_spdb.py
# 作者:WangXu
# 联系邮箱:iswongx@163.com

# 格式化基本信息
import random
import re

import requests

from . import xmla_parse
from . import parse_baidu
from . import ysg_parse
from . import qbxsw_parse
from . import mq_parse
from . import rx_parse
from . import qt_parse
from . import soxs_parse
from . import xuanshu_parse
from . import uuxshuo_parse
import time
from to_sql import save_data_to_sql
from settings import ua
from . import laishu8
from . import qmzhongwen_parse
from redis_client import redis_connect
import json
import urllib3

conn = redis_connect.Redis_connect()
import logging
# 忽略证书警告
urllib3.disable_warnings()



def main_set_logs():
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

# 获取真实页面方法
def get_true(url, ssin=None):
    uA = ua.get('user_agent')
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate',
        'If-None-Natch': '',
        'If-Modified-Since': '',
        'User-Agent': random.choice(uA),
    }
    print('=============================当前正在进入：{}  ===================================='.format(url))
    try:
        res = requests.get(url, headers=headers, timeout=20, verify=False)
        time.sleep(0.5)
        if res.status_code == 200:
            info = res.text
            char = re.findall('charset="{0,1}(.*?)"', info, re.S)
            if char:
                try:
                    info1 = res.content.decode(encoding='{}'.format(char[0].lower()))
                    return info1, res.url
                except Exception as e:
                    print(e, '异常编码了================')
                    return info, res.url
            else:
                # logging_1.info('编码异常-连接为{}，'.format(res.url))

                return '编码异常', res.url
        else:
            print('状态码异常返回数据', res.text)
            # logging_1.info('状态码/服务异常-被访问链接为{}，'.format(res.url))
            return '服务异常', res.url
    except Exception as e:
        print(e, '异常')
        # logging_1.info('特殊异常{}，异常连接{}'.format(e, url))
        return '超时', url


# 详情页解析
def format_data(data, dict):
    dict_details = {}
    author = ''
    # 作者名称
    author2 = re.findall('<meta property="og:novel:author" content="(.*?)"', data)
    if author2:
        author = author2[0]
        dict_details['author'] = author
    else:
        dict_details['author'] = author

    # 主角(默认为空)
    protagonist = ''
    if '主角' in data:
        protagonist = re.findall('主角：(.*?)<', data)
        if protagonist:
            dict_details['protagonist'] = protagonist[0]
        else:
            dict_details['protagonist'] = ''
    else:
        dict_details['protagonist'] = protagonist
    # 小说简介
    describe = re.findall('<meta property="og:description" content="(.*?)"', data, re.S)
    if describe:
        string = re.sub('&#\d+;', '', describe[0])
        dict_details['describe'] = string.replace('<br />\n', '').replace('<br />', '').replace('&ldquo;', '').replace(
            '&rdquo;', '').replace('&nbsp;', '').replace('&hellip;', '')
    else:
        dict_details['describe'] = ''
    # 章节标题
    tittle = ''
    # 默认为空
    dict_details['tittle'] = tittle
    dict['details'] = dict_details


# 首页数据解析
def format_text(first_data, keyword, list_redis,ssin=None):
    # sql_server.undate_data(status_='1', keyword=keyword)
    # print(first_data,'00000000000000000000000000')
    for i in first_data:

        dict = {}
        # 搜索内容标题
        new_data = i.replace('&quot;', '').replace('&#39;', '').replace('\n', '')
        new_data_ = re.sub(r'\\u\d+', '', new_data)
        # print(new_data_, '================')
        # 更进一步解析获取的脏数据
        tittle = re.findall('title.*?:(.*?)url', new_data_, re.S)[0].strip()
        url = re.findall('url.*?:(.*?)\}', new_data_, re.S)[0]
        if ',' in url:
            url = re.findall('url.*?:(.*?),', new_data_, re.S)[0]
        else:
            url = re.findall('url.*?:(.*?)\}', new_data_, re.S)[0]
        new_url = url.replace('"', '').replace("'", '')

        dict['tittle'] = tittle.replace('"', '').replace("'", '')
        # 跳转链接
        dict['url'] = new_url
        # 真实链接
        dict['true_url'] = ''
        dict['keyword'] = keyword
        # new_keyword = keyword.replace(':', '').replace('：', '')
        # new_tittle = tittle.replace(':', '').replace('：', '')

        list_redis.append(dict)


# 主要解析程序
def get_(new_keyword,new_tittle,details_data,true_url,dict):
    print('线程进来了================')
    list = []
    # dta = conn.search_data_redis(redis_key='baidus')
    # dict = json.loads(dta)
    #
    # new_tittle = dict.get('tittle')
    # new_url = dict.get('url')
    # details_data, true_url = get_true(url=new_url)
    # dict['true_url'] = true_url
    # new_keyword = dict.get('keyword')
    if new_keyword in new_tittle:
        if details_data == '编码异常':
            print('编码异常====', true_url)
            return None
        if details_data == '超时':
            print('超时了------------------', true_url)
            return None
        if details_data == '服务异常':
            print('服务异常=================', true_url)
            return None
        if '喜马拉雅' in details_data:
            xmla_parse.smly_(data=details_data, dict=dict)
        elif 'https://dushu.baidu.com/' in true_url:
            print('进入百度链接了')
            parse_baidu.parse_b(url=true_url, dict=dict)
        elif '来书吧' in details_data:
            laishu8.lais(data=details_data, dict=dict)
        elif '阅书阁' in details_data:
            ysg_parse.parse_ysg(data=details_data, dict=dict)
        elif '全本小说网' in new_tittle:
            qbxsw_parse.qbxsw_parse(data=details_data, dict=dict)
        elif '蜻蜓FM' in new_tittle:
            qt_parse.qt_par(data=details_data, dict=dict)
        elif '<p id="summary">' in details_data:
            mq_parse.mq_par(data=details_data, dict=dict)
        elif '若夏' in new_tittle:
            rx_parse.rx_par(data=details_data, dict=dict)
        elif '七猫中文网' in new_tittle:
            for i in range(5):
                time.sleep(1)
                data2 = qmzhongwen_parse.get_acw_sc_v2(base_url=true_url)
                if '七猫中文网' in data2:
                    qmzhongwen_parse.qimao_parse(data=data2, dict=dict)
                    break
                else:
                    print('七猫没进去========')
                    continue
        elif 'https://www.soxs.cc/' in true_url:
            soxs_parse.soxs_par(data=details_data, dict=dict)
        elif 'www.xuanshu.com' in true_url:
            xuanshu_parse.quanshu(data=details_data, dict=dict)
        elif 'http://www.uuxsw' in true_url:
            uuxshuo_parse.uuxs_par(data=details_data, dict=dict)
        elif 'quanben' in true_url:
            qbxsw_parse.qbxsw_parse(data=details_data, dict=dict)
        else:
            format_data(data=details_data, dict=dict)
        # 数据库存放数据
        sql_server = save_data_to_sql.Save_score_to_sql()
        sql_server.search_data_to_sql(data=dict)
        sql_server.details_data_to_sql(data=dict)
        list.append(dict)
        # print(dict)
    else:
        print('不符合跳过0000000000000000000000000000000000')
        print(new_tittle, '111111111111111111')
        print(true_url, '2222222222222222')
