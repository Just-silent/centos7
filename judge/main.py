# coding:UTF-8
# author    :Just_silent
# init time :2021/7/20 16:34
# file      :main.py
# IDE       :PyCharm

import os
from judge.methods import *


def get_result(path, command):
    judge_command = JudgeCommand()
    project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    cs = get_commands(base_path=project_path + '\source\commands')
    command_dict = {'command': []}
    # 补全原始command(目前仅处理不带管道符的多对象命令)
    if command != None and command != []:
        if '|' not in command.split() and '-exec' not in command.split():
            result_dict = judge_command.get_sub_command(command, cs)
            judge_command.format_path(path, result_dict)
            for p in result_dict['obje']:
                command_dict['command'].append(
                    (result_dict['oper'] + ' ' + ' '.join(result_dict['para']) + ' ' + p).replace('  ', ' '))
    return judge_command.get_result(command, cs, path), command_dict


if __name__ == '__main__':
    path = ''
    command = 'rm -rf /var/log/vmware-network.2.log'
    print(get_result(path, command))

'''
目前存在的问题：
    1. 思路设计上的问题
    2. 缺少软件命令集合
    3. 多机器的问题
    4.
'''



'''
目前存在的问题：
    1. 软件安装
    2. 系统与后来文件的区分
    3. 管道暂不考虑
'''









'''
其他问题：
    1. 命令覆盖不全：缺少管道、缺少软件命令
    2. 针对多对象的处理细节
    3. 操作对象补全，但是目前仅只是非管道符类型
    4. 整理代码：集中管理配置：路径等；代码整合简练
'''