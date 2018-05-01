# coding=utf-8
import random
import math
import copy
import collections

#---------------------------优化函数----------------------------------
def flavor_demand_sort(info_list,flavor_dic):
    fla_dic = {}
    for flavor in info_list:
        fla_dic.update({flavor[0]:int(flavor[1])})
    flavor_demand_list = fla_dic.keys()
    for j in range(len(flavor_demand_list)):
        for i in range(len(flavor_demand_list)-j-1):
            if fla_dic[flavor_demand_list[i]] < fla_dic[flavor_demand_list[i+1]]:
                temp = flavor_demand_list[i+1]
                flavor_demand_list[i+1] = flavor_demand_list[i]
                flavor_demand_list[i] = temp
    #print flavor_demand_list
    return flavor_demand_list

#优化整体预期收益
def optimize_efficiency(fla_distrib,rm_info,flavor_dic,info_list):
    flavor_filler = []
    flav_list = flavor_demand_sort(info_list,flavor_dic)
    rm_keys = fla_distrib.keys()
    #找出空间最大的机器
    max_key = ''
    max_ind = 0
    max_remain = 0
    mx_cpu_remain = 0
    mx_ram_remain = 0
    for key in rm_keys:     #服务器类别
        ind = -1
        for server in fla_distrib[key]:    #服务器
            cpu_remain = int(rm_info[key][0])
            ram_remain = int(rm_info[key][1])*1024
            for item in server:     #虚拟机
                cpu_remain = cpu_remain - flavor_dic[item][0]
                ram_remain = ram_remain - flavor_dic[item][1]
            remain = cpu_remain + ram_remain/1024
            ind = ind + 1
            if remain > max_remain:
                max_key = key
                max_ind = ind
                max_remain = remain
                mx_cpu_remain = cpu_remain
                mx_ram_remain = ram_remain

    #优化资源利用率
    if max_key:
        this_server = fla_distrib[max_key][max_ind]
        resource = int(rm_info[max_key][0]) + int(rm_info[max_key][1])
        if max_remain/float(resource) > 0.8:
            flav_set = set(this_server)
            for i in flav_set:
                if this_server.count(i) >= 2:
                    return fla_distrib
            fla_distrib[max_key].pop(max_ind)
        else:
            flavor_filler =  [flav_list[0],flav_list[1],flav_list[2],flav_list[0],flav_list[1],flav_list[2]]
            for flavor in flavor_filler:
                if mx_cpu_remain >= flavor_dic[flavor][0] and mx_ram_remain >= flavor_dic[flavor][1]:
                    mx_cpu_remain = mx_cpu_remain - flavor_dic[flavor][0]
                    mx_ram_remain = mx_ram_remain - flavor_dic[flavor][1]
                    fla_distrib[max_key][max_ind].append(flavor)
    return fla_distrib

#---------------------------测试函数----------------------------------
def efficiency_test(flavor_dic,rm_info,distribution):
    rm_keys = distribution.keys()
    total_cpu = 0
    total_ram = 0
    cpu_demand = 0
    ram_demand = 0
    for key in rm_keys:
        total_cpu = total_cpu + int(rm_info[key][0])*len(distribution[key])
        total_ram = total_ram + int(rm_info[key][1])*1024*len(distribution[key])
        for item in distribution[key]:
            for i in range(len(item)/2):
                cpu_demand = cpu_demand + flavor_dic[item[2*i]][0]*int(item[2*i+1])
                ram_demand = ram_demand + flavor_dic[item[2*i]][1]*int(item[2*i+1])
    cpu_efficiency = cpu_demand/float(total_cpu)
    ram_efficiency = ram_demand/float(total_ram)
    efficiency = (cpu_efficiency+ram_efficiency)/float(2)
    return efficiency

def get_infolist(distribution,rm_keys):
    f_list = []
    result = []
    temp = []
    for key in rm_keys:
        items = distribution[key]
        for server in items:
            for flavor in server:
                f_list.append(flavor)
    counter = collections.Counter(f_list)
    types = set(f_list)
    for type in types:
        temp.append(type)
        temp.append(str(counter[type]))
        result.append(temp)
        temp = []
    return result

