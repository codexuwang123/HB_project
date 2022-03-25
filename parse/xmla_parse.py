#!/usr/bin/python
# -*- coding:UTF-8 -*-
# 文件名:xmla_parse.py
# 创建日期:2022/3/12 17:48
# 作者:XU
# 联系邮箱:iswongx@163.com

import re
import json

# 喜马拉雅解析
def smly_(data,dict):
    dict_details = {}
    new_data = re.findall(r'"tdkMeta":(.*?\})\}',data)
    description = re.findall('"richIntro":"(.*?)"shortIntro"',data,re.S)
    if description:
        dict_details['describe'] = description[0].replace('\\u003cbr','').replace('/\\u003e','').replace('"','')
    else:
        dict_details['describe'] = ''
    if new_data:
        new_xmly = new_data[0]
        new_xmly_ = json.loads(new_xmly)
        dict_details['tittle'] = new_xmly_.get('title')
    dict['details'] = dict_details
    return dict
