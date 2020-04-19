#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import os


# pattern 长短不一样影响很大、
# 输出到clusters 读取cluster del 根据词典 生成 train test等文件
def pattern_extract(log_file_dir, log_file_name, log_fttree_out_directory, detailed_message_number, message_type_number, k):

    log_address = log_file_dir + log_file_name
    # 日志列表
    log_list = []
    '''读取源日志文件，转化为数组log_list'''
    with open(log_address, 'r') as file:
        content_list = file.readlines()
        log_list = [x.strip() for x in content_list]

    '''遍历log_list，找出所有日志类型，并构造索引表log_type_index'''
    # 日志类型
    log_type = []
    # 将日志按类型分类后将其索引存储在此变量种，如log_type_index[2]是一个列表，其中存储所有类型为第二种的日志索引
    log_type_index = []
    if message_type_number == -1:
        log_type.append('NO_TYPE')
        log_type_index.append([])
        for i in range(0, len(log_list)):
            log_type_index[0].append(i)
    else:
        for i in range(0, len(log_list)):
            log = []
            for word in log_list[i].split(' '):
                log.append(word)
            if log[message_type_number] in log_type:
                temp = log_type.index(log[message_type_number])
                log_type_index[temp].append(i)
            else:
                log_type.append(log[message_type_number])
                temp = []
                temp.append(i)
                log_type_index.append(temp)
    print(log_type)
    print(len(log_type))

    '''提取log_list中的detailed message存储在log_message中'''
    log_message = []
    for i in range(0, len(log_list)):
        log = []
        for word in log_list[i].split(' '):
            log.append(word)
        log = log[detailed_message_number:]
        log_message.append(log)
    print(log_message[0])

    del log_list

    '''统计所有单词及其出现次数,存储在word_support中'''
    word_support = {}
    for i in range(0, len(log_message)):
        for word in log_message[i]:
            if word in word_support.keys():
                word_support[word] += 1
            else:
                word_support[word] = 1
    print(len(word_support))
    for key, value in word_support.items():
        if value > 2000:
            print(key + ':' + str(value))

    '''将word_support根据value值进行排序,存储在word_list中'''
    word_list = sorted(word_support, key=word_support.__getitem__, reverse=True)
    print(word_list[0])

    '''分别对每一种类型的日志构造FT-tree'''
    print("")
    print("FT_tree:")
    FT_forest = []
    for i in range(0, len(log_type)):
        FT_tree = []
        FT_tree.append(log_type[i])
        for j in range(0, len(log_type_index[i])):
            sub_word_support = {}
            for word in log_message[log_type_index[i][j]]:
                support = word_support[word]
                sub_word_support[word] = support
            sub_word_list = sorted(sub_word_support, key=sub_word_support.__getitem__, reverse=True)
            FT_tree.append(sub_word_list)
        print(FT_tree[1])
        FT_forest.append(FT_tree)

    '''根据阈值k对FT-tree减枝'''
    for i in range(0, len(log_type)):
        for j in range(1, len(FT_forest[i])):
            if len(FT_forest[i][j]) > k:
                FT_forest[i][j] = FT_forest[i][j][:k]

    '''去重'''
    for i in range(0, len(log_type)):
        temp = []
        temp.append(FT_forest[i][0])
        for j in range(1, len(FT_forest[i])):
            if FT_forest[i][j] not in temp:
                temp.append(FT_forest[i][j])
        FT_forest[i] = temp
    print("去重后FT Forest:")
    print(FT_forest)

    '''构建索引表'''
    FT_num = []
    # 索引表,其第i项为第i种日志的FT_tree起始索引
    FT_index = []
    for i in range(0, len(log_type)):
        FT_num.append(len(FT_forest[i]) - 1)
    print(FT_num)
    for i in range(0, len(log_type)):
        FT_index.append(sum(FT_num[:i]) + 1)
    print(FT_index)
    print("聚类总数为：")
    print(sum(FT_num))

    '''将结果输出到log_fttree_out_file中'''
    log_cluster = {}
    log_pattern_key = {}
    for i in range(0, len(log_type)):
        for j in range(0, len(log_type_index[i])):
            sub_word_support = {}
            for word in log_message[log_type_index[i][j]]:
                support = word_support[word]
                sub_word_support[word] = support
            sub_word_list = sorted(sub_word_support, key=sub_word_support.__getitem__, reverse=True)
            # - 1 because the first in the list is message type
            index = FT_forest[i].index(sub_word_list[:k])
            log_key = index + FT_index[i] - 1
            log_pattern = FT_forest[i][0] + ' ' + ' '.join(FT_forest[i][index])
            log_pattern_key[log_pattern] = log_key
            if log_pattern in log_cluster.keys():
                log_cluster[log_pattern].append(log_type_index[i][j])
            else:
                log_cluster[log_pattern] = []
                log_cluster[log_pattern].append(log_type_index[i][j])
            # pattern = message type + FT_forest[i][value]
    # for i in sorted(log_cluster):
    # print((i, log_cluster[i]), end=" ")
    for pattern in log_cluster.keys():
        with open(log_fttree_out_directory + str(log_pattern_key[pattern]), 'w+') as file_obj:
            file_obj.write(pattern + '\n')
            file_obj.write(' '.join(str(x) for x in log_cluster[pattern]))
            i = i + 1
        # print(log_cluster)


if __name__ == '__main__':

    # log input/output address
    log_file_d = './'
    log_file_n = 'Apache.LOG'
    log_fttree_out_f = './' + log_file_n.split('.')[0] + '_fttree'
    out_f = log_fttree_out_f
    # 日志中Detailed message起始字段号
    detailed_message_num = 5
    # 日志中Message type所处字段号 若为-1 则表示无此字段
    message_type_num = 6
    # 阈值k，即树的最大深度-1
    k = 5

    pattern_extract(log_file_d, log_file_n, out_f, detailed_message_num, message_type_num, k)


