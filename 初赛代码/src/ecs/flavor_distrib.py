# coding=utf-8
import random
import math

def flavor_demand_sort(info_list,flavor_dic,optimizer):
    fla_dic = {}
    for flavor in info_list:
        fla_dic.update({flavor[0]:int(flavor[1])})
    flavor_demand_list = fla_dic.keys()
    if optimizer == 'CPU':
        for j in range(len(flavor_demand_list)):
            for i in range(len(flavor_demand_list)-j-1):
                #if fla_dic[flavor_demand_list[i]]+flavor_dic[flavor_demand_list[i]][0] < fla_dic[flavor_demand_list[i+1]]+flavor_dic[flavor_demand_list[i+1]][0]:
                if fla_dic[flavor_demand_list[i]] < fla_dic[flavor_demand_list[i+1]]:
                    temp = flavor_demand_list[i+1]
                    flavor_demand_list[i+1] = flavor_demand_list[i]
                    flavor_demand_list[i] = temp
    elif optimizer == 'MEM':
        for j in range(len(flavor_demand_list)):
            for i in range(len(flavor_demand_list)-j-1):
                #if fla_dic[flavor_demand_list[i]]+flavor_dic[flavor_demand_list[i]][1]/1024 < fla_dic[flavor_demand_list[i+1]]+flavor_dic[flavor_demand_list[i+1]][1]/1024:
                if fla_dic[flavor_demand_list[i]] < fla_dic[flavor_demand_list[i+1]]:
                    temp = flavor_demand_list[i+1]
                    flavor_demand_list[i+1] = flavor_demand_list[i]
                    flavor_demand_list[i] = temp
    print flavor_demand_list
    return flavor_demand_list

#optimize the efficiency by redistribution
def optimize_efficiency(distribution,optimizer,cpu,ram,flavor_dic,info_list):
    flavor_filler = []
    flavor_demand_list = flavor_demand_sort(info_list,flavor_dic,optimizer)
    #the resource remain
    last_server = distribution[(len(distribution)-1)]
    cpu_remain = cpu
    ram_remain = ram
    for item in last_server:
        cpu_remain = cpu_remain - flavor_dic[item][0]
        ram_remain = ram_remain - flavor_dic[item][1]
    #optimize
    if optimizer == 'CPU':
        if cpu_remain/float(cpu) > 0.8:
            flav_set = set(last_server)
            for i in flav_set:
                if last_server.count(i) >= 2:
                    return distribution
            #redistribution
            distribution.pop((len(distribution)-1))
        else:
            flavor_filler =  [flavor_demand_list[0],flavor_demand_list[0],flavor_demand_list[1],flavor_demand_list[2],flavor_demand_list[0],flavor_demand_list[1],flavor_demand_list[2]]
            for flavor in flavor_filler:
                    if cpu_remain >= flavor_dic[flavor][0] and ram_remain >= flavor_dic[flavor][1]:
                        cpu_remain = cpu_remain - flavor_dic[flavor][0]
                        ram_remain = ram_remain - flavor_dic[flavor][1]
                        distribution[(len(distribution)-1)].append(flavor)
    elif optimizer == 'MEM':
        if ram_remain/float(ram) > 0.8:
            flav_set = set(last_server)
            for i in flav_set:
                if last_server.count(i) >= 2:
                    return distribution
            distribution.pop((len(distribution)-1))
        else:
            flavor_filler =  [flavor_demand_list[0],flavor_demand_list[0],flavor_demand_list[1],flavor_demand_list[2],flavor_demand_list[0],flavor_demand_list[1],flavor_demand_list[2]]
            for flavor in flavor_filler:
                    if cpu_remain >= flavor_dic[flavor][0] and ram_remain >= flavor_dic[flavor][1]:
                        cpu_remain = cpu_remain - flavor_dic[flavor][0]
                        ram_remain = ram_remain - flavor_dic[flavor][1]
                        distribution[(len(distribution)-1)].append(flavor)
    return distribution

