# Config to preprocess raw logs

regL = {
    "original":[],
    "hdfs": ['blk_(|-)[0-9]+','(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)'],
    "bgl": ['core\.[0-9]*'],
    "proxifier": [],
    "hpc": ['([0-9]+\.){3}[0-9]']
}