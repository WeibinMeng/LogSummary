import re
regL = {
    "2kBGL": ['core\.[0-9]*'],
    "2kHPC": ['([0-9]+\.){3}[0-9]'],
    "2kHDFS": ['blk_(|-)[0-9]+','(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)'],
    "2kZookeeper": ['(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)'],
    "2kProxifier": [],
    "2kHadoop": ['(\d+\.){3}\d+'],
    "2kLinux": ['(\d+\.){3}\d+', '\d{2}:\d{2}:\d{2}'],
    "500Proxifier":[],
    "switch":[],
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
   "switch":[0,1,2],
   "hadoop": [0,1,2,3,4],
   "windows": [],
   "hdfs": [0,1,2],
   "bgl": [0],
   "spark": [0,1],
   "Proxifier": [0,1],
   "Zookeeper": [0,1,2,4,5],
   "HPC": [0,1]
}

add_space_str = set([":", "[", "]", "{", "}", ";", "(", ")", "=", ','])

def rexRemove(rex, line):
    for currentRex in rex:
        line = re.sub(currentRex, '', line)
    return line

def add_space(log):
    log_list = list(log)
    add_space_str = set([":", "[", "]", "{", "}", ";", "(", ")", "=", ','])
    new_log = []
    for index in range(len(log_list)):
        ch = log_list[index]
        new_log.append(ch)
        if ch in add_space_str:
            if index > 0 and log_list[index-1] != ' ':
                new_log.insert(len(new_log)-1, ' ')
            if index < (len(log_list)-1) and log_list[index+1] != ' ':
                new_log.insert(len(new_log), ' ')
    processed_log = ''.join(new_log)
    processed_log = processed_log.strip()
    return processed_log   
                                                                            
def split_col(log):
    temp = log.strip().split()
    result = []
    is_pair = False
    for word in temp:
        if '[' in word and ']' not in word:
            is_pair = True
            buffer = ''
        if is_pair:
            buffer += word + ' '
            if ']' in word:
                is_pair = False
                result.append(buffer.strip())
        else:
            result.append(word)
    return result

def remove_column(log, log_type):
    temp = split_col(log)
    if len(temp) - len(removeCol[log_type]) >= 3:
        temp = [word for i, word in enumerate(temp) if i not in removeCol[log_type]]
    newLog = ' '.join(temp)
    newLog = newLog.strip()
    return newLog

def process_log(args):
    ifile = open(args.i, 'r')
    ofile = open(args.o, 'w')
    count = 1
    skip_flag = 0
    debug_mode = args.d
    if debug_mode:
        temp = args.i.split('/')[-1]
        dfile = open('debug_'+temp, 'w')
    for log in ifile:
        if "===" in log:
            skip_flag = not skip_flag
            if skip_flag == True:
                continue
        if skip_flag == True:
            if debug_mode:
                dfile.write(log)
            continue  
        if args.t == "100wExample" and "Are you sure to continue? [Y/N]" in log:
            newLog = log.strip()
        else: 
            newLog = remove_column(log, args.t) 
        if len(newLog) < 3:
            if debug_mode:
                dfile.write(log)
            continue
        newLog = add_space(newLog)
        newLog = rexRemove(regL[args.t], newLog)
        ofile.write(str(count) + '\t' + newLog + '\n')
        count += 1
    if debug_mode:
        dfile.close()
    ifile.close()
    ofile.close()

import argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', help='debug mode', default=0, type=int)
    parser.add_argument('-t', help='data type')
    parser.add_argument('-i', help='input file')
    parser.add_argument('-o', help='output file')
    args = parser.parse_args()
    process_log(args)
    print("add serial end")
