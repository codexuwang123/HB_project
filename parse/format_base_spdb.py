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
from settings import code_new

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
        'Accept-Encoding': 'gzip, deflate,utf-8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'sec-ch-ua': '"NotA;Brand";v="99","Chromium";v="99","GoogleChrome";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
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


# 特殊详情页解析
def detail_parse(url):
    uA = ua.get('user_agent')
    headers = {
        'User-Agent': random.choice(uA),
    }
    res = requests.get(url, headers=headers, verify=False)
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


# 详情页解析
def format_data(data, dict, dict_details):
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
def format_text(first_data, keyword, list_redis, section_name, author, ssin=None):
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
        dict['section_name'] = section_name
        dict['author_name'] = author

        list_redis.append(dict)


# 解析规则
def parse_html_to_str(htmlbody):
    # 去除页面中所有的 script 标签
    re_script = re.compile('<script[^>]*>[\s\S]*?<\/script>', re.I)
    re_style = re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I)  # 去除页面中的style 标签
    del_label = re.compile(r'<[^>]+>', re.S)  # 去除页面中所有的标签

    content_del = re_script.sub("", htmlbody)
    content_del = re_style.sub("", content_del)
    content_del = del_label.sub("", content_del)
    # 去除标签后 会出现很多的空格 或者 换行符 ，对其进行处理
    content_del = content_del.replace('\t', '').replace(' ', '')
    # 处理后发现 有很多的空行，按 换行符进行分割
    content_del = content_del.split('\n')
    content = ''
    # 处理空行
    for c in content_del:
        if c:
            content = content + c.strip() + '\n'
    # 去除所有空格
    new_1 = re.sub('\s+', '', content)
    # 循环删除特殊符号
    for i in code_new:
        new_1 = new_1.replace('{}'.format(i), '')
    return new_1


# 主要解析程序
def get_(number, new_keyword, new_tittle, details_data, true_url, dict):
    print('线程进来了================')
    if new_keyword in new_tittle:
        book_dict = {}
        new_dict = {}
        sql_server = save_data_to_sql.Save_score_to_sql()
        # 解析详情页数据
        book_dict['number'] = number
        book_dict['book_name'] = new_keyword
        book_dict['true_url'] = true_url
        book_html = parse_html_to_str(htmlbody=details_data)
        book_name = dict['keyword']
        book_author = dict['author_name']
        book_section = dict['section_name']
        book_dict['book_detail'] = book_html
        name_score = 0.0
        if book_name in book_html:
            name_score = name_score + 1.0
            new_dict['book_name_score'] = name_score
        else:
            new_dict['book_name_score'] = 0.0
        book_author_ = 0.0
        if book_author in book_html:
            book_author_ = book_author_ + 1.0
            new_dict['author_score'] = book_author_
        else:
            new_dict['author_score'] = 0.0

        section_list = book_section.split(';')
        sec_score = 0.0
        for sec in section_list:
            if sec in book_html:
                sec_score = sec_score + 0.2
        new_dict['section_score'] = sec_score
        new_dict['weight'] = name_score + book_author_ + sec_score
        # 详情整页数据存储
        sql_server.book_html_to_sql(data=book_dict)
        # 解析数据
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
            xmla_parse.smly_(data=details_data, dict=dict, dict_details=new_dict)
        elif 'https://dushu.baidu.com/' in true_url:
            print('进入百度链接了')
            parse_baidu.parse_b(url=true_url, dict=dict, dict_details=new_dict)
        elif '来书吧' in details_data:
            laishu8.lais(data=details_data, dict=dict, dict_details=new_dict)
        elif '阅书阁' in details_data:
            ysg_parse.parse_ysg(data=details_data, dict=dict, dict_details=new_dict)
        elif '全本小说网' in new_tittle:
            qbxsw_parse.qbxsw_parse(data=details_data, dict=dict, dict_details=new_dict)
        elif '蜻蜓FM' in new_tittle:
            qt_parse.qt_par(data=details_data, dict=dict, dict_details=new_dict)
        elif '<p id="summary">' in details_data:
            mq_parse.mq_par(data=details_data, dict=dict, dict_details=new_dict)
        elif '若夏' in new_tittle:
            rx_parse.rx_par(data=details_data, dict=dict, dict_details=new_dict)
        elif '七猫中文网' in new_tittle:
            for i in range(5):
                time.sleep(1)
                data2 = qmzhongwen_parse.get_acw_sc_v2(base_url=true_url)
                if '七猫中文网' in data2:
                    qmzhongwen_parse.qimao_parse(data=data2, dict=dict, dict_details=new_dict)
                    break
                else:
                    print('七猫没进去========')
                    continue
        elif 'https://www.soxs.cc/' in true_url:
            soxs_parse.soxs_par(data=details_data, dict=dict, dict_details=new_dict)
        elif 'www.xuanshu.com' in true_url:
            xuanshu_parse.quanshu(data=details_data, dict=dict, dict_details=new_dict)
        elif 'http://www.uuxsw' in true_url:
            uuxshuo_parse.uuxs_par(data=details_data, dict=dict, dict_details=new_dict)
        elif 'quanben' in true_url:
            qbxsw_parse.qbxsw_parse(data=details_data, dict=dict, dict_details=new_dict)
        else:
            format_data(data=details_data, dict=dict, dict_details=new_dict)
        # 数据库存放数据
        sql_server.search_data_to_sql(data=dict)
        sql_server.details_data_to_sql(data=dict)


    else:
        print('不符合跳过0000000000000000000000000000000000')
        print(new_tittle, '111111111111111111')
        print(true_url, '2222222222222222')