#--------------------------输出函数-----------------------------------
#整理为输出格式
def output_distrib(distribution,rm_keys):
    i = 0
    server_distribution = {}
    for key in rm_keys:
        temp = []
        server_temp = []
        items = distribution[key]
        for server in items:
            types = set(server)
            counter = collections.Counter(server)
            for type in types:
                temp.append(type)
                temp.append(str(counter[type]))
                i = i + counter[type]
            server_temp.append(temp)
            temp = []
        server_distribution.update({key:server_temp})
    print 'flanum: ',i
    #print server_distribution
    return server_distribution

#--------------------------分析函数-----------------------------------
def demand_analyze(flavor_dic, fla_dis_list):
    f_list = []
    cpu_demand = 0
    ram_demand = 0
    types = set(fla_dis_list)
    for item in types:
        cpu_demand = cpu_demand + flavor_dic[item][0]*fla_dis_list.count(item)
        ram_demand = ram_demand + flavor_dic[item][1]*fla_dis_list.count(item)
    return cpu_demand, ram_demand

#物理机分配效率分析
def server_effciency(rm_info,m_list,rm_keys,cpu_demand,ram_demand):
    efficiency = 0
    cpu_resource = 0    #cpu资源
    ram_resource = 0    #ram资源
    i = 0
    for key in rm_keys:
        cpu_resource = cpu_resource + int(rm_info[key][0])*m_list[i]
        ram_resource = ram_resource + int(rm_info[key][1])*1024*m_list[i]
        i = i+1
    #在物理机资源满足的条件下,效率为cpu需求/cpu资源+ram需求/ram资源
    if cpu_resource>=cpu_demand and ram_resource>=ram_demand:
        cpu_efficiency = cpu_demand/float(cpu_resource)
        ram_efficiency = ram_demand/float(ram_resource)
        efficiency = (cpu_efficiency+ram_efficiency)/float(2)
    else:
        efficiency = 0
    return efficiency

#虚拟机分配效率分析
def flavor_effciency(cpu,ram,index,flavor_dic, fla_dis_list):
    efficiency = 0
    f_list = fla_dis_list[:index]
    cpu_demand, ram_demand = demand_analyze(flavor_dic, f_list)
    efficiency = cpu_demand/float(cpu) + ram_demand/float(ram)
    return efficiency

#------------------------虚拟机分配函数-------------------------------
#首次匹配函数分配虚拟机
def first_fit(rm_distrib,rm_info,fla_dis_list,flavor_dic):
    index = 0
    rm_keys = rm_distrib.keys()
    distribution = {}
    for key in rm_keys:
        distribution.update({key:[]})
    #预先分配物理机分配
    for key in rm_keys:
        for i in range(rm_distrib[key]):
            temp = []
            cpu_remain = int(rm_info[key][0])
            ram_remain = int(rm_info[key][1])*1024
            if index < len(fla_dis_list):
                while cpu_remain>=flavor_dic[fla_dis_list[index]][0] and ram_remain>=flavor_dic[fla_dis_list[index]][1]:
                    cpu_remain = cpu_remain - flavor_dic[fla_dis_list[index]][0]
                    ram_remain = ram_remain - flavor_dic[fla_dis_list[index]][1]
                    temp.append(fla_dis_list[index])
                    index = index+1
                    if index == len(fla_dis_list):
                        break
            if temp:
                distribution[key].append(temp)
    return distribution, index

