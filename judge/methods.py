# coding:UTF-8
# author    :Just_silent
# init time :2021/7/20 16:34
# file      :methods.py
# IDE       :PyCharm
import os
import json
import subprocess
import pandas as pd

from judge.rules import *
from py2neo import *

project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

graf = Graph(
            "http://127.0.0.1/:7474/",
            user="neo4j",
            password="156372"
        )

paras = []
paras_file = open(project_path + '\source\commands\paras.txt', 'r', encoding='utf-8')
for para in paras_file.readlines():
    paras.append(para.strip())

many2one = {}
with open(project_path + '\source\commands\many2one.json', 'r', encoding='utf-8') as many2one_file:
    for line in many2one_file.readlines():
        x = json.loads(line)
        many2one.update(x)

low_commands_single = []
mid_commands_single = []
high_commands_single = []
with open(project_path + '\source\commands\low.txt', 'r', encoding='utf-8') as low_commands_file:
    low_commands_single = low_commands_file.readlines()
with open(project_path + '\source\commands\mid.txt', 'r', encoding='utf-8') as mid_commands_file:
    mid_commands_single = mid_commands_file.readlines()
with open(project_path + '\source\commands\high.txt', 'r', encoding='utf-8') as high_commands_file:
    high_commands_single = high_commands_file.readlines()
for i in range(len(low_commands_single)):
    low_commands_single[i] = low_commands_single[i].strip()
for i in range(len(mid_commands_single)):
    mid_commands_single[i] = mid_commands_single[i].strip()
for i in range(len(high_commands_single)):
    high_commands_single[i] = high_commands_single[i].strip()

low_commands_multiple = []
mid_commands_multiple = []
high_commands_multiple = []
need_oper_commands_multiple = []
with open(project_path + '\source\commands\low_tupe.txt', 'r', encoding='utf-8') as low_commands_file:
    low_commands_multiple = low_commands_file.readlines()
with open(project_path + '\source\commands\mid_tupe.txt', 'r', encoding='utf-8') as mid_commands_file:
    mid_commands_multiple = mid_commands_file.readlines()
with open(project_path + '\source\commands\high_tupe.txt', 'r', encoding='utf-8') as high_commands_file:
    high_commands_multiple = high_commands_file.readlines()
with open(project_path + '\source\commands\\need_oper_tupe.txt', 'r', encoding='utf-8') as need_oper_commands_file:
    need_oper_commands_multiple = need_oper_commands_file.readlines()
for i in range(len(low_commands_multiple)):
    low_commands_multiple[i] = low_commands_multiple[i].strip()
for i in range(len(mid_commands_multiple)):
    mid_commands_multiple[i] = mid_commands_multiple[i].strip()
for i in range(len(high_commands_multiple)):
    high_commands_multiple[i] = high_commands_multiple[i].strip()
for i in range(len(need_oper_commands_multiple)):
    need_oper_commands_multiple[i] = need_oper_commands_multiple[i].strip()

low_tupes = []
mid_tupes = []
high_tupes = []