#--------------------------------
def sort_by_optimizer(flavor_dic,optimizer):
    opti_list = flavor_dic.keys()
    if optimizer == 'CPU':
        for j in range(len(opti_list)):
            for i in range(len(opti_list)-j-1):
                if flavor_dic[opti_list[i]][0] < flavor_dic[opti_list[i+1]][0]:
                    temp = opti_list[i+1]
                    opti_list[i+1] = opti_list[i]
                    opti_list[i] = temp
    elif optimizer == 'MEM':
        for j in range(len(opti_list)):
            for i in range(len(opti_list)-j-1):
                if flavor_dic[opti_list[i]][1] < flavor_dic[opti_list[i+1]][1]:
                    temp = opti_list[i+1]
                    opti_list[i+1] = opti_list[i]
                    opti_list[i] = temp
    return opti_list

#--------------------------------

#how many servers are need to satisfy the demand of cpu and ram
def server_demand(flavor_dic,info_list,cpu,ram):
    cpu_demand = 0  #the total cpu demand
    ram_demand = 0  #the total ram demand
    for flavor_request in info_list:
        flavor_type = flavor_request[0]     #the flavor type
        flavor_num = int(flavor_request[1]) #the pridicted number of this flavor type
        cpu_demand = cpu_demand + flavor_dic[flavor_type][0] * flavor_num
        ram_demand = ram_demand + flavor_dic[flavor_type][1] * flavor_num
    number_of_server = int(max(math.ceil(cpu_demand/float(cpu)),math.ceil(ram_demand/float(ram))))
    return number_of_server

def distribution_efficiency(distribution,flavor_dic,cpu,ram,optimizer):
    server_number = len(distribution)
    if server_number == 0:
        print 'OK'
    last_server = distribution[(server_number-1)]
    demand = 0
    if optimizer == 'CPU':
        for flavors in last_server:
            demand = demand + flavor_dic[flavors][0]
            efficiency = demand/float(cpu)
    elif optimizer == 'MEM':
        for flavors in last_server:
            demand = demand + flavor_dic[flavors][1]
            efficiency = demand/float(ram)
    efficiency = efficiency + 10*(server_number - 1)
    return efficiency

def first_fit(flavor_distrib_list,flavor_dic,cpu,ram):
    distribution = []
    cpu_remain = cpu
    ram_remain = ram
    server_conf = []
    for flavor in flavor_distrib_list:
        if cpu_remain >= flavor_dic[flavor][0] and ram_remain >= flavor_dic[flavor][1]:
            cpu_remain = cpu_remain - flavor_dic[flavor][0]
            ram_remain = ram_remain - flavor_dic[flavor][1]
            server_conf.append(flavor)
        else:
            cpu_remain = cpu
            ram_remain = ram
            distribution.append(server_conf)
            server_conf = []
            cpu_remain = cpu_remain - flavor_dic[flavor][0]
            ram_remain = ram_remain - flavor_dic[flavor][1]
            server_conf.append(flavor)
    if server_conf:
        distribution.append(server_conf)
    return distribution


