# -*- coding = utf-8 -*-
# 获取含有所需信息的帖子地址
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import math


# 读取含有股票代码的csv
def readCode(csv):
    df = pd.read_csv(csv)
    lst = list(df['code'])
    code_lst = []
    for ls in lst:
        ls = str(ls)
        ls = '0' * (6 - len(ls)) + ls
        code_lst.append(ls)
    return code_lst


# 得到股票列表页的上限值
def getPage(code):
    url = "http://guba.eastmoney.com/list,%s,f_1.html" % code
    data = get_data(url)
    soup = BeautifulSoup(data.text, 'lxml')
    step1 = soup.find_all('span', {'class': "pagernums"})
    string = str(step1)
    step2 = re.search('f_\|(.*?)\|', string).group(1)
    step3 = math.ceil(float(step2)/80)
    return step3


# 读取含有股票代码、列表页最大值的csv
def getCode(csv):
    df = pd.read_csv(csv)
    lst = list(df['code'])
    code_lst = []
    for ls in lst:
        ls = str(ls)
        ls = '0' * (6 - len(ls)) + ls
        code_lst.append(ls)
    page_lst = list(df['max'])
    page_start = list(df['start'])
    result = [code_lst, page_lst, page_start]
    return result


# 请求数据
def get_data(url):
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/68.0.3440.106 Safari/537.36"}
    data = requests.get(url, headers=headers)
    return data


# 解析列表页，获得帖子地址
def parse_date(data):
    soup = BeautifulSoup(data.text, 'lxml')
    urls = soup.find_all('div', {'class': "articleh normal_post"})
    url = []
    for u in urls:
        d = u.find('span', {'class': 'l3'})
        a = d.find('a')
        b = a.get("href")
        c = 'http://guba.eastmoney.com' + b
        url.append(c)
    return url


if __name__ == "__main__":
    # 第一步：读取csv，得到样本股的列表页上限值，结果存入csv
    csv = "wuran.csv"
    code_lst = readCode(csv)
    page_lst = []
    i = 1
    for code in code_lst:
        pagernums = getPage(code)
        page_lst.append(pagernums)
        print("正在处理第%d个股票" % i)
        i = i + 1
    union = {"code":code_lst,
             "maxpage":page_lst}
    df = pd.DataFrame(union)
    df.to_csv("wuran_step1.csv", index=False)

    # 第二步：读入含有列表页最大值的csv
    csv2 = "wuran_step1.csv.csv"
    result = getCode(csv2)
    length = len(result[0])

    # 第三步：解析列表页，获得帖子网址
    part1 = "http://guba.eastmoney.com/list,"
    part2 = ",f_"
    part3 = ".html"
    for i in range(0, length):
        code = result[0][i]
        maxpage = result[1][i]
        start = result[2][i]
        for j in range(1, maxpage + 1):
            url = part1 + code + part2 + str(j) + part3
            data = get_data(url)
            urls = parse_date(data)
            col1 = [code] * len(urls)
            col = {"code":col1,
                   "url":urls}
            df = pd.DataFrame(col)
            df.to_csv("wuran_url.csv", mode='a', header=False, index=False)
        print("已处理完成第%d个股票" % (i+1))