class JudgeCommand():

    def __init__(self):
        self.paras = paras
        self.rm_rule = RmRule()
        self.cp_rule = CpRule()
        self.mv_rule = MvRule()
        self.kill_rule = KillRule()
        self.vi_rule = ViRule()
        self.service_rule = ServiceRule()
        self.systemctl_rule = SystemctlRule()
        self.mysql_rule = MysqlRule()
        self.yum_rule = YumRule()
        self.rpm_rule = RpmRule()
        self.iptables_rule = IptablesRule()
        self.date_rule = DateRule()
        self.ethtool_rule = EthtoolRule()
        self.ip_rule = IpRule()
        self.chkconfig_rule = ChkconfigRule()
        self.crontab_rule = CrontabRule()
        self.hostnamectl_rule = HostnamectlRule()
        pass

    def format_path(self, base_path, result_dict):
        # ???????????? path: ???????????????name???name1/name2???./name???../name    ???????????????

        # ????????????????????????????????????????????????????????????????????????
        # ??????????????????????????????????????????
        # ????????????*???
        if base_path != '' and base_path != '/':
            transfor_paths = []
            for i, path in enumerate(result_dict['obje']):
                if base_path not in path:
                    # ???????????????
                    if './' == path[:2]:
                        transfor_paths.append(path.replace('./', base_path))
                    elif '../' in path:
                        num = 0
                        for name in path.split('/'):
                            if name=='..':
                                num+=1
                        m = '/'.join(base_path.split('/')[:-num-1])
                        n = '/'.join(path.split('/')[num:])
                        transfor_paths.append('/'.join(base_path.split('/')[:-num-1]) + '/' + '/'.join(path.split('/')[num:]))
                    else:
                        transfor_paths.append(base_path+path)
                    pass
            result_dict['obje'] = transfor_paths
            transfor_paths = []
            for path in result_dict['obje']:
                if '*' in path:
                    # ????????????????????????*
                    base_path = '/'.join(path.split('/')[:-1]) + '/'
                    sql1 = 'match (m:folder{path:\'' + base_path + '\'})-[]->(n:folder) return n'
                    sql2 = 'match (m:folder{path:\'' + base_path + '\'})-[]->(n:file) return n'
                    nodes = graf.run(sql1).data()
                    nodes.extend(graf.run(sql2).data())
                    for node in nodes:
                        m = path.split('/')[-1][:-1]
                        n = node['n']['name']
                        if path.split('/')[-1][:-1] in node['n']['name']:
                            transfor_paths.append(node['n']['path'])
                else:
                    transfor_paths.append(path)
            result_dict['obje'] = transfor_paths
        pass

    def reformat_command(self, command):
        # ???????????????????????????????????????????????????????????????
        command = command.replace('\'', '\' ').replace('\"', '\" ').replace('|', '| ')
        return command
        pass

    def get_sub_command(self, command, cs):
        result_dict = {
            'oper': '',
            'para': [],
            'obje': []
        }
        many_oper = ''
        # ????????????????????????????????????
        num = 0
        sub_command = command.split()
        # ??????oper
        for index in range(len(sub_command)):
            if sub_command[index] in cs or '/bin/' + sub_command[index] in cs or './bin/' + sub_command[index] + '.sh' in cs:
                if index+1 < len(sub_command) and sub_command[index+1] in cs:
                    many_oper = sub_command[index] + ' ' + sub_command[index+1]
                    result_dict['oper'] = many2one[many_oper]
                else:
                    result_dict['oper'] = sub_command[index]
                num+=1
        # ??????????????????oper
        for c in many_oper.split():
            sub_command.remove(c)
        if many_oper == '':
            sub_command.remove(result_dict['oper'])
        if num==0:
            return {'????????????': '?????????????????????'}
        # ??????para
        for sub in sub_command:
            if '-'==sub[0] or '+'==sub[0]:
                result_dict['para'].append(sub)
            elif sub in self.paras:
                result_dict['para'].append(sub)
        for c in result_dict['para']:
            sub_command.remove(c)
        # ??????obje
        # ?????????????????????????????????????????????????????????????????????*
        # ????????????????????????oper????????????str????????????
        for sub in sub_command:
            if '\'' not in sub and '\"' not in sub:
                if '/' in sub or '*' in sub:
                    result_dict['obje'].append(sub)
                elif graf.run('match (n:folder{name:\'' + sub + '\'}) return n').data() != [] or graf.run(
                        'match (n:file{name:\'' + sub + '\'}) return n').data() != []:
                    result_dict['obje'].append(sub)
        if len(result_dict['obje']) == 0:
            for sub in sub_command:
                result_dict['obje'].append(sub)
        return result_dict
        pass

    def exec_command(self, command, cs):
        opers = []
        commands = []
        if 'xargs' in command:
            command = command.replace('xargs ', '')
        if '-exec' in command:
            commands = command.split('-exec')
        if '|' in command:
            commands = command.split('|')
        for command in commands:
            opers.append(self.get_sub_command(command, cs)['oper'])
        return opers, commands[0], self.get_sub_command(commands[1], cs)
        pass

    def judge_result_by_oper_obje(self, result_dict):
        if result_dict['oper'] in low_commands_single:
            return {'????????????':['????????????-???', 'green'], '????????????': ['??????-?????????', 'green']}
        elif result_dict['oper'] in mid_commands_single:
            return {'????????????':['????????????-???', 'yellow'], '????????????': ['??????-?????????', 'yellow']}
        elif result_dict['oper'] in high_commands_single:
            return {'????????????':['????????????-???', 'red'], '????????????': ['??????-?????????', 'red']}
        elif result_dict['oper'] == 'rm':
            return self.rm_rule.get_grade(result_dict)
        elif result_dict['oper'] == 'cp':
            return self.cp_rule.get_grade(result_dict)
        elif result_dict['oper'] == 'mv':
            return self.mv_rule.get_grade(result_dict)
        elif result_dict['oper'] == 'kill': # ???????????????????????????
            return self.kill_rule.get_grade(result_dict)
        elif result_dict['oper'] == 'vi' or result_dict['oper'] == 'vim': # ????????????????????????????????????????????????????????????????????????????????????????????????
            return self.vi_rule.get_grade(result_dict)
        elif result_dict['oper'] == 'service':
            return self.service_rule.get_grade(result_dict)
        elif result_dict['oper'] == 'systemctl':
            return self.service_rule.get_grade(result_dict)
        elif result_dict['oper'] == 'sed':
            return
        elif result_dict['oper'] == 'mysql':
            return self.mysql_rule.get_grade(result_dict)
        elif result_dict['oper'] == 'yum':
            return self.yum_rule.get_grade(result_dict)
        elif result_dict['oper'] == 'rpm':
            return self.rpm_rule.get_grade(result_dict)
        elif result_dict['oper'] == 'iptables':
            return self.iptables_rule.get_grade(result_dict)
        elif result_dict['oper'] == 'date':
            return self.date_rule.get_grade(result_dict)
        elif result_dict['oper'] == 'ethtool':
            return self.ethtool_rule.get_grade(result_dict)
        elif result_dict['oper'] == 'ip':
            return self.ip_rule.get_grade(result_dict)
        elif result_dict['oper'] == 'chkconfig':
            return self.chkconfig_rule.get_grade(result_dict)
        elif result_dict['oper'] == 'crontab':
            return self.crontab_rule.get_grade(result_dict)
        elif result_dict['oper'] == 'hostnamectl':
            return self.hostnamectl_rule.get_grade(result_dict)
        return {'error': 'error in judge_result_by_oper_obje()'}
        pass

    def get_result(self, command, cs, base_path = ''):
        if command==None:
            return {'????????????':['????????????????????????', 'yellow']}
        # ????????????????????????????????????????????????
        command = self.reformat_command(command)
        # ???????????????????????????????????????
        if '|' not in command.split() and '-exec' not in command.split():
            result_dict = self.get_sub_command(command, cs)
            self.format_path(base_path, result_dict)
            return self.judge_result_by_oper_obje(result_dict)
        else:
            opers, first_command, second_result_dict = self.exec_command(command, cs)
            self.format_path(base_path, second_result_dict)
            # ???????????????oper????????????????????????????????????????????????????????????
            flag = True
            for o in opers[1:]:
                if o not in low_commands_single:
                    flag = False
            if flag:
                return self.get_result(first_command, cs, base_path=base_path).update({'???????????????????????????': ['???', 'green']})
            # ??????????????????????????????????????????
            # opers???????????????????????????????????????
            elif ' '.join(opers) in low_commands_multiple:
                return {'????????????':['????????????-???', 'green'], '????????????': ['??????-?????????', 'green']}
            # opers???????????????????????????????????????
            elif ' '.join(opers) in mid_commands_multiple:
                return {'????????????':['????????????-???', 'yellow'], '????????????': ['??????-?????????', 'yellow']}
            # opers???????????????????????????????????????
            elif ' '.join(opers) in high_commands_multiple:
                return {'????????????':['????????????-???', 'red'], '????????????': ['??????-?????????', 'red']}
            # ?????????????????????????????????????????????????????????????????????????????????????????????
            elif ' '.join(opers) in need_oper_commands_multiple or '{}' in command:
                # ?????????????????????????????????????????????
                # find rm {}
                first_command_result = subprocess.getstatusoutput(first_command)[1].split('\n')
                second_result_dict['obje'] = first_command_result
                self.format_path(base_path, second_result_dict)
                return self.judge_result_by_oper_obje(second_result_dict)
            else:
                return {'????????????':['?????????????????????', 'yellow']}



def get_commands(base_path):
    commands_file_path = os.path.join(base_path, 'oper.txt')
    save_path = os.path.join(base_path, 'oper.csv')
    cs = []
    ts = []
    commands_file = open(commands_file_path, 'r', encoding='utf-8')
    for line in commands_file.readlines():
        command, times = line.split()[:2]
        command = str(command[2:-2])
        tag = 1
        if command not in cs:
            cs.append(command)
            ts.append(tag)
    data_frame = pd.DataFrame({'command': cs, 'times': ts})
    data_frame.to_csv(save_path, index=False, sep=',')
    return cs
    pass


def get_commands_from_xlsx(path):
    commands = []
    pd_xlsx = pd.read_excel(path, sheet_name='Sheet1', header=1)
    for c in pd_xlsx.values.tolist():
        commands.append(c[0])
    return commands
    pass


if __name__ == '__main__':
    cs = get_commands(base_path=project_path + '\source\commands')
    base_path = '/var/log/'
    command = 'rm -i ./vmware-network*'
    judge_command = JudgeCommand()
    print(judge_command.get_result(command, cs, base_path))