def simulate_annealing(flavor_dic,info_list,cpu,ram,optimizer):
    server_distribution = []
    distribution = []
    new_distribution = []
    efficiency = 0
    new_efficiency = 0
    #进行first fit分配的虚拟机队列
    flavor_distrib_list = []
    new_flavor_distrib_list = []
    ser_number = server_demand(flavor_dic,info_list,cpu,ram)
    for flavor in info_list:
        for i in range(int(flavor[1])):
            if flavor_distrib_list:
                randompos = random.randint(0,len(flavor_distrib_list)-1)
                flavor_distrib_list.insert(randompos,flavor[0])
            else:
                flavor_distrib_list.append(flavor[0])
    distribution = first_fit(flavor_distrib_list,flavor_dic,cpu,ram)
    efficiency = distribution_efficiency(distribution,flavor_dic,cpu,ram,optimizer)
    #模拟退火条件
    Tmin = 1  #终止条件
    at = 0.9999  #降温系数
    T = 100.0   #初始温度
    #退火过程
    while T > Tmin:
        index0 = random.randint(0,len(flavor_distrib_list)-1)
        index1 = random.randint(0,len(flavor_distrib_list)-1) #产生新解
        new_flavor_distrib_list = flavor_distrib_list
        temp = new_flavor_distrib_list[index0]
        new_flavor_distrib_list[index0] = new_flavor_distrib_list[index1]
        new_flavor_distrib_list[index1] = temp  #交换虚拟机分配
        #再次分配
        new_distribution = first_fit(new_flavor_distrib_list,flavor_dic,cpu,ram)
        new_efficiency = distribution_efficiency(new_distribution,flavor_dic,cpu,ram,optimizer)
        #效率增量
        df = new_efficiency - efficiency

        if df < 0:
            flavor_distrib_list = new_flavor_distrib_list
            distribution = new_distribution
            efficiency = new_efficiency
        elif math.exp(-df/float(T))>=random.random():
            flavor_distrib_list = new_flavor_distrib_list
            distribution = new_distribution
            efficiency = new_efficiency
        T = T * at
    #优化资源利用率
    distribution = optimize_efficiency(distribution,optimizer,cpu,ram,flavor_dic,info_list)
    #归并虚拟机分配
    temp = []
    for server in distribution:
        items = set(server)
        for item in items:
            temp.append(item)
            temp.append(str(server.count(item)))
        server_distribution.append(temp)
        temp = []
    return server_distribution, efficiency

def flavor_distrib(flavor_list, info_list, optimizer, cpu, ram):
    distribution = []
    #将虚拟机列表转为字典形式
    flavor_dic = {}
    for flavor in flavor_list:
        flavor_dic.update({('flavor'+flavor[0]):[int(flavor[1]),int(flavor[2])]})
    #模拟退火得到分配
    distribution,efficiency = simulate_annealing(flavor_dic,info_list,cpu,ram,optimizer)
    for i in range(2):
        distribution1,efficiency1 = simulate_annealing(flavor_dic,info_list,cpu,ram,optimizer)
        if efficiency > efficiency1:
            distribution = distribution1
            efficiency = efficiency1
    #print
    cpu_num = 0
    total_cpu = 0
    for item in distribution:
        for i in range(len(item)/2):
            cpu_num = cpu_num + flavor_dic[item[2*i]][0]*int(item[2*i+1])
        total_cpu = total_cpu + cpu_num
        print 'item:',item,'\n'
        print 'cpu',cpu_num,'\n'
        cpu_num = 0
    print 'total cpu',total_cpu,len(distribution)
    return distribution

def get_new_info_list(distribution,info_list):
    keys = []
    for i in info_list:
        keys.append(i[0])
    num = [0]*len(keys)
    for ser in distribution:
        fla_len = len(ser)
        for n in range(fla_len/2):
            index = keys.index(ser[2*n])
            num[index] = num[index] + int(ser[2*n+1])
    info_list = []
    temp = []
    for m in range(len(keys)):
        temp.append(keys[m])
        temp.append(str(num[m]))
        info_list.append(temp)
        temp = []
    total_num = sum(num)
    return info_list,total_num

def main():
    flavor_list = [['1', '4', '1024'], ['2', '6', '2048'], ['3', '12', '4096'], ['4', '16', '2048'], ['5', '8', '4096']]
    info_list = [['flavor1', '11'], ['flavor2', '13'], ['flavor3', '15'], ['flavor4', '10'], ['flavor5', '12']]
    optimizer = 'CPU'
    cpu = 56
    ram = 64*1024
    #demo: distribution = [['flavor5','2'],['flavor5','1','flavor10','1'],['flavor15','1'],['flavor10','1']]
    distribution = flavor_distrib(flavor_list, info_list, optimizer, cpu, ram)
    #print distribution

if __name__ == "__main__":
    main()
