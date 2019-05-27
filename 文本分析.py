# 基于情感词典的文本分析方法，对评论情感打分
from collections import defaultdict
import jieba
import codecs
import pandas as pd


# 使用jieba对文档分词，并去除停用词
def seg_word(sentence, stopwords):
    seg_list = jieba.cut(sentence)
    seg_result = []
    for w in seg_list:
        seg_result.append(w)
    return list(filter(lambda x: x not in stopwords, seg_result))


# 词语分类,找出情感词、否定词、程度副词
# 分类结果，词语的index作为key,词语的分值作为value，否定词分值设为-1
def classify_words(word_dict, sen_dict, not_word_list, degree_dic):
    sen_word = dict()
    not_word = dict()
    degree_word = dict()

    for word in word_dict.keys():
        if word in sen_dict.keys() and word not in not_word_list and word not in degree_dic.keys():
            sen_word[word_dict[word]] = sen_dict[word]
        elif word in degree_dic.keys() and word not in not_word_list:
            degree_word[word_dict[word]] = degree_dic[word]
        elif word in not_word_list:
            not_word[word_dict[word]] = -1

    return sen_word, not_word, degree_word


# 将分词后的列表转为字典，key为单词，value为单词在列表中的索引，索引相当于词语在文档中出现的位置
def list_to_dict(word_list):
    data = {}
    for x in range(0, len(word_list)):
        data[word_list[x]] = x
    return data


def get_init_weight(sen_word, not_word, degree_word):
    # 权重初始化为1
    W = 1
    # 将情感字典的key转为list
    sen_word_index_list = list(sen_word.keys())
    if len(sen_word_index_list) == 0:
        return W
    # 获取第一个情感词的下标，遍历从0到此位置之间的所有词，找出程度词和否定词
    for i in range(0, sen_word_index_list[0]):
        if i in not_word.keys():
            W *= -1
        elif i in degree_word.keys():
            # 更新权重，如果有程度副词，分值乘以程度副词的程度分值
            W *= float(degree_word[i])
    return W


def score_sentiment(sen_word, not_word, degree_word, seg_result):
    """计算得分"""
    score = 0
    W = get_init_weight(sen_word, not_word, degree_word)
    # 情感词下标初始化
    sentiment_index = -1
    # 情感词的位置下标集合
    sentiment_index_list = list(sen_word.keys())
    # 遍历分词结果(遍历分词结果是为了定位两个情感词之间的程度副词和否定词)
    for i in range(0, len(seg_result)):
        # 如果是情感词（根据下标是否在情感词分类结果中判断）
        if i in sen_word.keys():
            # 权重*情感词得分
            score += W * float(sen_word[i])
            W = 1
            # 情感词下标加1，获取下一个情感词的位置
            sentiment_index += 1
            if sentiment_index < len(sentiment_index_list) - 1:
                # 判断当前的情感词与下一个情感词之间是否有程度副词或否定词
                for j in range(sentiment_index_list[sentiment_index], sentiment_index_list[sentiment_index + 1]):
                    # 更新权重，如果有否定词，取反
                    if j in not_word.keys():
                        W *= -1
                    elif j in degree_word.keys():
                        # 更新权重，如果有程度副词，分值乘以程度副词的程度分值
                        W *= float(degree_word[j])
        # 定位到下一个情感词
        if sentiment_index < len(sentiment_index_list) - 1:
            i = sentiment_index_list[sentiment_index + 1]
    return score


# 计算得分
def setiment_score(sententce, stopwords, sen_dict, not_word_list, degree_dic):
    # 1.对文档分词
    seg_list = seg_word(sententce, stopwords)
    # 2.将分词结果列表转为dic，然后找出情感词、否定词、程度副词
    sen_word, not_word, degree_word = classify_words(list_to_dict(seg_list), sen_dict, not_word_list, degree_dic)
    # 3.计算得分
    score = score_sentiment(sen_word, not_word, degree_word, seg_list)
    return score


# 读取含有评论的csv
def getSen(csv):
    df = pd.read_csv(csv)
    lst = list(df['code'])
    code_lst = []
    for ls in lst:
        ls = str(ls)
        ls = '0' * (6 - len(ls)) + ls
        code_lst.append(ls)
    time = list(df['time'])
    comment = list(df['comment'])
    click = list(df['click'])
    result = [code_lst, time, comment, click]
    return result


# 存储数据
def saveData(code, time, score, click):
    result = [code, time, score, click]
    df = pd.DataFrame([result], columns=['code', 'time', 'score', 'click'])
    df.to_csv("newscore_buchong.csv", mode='a', index=False, header=False)


if __name__ == "__main__":
    # 读取停用词文件
    stopwords = set()
    fr = codecs.open('stopwords.txt', 'r', 'utf-8')
    for word in fr:
        stopwords.add(word.strip())
    fr.close()

    # 读取情感字典文件
    sen_file = open('BosonNLP_sentiment_score.txt', 'r+', encoding='utf-8')
    # 获取字典文件内容
    sen_list = sen_file.readlines()
    # 创建情感字典
    sen_dict = defaultdict()
    # 读取字典文件每一行内容，将其转换为字典对象，key为情感词，value为对应的分值
    for s in sen_list:
        # 每一行内容根据空格分割，索引0是情感词，索引1是情感分值
        try:
            sen_dict[s.split(' ')[0]] = s.split(' ')[1]
        except IndexError:
            pass
    sen_file.close()

    # 读取否定词文件
    not_word_file = open('notDic.txt', 'r+', encoding='utf-8')
    # 由于否定词只有词，没有分值，使用list即可
    not_word_list = not_word_file.readlines()
    for i in range(0, len(not_word_list)):
        not_word_list[i] = not_word_list[i].strip('\n')
    not_word_file.close()

    # 读取程度副词文件
    degree_file = open('degree.txt', 'r+', encoding='gbk')
    degree_list = degree_file.readlines()
    degree_dic = defaultdict()
    # 程度副词与情感词处理方式一样，转为程度副词字典对象，key为程度副词，value为对应的程度值
    for d in degree_list:
        try:
            degree_dic[d.split(',')[0]] = d.split(',')[1]
        except IndexError:
            pass
    degree_file.close()

    # 测试
    # string = "操盘者每天把股价牢牢控制在圆角分上，想想这能力、这技术能让散户喝上汤吗？就靠着这几分钱加上时间足以榨干每一个小散。"
    # print(setiment_score(string, stopwords, sen_dict, not_word_list, degree_dic))

    result = getSen('newpinglun_buchong.csv')
    length = len(result[0])
    for i in range(0, length):
        code = result[0][i]
        time = result[1][i]
        comment = result[2][i]
        click = result[3][i]
        score = setiment_score(comment, stopwords, sen_dict, not_word_list, degree_dic)
        saveData(code, time, score, click)
        print("已处理完成第%d个文本" % (i + 1))
