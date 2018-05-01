import time
import json
import re
import flavor_distrib as fd
import flavor_predict as fp

def predict_vm(ecs_lines, input_lines):
    # Do your work from here#
    result = []
    if ecs_lines is None:
        print 'ecs information is none'
        return result
    if input_lines is None:
        print 'input file information is none'
        return result

    start_stamp = start_time(ecs_lines)
    data_dict = parse_data(ecs_lines, start_stamp)
    # with open('json_data.json', 'w') as file:
    #     json.dump(data_dict, file)

    input_dict = parse_input(input_lines, start_stamp)
    # print input_dict

    output_dict = Output(data_dict, input_dict)
    # print output_dict

    result = output_lines(output_dict)
    # print result

    return result


def parse_data(data_lines, start_stamp):
    """
    parse train_data and test_data
    """
    data_dict = {}
    #parse the flavor
    for line in data_lines:
        pattern_flavor = re.compile(r'flavor\d+')
        name = (pattern_flavor.findall(line))[0]
        
        # date = line[-20:-1]
        pattern_data = re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')
        date = (pattern_data.findall(line))[0]
        timestamp = time_transfer(date)

        timestamp = (timestamp - start_stamp)/86400

        if name not in data_dict.keys():
            data_dict[name] = [timestamp]
        else:
            data_dict[name].append(timestamp)

    return data_dict


def parse_input(input_lines, start_stamp):
    """
    parse input data

    {'optimizer': 'CPU', 'hard_disk': 1200, 'ram': 128, 'number': 5, 
    'info_list': [['1', '1', '1024'], ['2', '1', '2048'], ['3', '1', '4096'], ['4', '2', '2048'], ['5', '2', '4096']], 
    'start': 1424361600.0, 'end': 1424966400.0, 'cpu': 56}

    """
    input_dict = {}
    mode = re.compile(r'\d+')

    # parse the physical server info
    physical_server = mode.findall(input_lines[0])
    # print physical_server
    input_dict['cpu'] = int(physical_server[0])
    input_dict['ram'] = int(physical_server[1])
    input_dict['hard_disk'] = int(physical_server[2])

    # parse flavor number
    number = mode.findall(input_lines[2])
    number = int(number[0])
    input_dict['number'] = number

    # parse flavor info
    info_list = []
    for line in input_lines[3:3+number]:
        info_list.append(mode.findall(line))
    input_dict['info_list'] = info_list

    # CPU or MEN
    input_dict['optimizer'] = input_lines[4+number][0:3]

    # start and end time
    start = input_lines[6+number][0:19]
    print start
    input_dict['start'] = (time_transfer(start) - start_stamp)/86400
    # print input_dict['start']

    end = input_lines[7+number][0:19]
    print end
    input_dict['end'] = (time_transfer(end) - start_stamp)/86400

    return input_dict


def output_lines(output_dict):
    """
    output the prediction and distribution
    """
    output_lines = []

    vm_num = output_dict['vm_num']
    output_lines.append(str(vm_num))

    info_list = output_dict['info_list']
    for info in info_list:
        output_lines.append(' '.join(info))

    output_lines.append('')

    rm_num = output_dict['rm_num']
    output_lines.append(str(rm_num))

    distribution = output_dict['distribution']
    for i in range(len(distribution)):
        element = str(i + 1) + ' ' + ' '.join(distribution[i])
        # print element
        output_lines.append(element)

    return output_lines


def start_time(data_lines):
    pattern_start = re.compile(r'\d{4}-\d{2}-\d{2} ')
    start = (pattern_start.findall(data_lines[0]))[0]
    start = start + '00:00:00'
    start_stamp = time_transfer(start)
    return start_stamp


def time_transfer(date):
    timeArray = time.strptime(date, "%Y-%m-%d %H:%M:%S")
    timestamp = time.mktime(timeArray)
    return timestamp


def Output(data_dict, input_dict):
    """
    predict the ecs

    {'rm_num': 1, 
    'distribution': [['flavor1', '3', 'flavor2', '3', 'flavor3', '3', 'flavor4', '3', 'flavor5', '3']], 
    'vm_num': 15,
    'info_list': [['flavor1', '3'], ['flavor2', '3'], ['flavor3', '3'], ['flavor4', '3'], ['flavor5', '3']]}
    
    """
    output_dict = {}

    flavor_list = input_dict['info_list']
    start = input_dict['start']
    end   = input_dict['end']

    info_list = []
    vm_num = 0
    for flavor in flavor_list:
        name = 'flavor' + flavor[0]
        data = data_dict.get(name,[])
        num  = fp.flavor_predict(data, start, end)

        info_list.append([name, str(num)])
        vm_num += num

    optimizer = input_dict['optimizer']
    cpu = input_dict['cpu']
    ram = input_dict['ram']
    print flavor_list, '\n', info_list
    # print cpu,ram
    distribution = fd.flavor_distrib(flavor_list, info_list, optimizer, cpu, ram*1024)
    info_list, vm_num = fd.get_new_info_list(distribution, info_list)
    # print distribution

    output_dict['info_list'] = info_list
    output_dict['vm_num'] = vm_num
    
    output_dict['distribution'] = distribution
    output_dict['rm_num'] = len(distribution)

    return output_dict


# def flavor_predict(data, start, end):
#     """
#     holt_winters, ARIMA, GARCH, EGRCH, multivariate GARCH
#     """
#     return 25



# def flavor_distrib(flavor_list, info_list, optimizer, cpu, ram):
#     return [['flavor1', '3', 'flavor2', '3', 'flavor3', '3', 'flavor4', '3', 'flavor5', '3']]
