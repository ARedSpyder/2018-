import json
import os
import re
import math
import time
import random
import Weights


def read_lines(file_path):
    if os.path.exists(file_path):
        array = []
        with open(file_path, 'r') as lines:
            for line in lines:
                array.append(line)
        return array
    else:
        print('file not exist: ' + file_path)
        return None


def string_to_num(string):
    mode = re.compile(r'\d+.\d+')
    num = mode.findall(string)
    num_list = []
    for item in num:
        num_list.append(float(item))
    return num_list

def read_weights(file_path):
    array = read_lines(file_path)
    weights = []
    bias = []
    for item in array[:-1]:
        weights.append(string_to_num(item))

    bias = string_to_num(array[-1])
    return weights, bias


def count_days(data_list):
    end = math.ceil(data_list[-1])
    days_list = [0 for i in range(int(end))]
    for data in data_list:
        i = int(data)
        if days_list[i] >= 70:
          continue
        days_list[i] += 1
    return days_list


def array_multiply(X, weight, bias):
    acount = 0
    for i in range(len(X)):
        acount += X[i]*weight[i]
    acount += bias
    return acount

def flavor_predict(data_list, start, end):
    if len(data_list) == 0:
        return 0

    # weights, bias = read_weights('weights.txt')
    weights, bias = Weights.get_weight()

    start = int(round(start))
    end = int(round(end))

    data = count_days(data_list)
    print len(data),start,end
    #if (end - start) > 13:
    #  exit()

    average = float(sum(data))/len(data)
    print average

    slide = 28
    if average <= 1.2:
        for i in range(len(data),end):
           
            data.append(average)

    else:
        item = math.ceil(float(end-len(data))/slide)
        item = int(item)
        # print item,len(data)

        for i in range(item):
            X = data[-13:]
            for ind in range(slide):
                num_pred = array_multiply(X, weights[ind], bias[ind])
                # if num_pred >= 30:
                #     num_pred += 30
                data.append(num_pred)
                # data.append(average)

    # for i in range(start, end):
    #     X = data[-14]
    print len(data),data[start:end]
    amount = round(sum(data[start:end]))
    # print amount
    #if amount > 150:
    #  exit()
    return int(amount)


