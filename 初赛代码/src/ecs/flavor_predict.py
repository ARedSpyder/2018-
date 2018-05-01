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


def count_days(data_list, start):
    days_list = [0 for i in range(start)]
    for data in data_list:
        i = int(data)
        if days_list[i] >= 10:
          continue
        days_list[i] += 1
    return days_list


def array_multiply(X, weight, bias):
    acount = 0
    for i in range(len(X)):
        acount += X[i]*weight[i] + bias
    return acount

def flavor_predict(data_list, start, end):
    if len(data_list) == 0:
        return 0

    # weights, bias = read_weights('weights.txt')
    weights, bias = Weights.get_weight()

    start = int(start)
    end = int(end)

    data = count_days(data_list, start)

    average = float(sum(data))/len(data)
    print average

    slide = 14
    if average <= 0.5:
        for i in range(start,end):
           
            data.append(average)

    else:
        item = math.ceil(float(end-start)/slide)
        item = int(item)

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

    print data[start-3:end]
    amount = round(sum(data[start:end]))
    # print amount
    return int(amount)


