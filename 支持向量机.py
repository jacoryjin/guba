# -*- coding = utf-8 -*-
# 股价涨跌预测
import pandas as pd
import numpy as np
from sklearn import svm
from sklearn import model_selection
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import StratifiedShuffleSplit


# 读取数据
def readCsv(csv):
    data = pd.read_csv(csv, parse_dates=[0], index_col=0)
    return data


# 对照组，x：收盘价、最高价、最低价、开盘价、成交量；y：0或1,1表示当日收盘价大于等于前一日收盘价，否则为0
def get_xy_1(data, dayfeature):
    featurenum = 5 * dayfeature
    x = np.zeros((data.shape[0] - dayfeature, featurenum + 1))
    y = np.zeros((data.shape[0] - dayfeature))
    for i in range(0, data.shape[0] - dayfeature):
        x[i, 0:featurenum] = np.array(data[i:i + dayfeature] \
                                          [[u'close', u'high',
                                            u'low', u'open', u'volume']]).reshape((1, featurenum))
        x[i, featurenum] = data.ix[i + dayfeature][u'open']
    for i in range(0, data.shape[0] - dayfeature):
        if data.ix[i + dayfeature][u'close'] >= data.ix[i + dayfeature][u'open']:
            y[i] = 1
        else:
            y[i] = 0
    return x, y


# 实验组，x：收盘价、最高价、最低价、开盘价、成交量、情感值；y：0或1,1表示当日收盘价大于等于前一日收盘价，否则为0
def get_xy_2(data, dayfeature):
    featurenum = 6 * dayfeature
    x = np.zeros((data.shape[0] - dayfeature, featurenum + 1))
    y = np.zeros((data.shape[0] - dayfeature))
    for i in range(0, data.shape[0] - dayfeature):
        x[i, 0:featurenum] = np.array(data[i:i + dayfeature] \
                                          [[u'close', u'high',
                                            u'low', u'open', u'volume',
                                            u'score']]).reshape((1, featurenum))
        x[i, featurenum] = data.ix[i + dayfeature][u'open']
    for i in range(0, data.shape[0] - dayfeature):
        if data.ix[i + dayfeature][u'close'] >= data.ix[i + dayfeature][u'open']:
            y[i] = 1
        else:
            y[i] = 0
    return x, y


# 设置C、gamma参数值变化范围，使用网格搜索找出最好的参数组合
def svm_param(x, y):
    C_range = [i/10 for i in range(1, 51, 1)]
    gamma_range = [i/10 for i in range(1, 51, 1)]
    param_grid = dict(gamma=gamma_range, C=C_range)
    cv = StratifiedShuffleSplit(n_splits=10, test_size=0.2, random_state=42)
    grid = GridSearchCV(estimator=svm.SVC(), param_grid=param_grid, cv=cv)
    grid.fit(x, y)
    return grid.best_params_


# 创建SVM并进行交叉验证，返回模型准确率
def svmModel(x, y, c, gamma):
    clf = svm.SVC(kernel='rbf', C=c, gamma=gamma)
    result = []
    for i in range(10):
        x_train, x_test, y_train, y_test = model_selection.train_test_split(x, y, test_size=0.2)
        clf.fit(x_train, y_train)
        result.append(np.mean(y_test == clf.predict(x_test)))
    print("svm classifier accuacy:")
    print(result)
    return result


if __name__ == "__main__":
	# 读取外部文件"gujia.csv"
    csv = "gujia.csv"
    data = readCsv(csv)
    # dayfeature表示采用n天的收盘价、最高价等变量作为输入特征，可根据样本做出改变
    dayfeature = 2

    x1, y1 = get_xy_1(data, dayfeature)
    x2, y2 = get_xy_2(data, dayfeature)
    # 训练参数
    best_params = svm_param(x1, y1)
    c = best_params['C']
    gamma = best_params['gamma']
    print(c)
    print(gamma)
    # 输出对照组模型准确率
    result_1 = svmModel(x1, y1, c, gamma)
    print(np.mean(result_1))
    # 输出实验组模型准确率
    result_2 = svmModel(x2, y2, c, gamma)
    print(np.mean(result_2))
