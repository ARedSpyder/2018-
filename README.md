# 2018华为软件精英挑战赛
## 赛题介绍：[2018华为软件精英挑战赛](http://codecraft.devcloud.huaweicloud.com/home/detail)
## 运行环境：python 2.7
## 运行：python trainxxx.txt inputxxx.txt output.txt
* 初赛：python ecs.py TrainData_2015.1.1_2015.2.19.txt input_5flavors_cpu_7days.txt output.txt 

* 复赛：python ecs.py TrainData_2015.12.txt input_3hosttypes_5flavors_1week.txt output.txt

## 方法简述：
* 预测：使用线性模型，采取前n天对后m天的flavor数量进行预测，参数通过离线训练得到
* 装箱：初赛先通过首次匹配确定大致数量，然后使用退火算法优化。复赛先计算所需的cpu和mem，然后通过线性规划确定大致的物理机数量，然后进行首次匹配，判断能否装完，若能，则退出，否则通过退火算法使利用率最大，再对余下虚拟机重复以上操作。初赛和复赛阶段的利用率大致能达到0.9。

## 效果简述：
* 初赛：武长赛区第8名
* 复赛：武长赛区第26名

## 补充：
* 只包括线上测试代码，数据处理和训练代码未给出
* 预测部分还有一些小trick，未给出
