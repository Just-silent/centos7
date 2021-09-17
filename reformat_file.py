# coding:UTF-8
# author    :Just_silent
# init time :2021/7/16 14:25
# file      :reformat_file.py
# IDE       :PyCharm

import numpy as np
import pandas as pd
from tqdm import tqdm

def rf_file(path, new_path):
    csv = pd.read_csv(path, header=None)
    np_csv = np.array(csv)
    node_dict = {
        'name':[],
        'id':[],
        'path':[],
        'file_type':[],
        'u1_rwx':[],
        'u2_rwx':[],
        'u3_rwx':[],
        'change_ts':[],
        'user_name':[],
        'group_name':[],
        'size':[],
        'time':[]
    }
    for one in tqdm(np_csv):
        node_dict['name'].append(one[0])
        node_dict['id'].append(one[2])
        node_dict['path'].append(one[3])
        other = eval(one[4])
        if other=={}:
            other={
                'file_type':'',
                'u1_rwx':'',
                'u2_rwx':'',
                'u3_rwx':'',
                'change_ts':'',
                'user_name':'',
                'group_name':'',
                'size':'',
                'time':'',
            }
        node_dict['file_type'].append(other['file_type'])
        node_dict['u1_rwx'].append(other['u1_rwx'])
        node_dict['u2_rwx'].append(other['u2_rwx'])
        node_dict['u3_rwx'].append(other['u3_rwx'])
        node_dict['change_ts'].append(other['change_ts'])
        node_dict['user_name'].append(other['user_name'])
        node_dict['group_name'].append(other['group_name'])
        node_dict['size'].append(other['size'])
        node_dict['time'].append(other['time'])
    dataframe = pd.DataFrame(node_dict)
    dataframe.to_csv(new_path, index=False, sep=',')
    pass

if __name__ == '__main__':
    files = ['./neo4j_file/file_node.csv', './neo4j_file/folder_node.csv']
    new_files = ['./new_neo4j_file/file_node.csv', './new_neo4j_file/folder_node.csv']
    for path, new_path in zip(files, new_files):
        rf_file(path, new_path)