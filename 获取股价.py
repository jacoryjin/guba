# -*- coding = utf-8 -*-
# 获取指定股票在某段时间的交易数据
import tushare as ts
import pandas as pd


# 读取股票代码
def readCode(csv):
    df = pd.read_csv(csv)
    lst = list(df['代码'])
    code_lst = []
    for ls in lst:
        ls = str(ls)
        ls = '0' * (6 - len(ls)) + ls
        code_lst.append(ls)
    return code_lst


# 从财经包中获取交易数据
def getData(code, start, end):
    data = ts.get_hist_data(code, start, end)
    return data


# 记录不存在交易数据的股票代码，并保存至csv
def checkNone(code_lst, start, end):
    empty_code = []
    for code in code_lst:
        data = getData(code, start, end)
        if data is None or data.empty:
            print(code)
            empty_code.append(code)
    df = pd.DataFrame(empty_code, columns=['code_number'])
    df.to_csv('step1.csv')


# 记录交易数据存在缺失(出现停牌)的股票代码，并保存在csv
def checkMissing(code_lst, start, end):
    check_code = []
    for code in code_lst:
        data = getData(code, start, end)
        # 若股票交易数据没有缺失等情况，数据长度应是39
        if data.shape[0] not in [39]:
            print(code)
            check_code.append(code)
    df = pd.DataFrame(check_code, columns=['code_number'])
    df.to_csv('step2.csv')


# 存储数据
def saveData(code_lst, start, end):
    df = pd.DataFrame()
    for code in code_lst:
        data = getData(code, start, end)
        code_col = [code] * data.shape[0]
        data['code'] = code_col
        df = df.append(data)
        print("正在处理%s股票" % code)
    df.to_csv('newgujia.csv')


if __name__ == "__main__":
    csv = 'daima.csv'
    code_lst = readCode(csv)
    start = '2016-12-12'
    end = '2017-02-03'

    checkNone(code_lst, start, end)
    checkMissing(code_lst, start, end)

    saveData(code_lst, start, end)