#模拟退火得到虚拟机配置
def flavor_sa(rm_distrib,rm_info,fla_dis_list,flavor_dic):
    #物理机资源
    distribution = {}
    cpu = 0
    ram = 0
    rm_keys = rm_distrib.keys()
    for key in rm_keys:
        cpu = cpu + int(rm_info[key][0])*rm_distrib[key]
        ram = ram + int(rm_info[key][1])*1024*rm_distrib[key]
    #首次分配
    distribution, index = first_fit(rm_distrib,rm_info,fla_dis_list,flavor_dic)

    efficiency = flavor_effciency(cpu,ram,index,flavor_dic, fla_dis_list)

    #模拟退火条件
    Tmin = 1  #终止条件
    at = 0.999  #降温系数
    T = 100.0   #初始温度
    #退火过程
    while T > Tmin:
        new_efficiency = 0
        new_index = 0
        new_distribution = {}
        for key in rm_keys:
            new_distribution.update({key:[]})
        new_fla_dis_list = copy.deepcopy(fla_dis_list)
        #产生新解:两个虚拟机交换位置
        index0 = random.randint(0,len(new_fla_dis_list)-1)
        index1 = random.randint(0,len(new_fla_dis_list)-1)
        while new_fla_dis_list[index0] == new_fla_dis_list[index1]:
            index1 = random.randint(0,len(new_fla_dis_list)-1)
        temp = new_fla_dis_list[index0]
        new_fla_dis_list[index0] = new_fla_dis_list[index1]
        new_fla_dis_list[index1] = temp  #交换虚拟机分配
        #再次分配
        new_distribution, new_index = first_fit(rm_distrib,rm_info,new_fla_dis_list,flavor_dic)

        #计算效率增量
        new_efficiency = flavor_effciency(cpu,ram,new_index,flavor_dic,new_fla_dis_list)

        df = new_efficiency - efficiency
        #退火
        if df > 0:
            for key in rm_keys:
                distribution[key] = new_distribution[key]
            fla_dis_list = new_fla_dis_list[:]
            efficiency = new_efficiency
            index = new_index
        elif math.exp(df/float(T))>=random.random():
            for key in rm_keys:
                distribution[key] = new_distribution[key]
            fla_dis_list = new_fla_dis_list[:]
            efficiency = new_efficiency
            index = new_index
        T = T * at
    return distribution,efficiency,index,fla_dis_list

#------------------------物理机分配函数-------------------------------
#循环得到物理机初步配置
def server_distib(rm_info,cpu_demand,ram_demand):
    rm_distrib = {}     #物理机分配
    rm_keys = rm_info.keys()    #物理机种类
    rm_num = [0]*len(rm_keys)
    #算出范围值
    for i in range(len(rm_keys)):
        num_cpu = math.ceil(cpu_demand/float(int(rm_info[rm_keys[i]][0])))
        num_ram = math.ceil(ram_demand/float(int(rm_info[rm_keys[i]][1])*1024))
        rm_num[i] = int(max(num_cpu,num_ram))

    #初始化rm_distrib
    for i in range(len(rm_keys)):
        rm_distrib.update({rm_keys[i]:rm_num[i]})
    #循环
    efficiency = 0
    for i0 in range(rm_num[0]+1):
        for i1 in range(rm_num[1]+1):
            for i2 in range(rm_num[2]+1):
                m_list = [i0,i1,i2]
                new_efficiency = server_effciency(rm_info,m_list,rm_keys,cpu_demand,ram_demand)
                if new_efficiency > efficiency:
                    efficiency = new_efficiency
                    for i in range(len(rm_keys)):
                        rm_distrib[rm_keys[i]] = m_list[i]

    return rm_distrib

