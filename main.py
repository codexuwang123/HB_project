#!/usr/bin/python
# -*- coding:UTF-8 -*-
# 文件名:settings.py
# 创建日期:2022/3/10 10:19
# 作者:XU
# 联系邮箱:iswongx@163.com

import uuid
from multiprocessing.dummy import Pool as ThreadPool
import time
from to_sql import save_data_to_sql
from spider import Spider_data
from parse import format_base_spdb
from redis_client import redis_connect
from multiprocessing import Pool
import json

conn = redis_connect.Redis_connect()
# 实例化sql链接
s_data = save_data_to_sql.Save_score_to_sql()


# 主函数调用
# def last_mains():
#     # 数据库获取关键次列表
#     keyword_list = s_data.get_keyword()
#     if keyword_list:
#         i = ''
#         for i in keyword_list:
#             list_redis = []
#             dict_redis = {}
#             dict_redis['book_name'] = i.get('Search_Keyword')
#             for n in range(0, 20, 10):
#                 spider_self = Spider_data.Spider_desc(wd=i.get('Search_Keyword'))
#                 spider_self.spider(pn=n, keyword=spider_self.wd, list_redis=list_redis)
#             dict_redis['data'] = list_redis
#             dict_ = json.dumps(dict_redis)
#             conn.insert_data_redis(redis_key='baidus', values=dict_)
#         # 更新爬虫状态
#         s_data.undate_data(status_='1', keyword=i.get('Search_Keyword'))
#         # 关闭数据库连接
#         # s_data.close()
#         return keyword_list
#     else:
#         print('========温馨提示：没有有效关键词需要爬取=======')


# 总调用
def main_parse(dict):
    # print(i, '--------')
    print('线程进来了================')
    print(dict,'==========---')
    new_tittle = dict.get('tittle')
    new_url = dict.get('url')
    details_data, true_url = format_base_spdb.get_true(url=new_url)
    dict['true_url'] = true_url
    new_keyword = dict.get('keyword')
    number = str(uuid.uuid1()).replace('-', '')
    dict['number'] = number
    format_base_spdb.get_(new_keyword=new_keyword, new_tittle=new_tittle, details_data=details_data, true_url=true_url,dict=dict)


if __name__ == '__main__':


    while True:
        flag_data = conn.search_all_data(redis_key='baidus')
        print(flag_data,'''==============11111111111111''')
        time.sleep(3)
        print('等待新任务中========')
        # try:
        flags = len(flag_data)
        if flags == 0:
            continue
        else:
            dta = conn.search_data_redis(redis_key='baidus')
            dict = json.loads(dta)
            book_name = dict.get('book_name')
            data_book = dict.get('data')
            print(data_book,'000001111111111111111')
            # 最大任务数
            pool = ThreadPool(8)
            time3 = time.time()
            results = pool.map(main_parse, data_book)
            pool.close()
            pool.join()
            s_data.undate_data(status_='2', keyword=book_name)
        # except Exception as e:
        #     print(e, '=============')

