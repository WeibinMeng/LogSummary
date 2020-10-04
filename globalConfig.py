#!/usr/bin/python
# -*- coding: UTF-8 -*-

# **********************************************************
# * Author        : Weibin Meng
# * Email         : m_weibin@163.com
# * Create time   : 2020-03-08 23:29
# * Last modified : 2020-03-08 23:29
# * Filename      : globalConfig.py
# * Description   : 
'''
'''
# **********************************************************
#!/usr/bin/env python3
#-*- coding:utf-8 -*-

DATA_PATH = "./data/"
RESULT_PATH = "./results/"
ALGORITHM_PATH = "./algorithm/"

ALGORITHM_LIST = ['IPLoM', 'LKE', 'LogSig', 'FT_tree', 'Spell', 'Drain', 'MoLFI']
DATASET_LIST = ['test', '2kBGL', '2kHPC', '2kHDFS', '2kZookeeper', '2kProxifier', '2kLinux', '2kHadoop']
ALGORITHM_STR = 'IPLoM, LKE, LogSig, FT_tree, Spell, Drain, MoLFI'
DATASET_STR = 'test', '2kBGL, 2kHPC, 2kHDFS, 2kZookeeper, 2kProxifier, 2kHadoop, 2kLinux'

ContextNum = {
    "preceding_word_num": 1,
    "succeeding_word_num": 0,
}

regL = {
    "2kBGL": ['core\.[0-9]*'],
    "2kHPC": ['([0-9]+\.){3}[0-9]'],
    "2kHDFS": ['blk_(|-)[0-9]+','(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)'],
    "2kZookeeper": ['(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)'],
    "2kProxifier": [],
    "2kHadoop": ['(\d+\.){3}\d+'],
    "2kLinux": ['(\d+\.){3}\d+', '\d{2}:\d{2}:\d{2}'],
    "500Proxifier":[],
    "100wExample":[],
    "hadoop": ['(\d+\.){3}\d+'],
    "windows": [],
    "hdfs": ['blk_(|-)[0-9]+','(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)'],
    "bgl": ['core\.[0-9]*'],
    "spark": [],
    "Zookeeper": ['(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)'],
    "Proxifier": [],
    "HPC": ['([0-9]+\.){3}[0-9]']
}

removeCol = {
   "2kBGL": [0,1,2,3,4,5],
   "2kHPC": [0,1],
   "2kHDFS": [0,1,2],
   "2kZookeeper": [0,1,2],
   "2kProxifier": [0,1],
   "2kHadoop": [],
   "2kLinux": [],
   "500Proxifier":[0,1],
   "100wExample":[],
   "hadoop": [],
   "windows": [],
   "hdfs": [],
   "bgl": [],
   "spark": [],
   "Proxifier": [],
   "Zookeeper": [],
   "HPC": []
}

GroupNum = {
    "2kBGL":{"all": 112, "head": 60, "tail": 67},
    "2kHDFS":{"all": 14, "head": 12, "tail": 13},
    "2kHPC":{"all": 44, "head": 38, "tail": 12},
    "2kZookeeper":{"all": 46, "head": 33, "tail": 35},
    "2kProxifier":{"all": 7, "head": 7, "tail": 5},
    "2kHadoop":{"all": 116, "head": 105, "tail": 22},
    "2kLinux":{"all": 123, "head": 28, "tail": 109},
    "500Proxifier":{"all": 7, "head": 7, "tail": 5},
}

def printLine():
    print('*********************************************')

from pprint import pprint
def print_obj(name, obj):
    print(name)#, end=": ")
    pprint(obj)

if __name__ == "__main__":
# run __main__ to print
    print("DATA_PATH:", DATA_PATH)
    print("RESULT_PATH:", RESULT_PATH)
    print("ALGORITHM_PATH:", ALGORITHM_PATH)
    print("")
    print_obj("ContextNum", ContextNum)
    print("")
    print_obj("regL", regL)
    print("")
    print_obj("removeCol", removeCol)