#-------------------------主分配函数----------------------------------
def flavor_distrib(flavor_list, info_list, rm_info):
    #变量初始化
    distribution = {}
    index = 0
    efficiency = 0
    rm_keys = rm_info.keys()
    Flag = True     #调试用
    for key in rm_keys:
        distribution.update({key:[]})
    #将虚拟机列表转为字典形式
    flavor_dic = {}
    for flavor in flavor_list:
        flavor_dic.update({('flavor'+flavor[0]):[int(flavor[1]),int(flavor[2])]})
    #初始虚拟机分配队列
    fla_dis_list = []
    random.seed(10) #给个随机种子
    for flavor in info_list:
        for i in range(int(flavor[1])):
            if fla_dis_list:
                pos = random.randint(0,len(fla_dis_list)-1)
                fla_dis_list.insert(pos,flavor[0])
            else:
                fla_dis_list.append(flavor[0])

    #虚拟机分配
    while Flag:
        index = 0
        #需求分析
        cpu_demand, ram_demand = demand_analyze(flavor_dic, fla_dis_list)
        #物理机分配
        rm_distrib = server_distib(rm_info,cpu_demand,ram_demand)
        #虚拟机分配
        fla_distrib, index = first_fit(rm_distrib,rm_info,fla_dis_list,flavor_dic)
        #如果分配完毕,结束
        if index == len(fla_dis_list):
            #优化资源利用率
            fla_distrib = optimize_efficiency(fla_distrib,rm_info,flavor_dic,info_list)
            fla_distrib = optimize_efficiency(fla_distrib,rm_info,flavor_dic,info_list)
            #添加分配
            for key in rm_keys:
                temp = distribution[key] + fla_distrib[key]
                distribution.update({key:temp})
            new_info_list = get_infolist(fla_distrib,rm_keys)
            break
        else:
            #退火优化虚拟机分配
            fla_distrib,effic,index,fla_dis_list = flavor_sa(rm_distrib,rm_info,fla_dis_list,flavor_dic)

            for i in range(4):

                fla_distrib1,effic1,index1,fla_dis_list1 = flavor_sa(rm_distrib,rm_info,fla_dis_list,flavor_dic)

                #print effic1,index1
                if effic1 > effic:
                    fla_distrib = copy.deepcopy(fla_distrib1)
                    effic = effic1
                    index = index1
                    fla_dis_list = fla_dis_list1[:]
            #print effic,index

            #剩余虚拟机
            if index == len(fla_dis_list):
                #添加分配方式
                #print fla_distrib
                #优化资源利用率
                fla_distrib = optimize_efficiency(fla_distrib,rm_info,flavor_dic,info_list)
                fla_distrib = optimize_efficiency(fla_distrib,rm_info,flavor_dic,info_list)
                for key in rm_keys:
                    temp = distribution[key] + fla_distrib[key]
                    distribution.update({key:temp})
                new_info_list = get_infolist(fla_distrib,rm_keys)
                break
            else:
                fla_dis_list = fla_dis_list[index:]
                #添加分配方式
                #print fla_distrib
                for key in rm_keys:
                    temp = distribution[key] + fla_distrib[key]
                    distribution.update({key:temp})
                new_info_list = get_infolist(fla_distrib,rm_keys)
                

        #Flag = False

    new_info_list = get_infolist(distribution,rm_keys)
    print new_info_list
    server_distribution = output_distrib(distribution,rm_keys)
    return server_distribution

def get_new_info_list(distribution,info_list):
    rm_keys = distribution.keys()
    f_keys = []
    for i in info_list:
        f_keys.append(i[0])
    #每种虚拟机台数
    f_num = {}
    for f in f_keys:
        f_num.update({f:0})
    #统计
    i = 0
    for key in rm_keys:
        for server in distribution[key]:
            fla_num = len(server)
            for n in range(fla_num/2):
                type_num = f_num[server[2*n]] + int(server[2*n+1])
                f_num.update({server[2*n]:type_num})
    #整理
    info_list = []
    temp = []
    total_num = 0
    for f in f_keys:
        temp.append(f)
        temp.append(str(f_num[f]))
        total_num = total_num + f_num[f]
        info_list.append(temp)
        temp = []
    print info_list,total_num
    return info_list,total_num

#--------------------------测试部分-----------------------------------
def main():
    flavor_list = [['1', '4', '2048'], ['2', '4', '8192'], ['3', '32', '8192'], ['4', '16', '65536'], ['5', '32', '131072']]
    #info_list = [['flavor1', '50'], ['flavor2', '50'], ['flavor3', '50'], ['flavor4', '50'], ['flavor5', '50']]
    info_list = [['flavor1', '100'], ['flavor2', '100'], ['flavor3', '100'], ['flavor4', '100'], ['flavor5', '100']]
    #info_list = [['flavor1', '1']]
    #info_list = [['flavor1', '1'], ['flavor2', '1'], ['flavor3', '1']]
    #info_list = [['flavor1', '20'], ['flavor2', '20'], ['flavor3', '20'], ['flavor4', '20'], ['flavor5', '20']]
    rm_info = {'Large-Memory': ['84', '256', '2400'],'High-Performance': ['112', '192', '3600'],'General': ['56', '128', '1200']}
    distribution = flavor_distrib(flavor_list, info_list, rm_info)
    info_list,total_num = get_new_info_list(distribution,info_list)
    #print distribution


if __name__ == "__main__":
    main()
