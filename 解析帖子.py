# -*- coding = utf-8 -*-
# 从给定网址获取指定字段
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time


# 读取含有网址的csv
def readUrl(csv):
    df = pd.read_csv(csv)
    lst = list(df['code'])
    code_lst = []
    for ls in lst:
        ls = str(ls)
        ls = '0' * (6 - len(ls)) + ls
        code_lst.append(ls)
    urls = list(df['url'])
    result = [code_lst, urls]
    return result


# 抓取整个网页信息
def get_data(url):
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/68.0.3440.106 Safari/537.36"}
    data = requests.get(url, headers=headers)
    return data


# 从整个网页信息中提取所需字段
# 设置flag，判断是否在所需时间区间；异常处理，当帖子不存在时跳过不处理
# title:帖子标题，time:发帖时间，content:帖子内容
# click_count:点击量，like_count：点赞量，comment_count：评论量，forward_count：转发量
# comment：评论, c_time：评论的时间
def parse_data(data):
    soup = BeautifulSoup(data.text, 'lxml')

    title = soup.find('div', {'id': 'zwconttbt'}).get_text()
    title = title.replace('\n', '').replace(' ', '').replace('\r', '')

    time = soup.find('div', {'class': 'zwfbtime'}).get_text()
    time = re.findall('发表于 (.{19})', str(time))[0]
    timeArray = time[0:10]
    flag = 0
    if timeArray >= "2018-01-13":
        flag = 1

    content = soup.find('div', {'class': 'stockcodec .xeditor'}).get_text()
    content = content.replace('\n', '').replace(' ', '').replace('\r', '')

    # 可使用正则表达式查找post_click_count
    click_count = re.findall(r'"post_click_count":(.*?),', data.text)[0]
    like_count = re.findall(r'"post_like_count":(.*?),', data.text)[0]
    comment_count = re.findall(r'"post_comment_count":(.*?),', data.text)[0]
    forward_count = re.findall(r'"post_forward_count":(.*?),', data.text)[0]

    # 提取评论内容和时间
    comment = []
    c_time = []

    if comment_count:
        comments = soup.find_all('div', {'class': 'zwlitext'})
        for c in comments:
            a = c.find('div', {'class': 'short_text'})
            con = a.get_text()
            con = con.replace('\n', '').replace(' ', '').replace('\r', '')
            comment.append(con)

        c_times = soup.find_all('div', {'class': 'zwlitime'})
        for c in c_times:
            con = c.get_text()
            con = con.replace('\n', '').replace(' ', '').replace('\r', '')
            con = con[3:]
            c_time.append(con)

    return title, time, content, click_count, like_count, comment_count,\
           forward_count, comment, c_time, flag


# 存储数据
def saveData(title, time, content, click_count, like_count, comment_count,
             forward_count, comment, c_time, flag, code):
    l = max(1, len(comment))
    if len(comment) == 0:
        comment = ["None"]
        c_time = ["None"]
    dict = {"title": [title] * l,
            "time": [time] * l,
            "content": [content] * l,
            "click_count": [click_count] * l,
            "like_count": [like_count] * l,
            "comment_count": [comment_count] * l,
            "forward_count": [forward_count] * l,
            "comment": comment,
            "c_time": c_time,
            "flag": [flag] * l,
            "code": [code] * l}
    df = pd.DataFrame(dict)
    df = df[["title", "time", "content", "click_count", "like_count", "comment_count",
             "forward_count", "comment", "c_time", "flag", "code"]]
    df.to_csv("pinglun.csv", mode='a', index=False, header=False)


if __name__ == "__main__":
	# 读取含有网址的csv
    csv= "guba.csv"
    result = readUrl(csv)
    length = len(result[0])
    for i in range(0, length):
        code = result[0][i]
        url = result[1][i]
        # 每处理10条网址，暂停10秒，避免速度过快造成网站崩溃
        if i % 10 == 0:
            time.sleep(10)
        data = get_data(url)
        soup = BeautifulSoup(data.text, 'lxml')
        t = soup.find('div', {'id': 'zwconttbt'})
        if t is None:
            continue
        else:
            title, time2, content, click_count, like_count, comment_count, \
            forward_count, comment, c_time, flag = parse_data(data)
            saveData(title, time2, content, click_count, like_count, comment_count,
                     forward_count, comment, c_time, flag, code)
            print("已处理完第%d个网址" % (i + 1))
