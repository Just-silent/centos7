# coding:UTF-8
# author    :Just_silent
# init time :2021/7/28 15:56
# file      :rules.py
# IDE       :PyCharm

from py2neo import *

graf = Graph(
            "http://127.0.0.1/:7474/",
            user="neo4j",
            password="156372"
        )


class RmRule():

    def __init__(self):
        self.rule = {
            'hard_conditions': {
                'contents': ['boot', 'bin', 'run', 'dev', 'lib', 'media', 'opt', 'proc', 'lib', 'srv', 'sys', 'lib64', 'sbin'],
                'power': ['.rar' ,'.zip' ,'.txt' ,'.war' ,'log'],
            },
            'soft_conditions': {
                'sub_str': [],
                'owner' : '',
                'change_times': 1,
                'last_time': '',
            },
            'weights': {
                'w1': 0.6,
                'w2': 0.3,
                'w3': 0.1,
                'w4': 0.1,
            },
            'threshold': {
                'h1': 0.1,
                'h2': 0.5,
            },
        }
        self.show = {}
        pass

    def get_grade(self, command_dict):
        sql_result = None
        sql_file = 'match (n:file{path:\'' + command_dict['obje'][0] + '\'}) return n'
        sql_folder = 'match (n:folder{path:\'' + command_dict['obje'][0] + '\'}) return n'
        if graf.run(sql_file).data() != []:
            sql_result = graf.run(sql_file).data()[0]['n']
        else:
            sql_result = graf.run(sql_folder).data()[0]['n']
        name = sql_result['name']
        path = sql_result['path']
        u1_rwx = sql_result['u1_rwx']
        user_name = sql_result['user_name']
        change_ts = int(sql_result['change_ts'])
        time = sql_result['time']
        boot_path = sql_result['path'].split('/')[1]
        score = 0
        self.show = {
            '根目录': [boot_path, 'green'],
            '后缀': ['', 'yellow'],
            '名称': ['英文', 'yellow'],
            '创建者': [user_name, 'yellow'],
            '修改次数': [change_ts, 'yellow']
        }
        if boot_path in self.rule['hard_conditions']['contents'] or 'rwx' != graf.run('match (n:folder{path:\'' + '/'.join(sql_result['path'].split('/')[:-1])+ '/' + '\'}) return n').data()[0]['n']['u1_rwx']:
            self.show['根目录'][1] = 'red'
            print(self.show)
            self.show.update({'危险等级': ['危险等级-高', 'red']})
            return self.show
        else:
            for s in self.rule['hard_conditions']['power']:
                if s in path:
                    self.show['后缀'][0] = s
                    self.show['后缀'][1] = 'green'
                    score += 0.6
            for c in name:
                if u'\u4e00' <= c <= u'\u9fff':
                    self.show['名称'][0] = '中文'
                    self.show['名称'][1] = 'green'
                    if score == 0:
                        score += 0.6
            if user_name != 'root':
                self.show['创建者'][1] = 'green'
                score += 0.3
            if change_ts > 1:
                self.show['修改次数'][0] = change_ts
                self.show['修改次数'][1] = 'green'
                score += 0.1
            if self.rule['threshold']['h1'] >= score:
                print(self.show)
                self.show.update({'危险等级': ['危险等级-高', 'red']})
                return self.show
            elif self.rule['threshold']['h1'] < score and self.rule['threshold']['h2'] >= score:
                print(self.show)
                self.show.update({'危险等级': ['危险等级-中', 'yellow']})
                return self.show
            else:
                print(self.show)
                self.show.update({'危险等级': ['危险等级-低', 'green']})
                return self.show
        pass



class CpRule():

    def __init__(self):
        self.rule = {
            'hard_conditions': {
                'contents': ['boot', 'bin', 'run', 'dev', 'lib', 'media', 'opt', 'proc', 'lib', 'srv', 'sys', 'lib64', 'sbin'],
                'power': ['.rar' ,'.zip' ,'.txt' ,'.war' ,'log'],
            },
            'soft_conditions': {
                'sub_str': [],
                'owner' : '',
                'change_times': 1,
                'last_time': '',
            },
            'weights': {
                'w1': 0.6,
                'w2': 0.3,
                'w3': 0.1,
                'w4': 0.1,
            },
            'threshold':{
                'h1': 0.1,
                'h2': 0.5,
            },
        }
        self.show = {}
        pass

    def get_grade(self, command_dict):
        sql1_result = None
        sql1_file = 'match (n:file{path:\'' + command_dict['obje'][0] + '\'}) return n'
        sql1_folder = 'match (n:folder{path:\'' + command_dict['obje'][0] + '\'}) return n'
        sql2_result = None
        sql2_file = 'match (n:file{path:\'' + command_dict['obje'][-1] + '\'}) return n'
        sql2_folder = 'match (n:folder{path:\'' + command_dict['obje'][-1] + '\'}) return n'
        if graf.run(sql1_file).data() != []:
            sql1_result = graf.run(sql1_file).data()[0]['n']
        else:
            sql1_result = graf.run(sql1_folder).data()[0]['n']
        if graf.run(sql2_file).data() != []:
            sql2_result = graf.run(sql2_file).data()[0]['n']
        else:
            sql2_result = graf.run(sql2_folder).data()[0]['n']
        name1 = sql1_result['name']
        u1_rwx1 = sql1_result['u1_rwx']
        user_name1 = sql1_result['user_name']
        change_ts1 = int(sql1_result['change_ts'])
        time1 = sql1_result['time']
        name2 = sql2_result['name']
        u1_rwx2 = sql2_result['u1_rwx']
        user_name2 = sql2_result['user_name']
        change_ts2 = int(sql2_result['change_ts'])
        time2 = sql2_result['time']
        score = 0
        self.show = {
            '目标“写”权限': ['有', 'green'],
            '源文件“读”权限': ['有', 'green']
        }
        if 'r' in u1_rwx1 and 'w' in u1_rwx2:
            score += 0.6
        elif 'r' in u1_rwx1:
            self.show['目标“写”权限'] = ['无', 'red']
        elif 'w' in u1_rwx2:
            self.show['源文件“读”权限'] = ['无', 'red']
        if 0.6>score:
            print(self.show)
            self.show.update({'危险等级': ['危险等级：高', 'red']})
            return self.show
        else:
            print(self.show)
            self.show.update({'危险等级': ['危险等级：低', 'green']})
            return self.show
        pass



class MvRule():

    def __init__(self):
        self.rule = {
            'hard_conditions': {
                'contents': ['boot', 'bin', 'run', 'dev', 'lib', 'media', 'opt', 'proc', 'lib', 'srv', 'sys', 'lib64', 'sbin'],
                'power': ['.rar' ,'.zip' ,'.txt' ,'.war' ,'log'],
            },
            'soft_conditions': {
                'sub_str': [],
                'owner' : '',
                'change_times': 1,
                'last_time': '',
            },
            'weights': {
                'w1': 0.6,
                'w2': 0.3,
                'w3': 0.1,
                'w4': 0.1,
            },
            'threshold':{
                'h1': 0.1,
                'h2': 0.5,
            },
        }
        self.show = {}
        pass

    def get_grade(self, command_dict):
        is_exist = False
        sql1_result = None
        sql1_file = 'match (n:file{path:\'' + command_dict['obje'][0] + '\'}) return n'
        sql1_folder = 'match (n:folder{path:\'' + command_dict['obje'][0] + '\'}) return n'
        sql2_result = None
        sql2_file = 'match (n:file{path:\'' + command_dict['obje'][-1] + '\'}) return n'
        sql2_folder = 'match (n:folder{path:\'' + command_dict['obje'][-1] + '\'}) return n'
        if graf.run(sql1_file).data() != []:
            sql1_result = graf.run(sql1_file).data()[0]['n']
        else:
            sql1_result = graf.run(sql1_folder).data()[0]['n']
        if graf.run(sql2_file).data() != []:
            sql2_result = graf.run(sql2_file).data()[0]['n']
            is_exist = True
            self.show['是否存在文件覆盖'] = ['是', 'red']
            self.show.update({'危险等级': ['危险等级：高', 'red']})
            return self.show
        elif graf.run(sql2_folder).data() != []:
            sql2_result = graf.run(sql2_folder).data()[0]['n']
        else:
            sql2_result = None
        name1 = sql1_result['name']
        u1_rwx1 = sql1_result['u1_rwx']
        user_name1 = sql1_result['user_name']
        change_ts1 = int(sql1_result['change_ts'])
        time1 = sql1_result['time']
        name2 = sql2_result['name']
        u1_rwx2 = sql2_result['u1_rwx']
        user_name2 = sql2_result['user_name']
        change_ts2 = int(sql2_result['change_ts'])
        time2 = sql2_result['time']
        score = 0
        self.show = {
            '名称': ['英文', 'yellow'],
            '创建者': [user_name1, 'yellow'],
            '修改次数': [change_ts1, 'yellow'],
            '目标“写”权限': ['有', 'green'],
            '源文件“读”权限': ['有', 'green']
        }
        if 'r' in u1_rwx1 and 'w' in u1_rwx2:
            score += 0.6
        elif 'r' in u1_rwx1:
            self.show['目标“写”权限'] = ['无', 'red']
        elif 'w' in u1_rwx2:
            self.show['源文件“读”权限'] = ['无', 'red']
        for c in name1:
            if u'\u4e00' <= c <= u'\u9fff':
                self.show['名称'] = ['中文', 'green']
                if score == 0:
                    score += 0.6
        if user_name1 != 'root':
            self.show['创建者'] = [user_name1, 'green']
            score += 0.3
        if change_ts1 > 1:
            self.show['修改次数'] = [change_ts1, 'green']
            score += 0.1
        if self.rule['threshold']['h1'] >= score:
            self.show.update({'危险等级': ['危险等级：高', 'red']})
            return self.show
        elif self.rule['threshold']['h1'] < score and self.rule['threshold']['h2'] >= score:
            self.show.update({'危险等级': ['危险等级：中', 'yellow']})
            return self.show
        else:
            self.show.update({'危险等级': ['危险等级：低', 'green']})
            return self.show
        pass



class KillRule():

    def __init__(self):
        self.rule = {
            'hard_conditions': {
                'contents': ['boot', 'bin', 'run', 'dev', 'lib', 'media', 'opt', 'proc', 'lib', 'srv', 'sys', 'lib64', 'sbin'],
                'power': ['.rar' ,'.zip' ,'.txt' ,'.war' ,'log'],
            },
            'soft_conditions': {
                'sub_str': [],
                'owner' : '',
                'change_times': 1,
                'last_time': '',
            },
            'weights': {
                'w1': 0.6,
                'w2': 0.3,
                'w3': 0.1,
                'w4': 0.1,
            },
            'threshold':{
                'h1': 0.1,
                'h2': 0.5,
            },
        }
        self.show = {}
        pass

    def get_grade(self, command_dict):
        # 可以进一步区分等级
        return {'危险等级': ['危险等级：中', 'yellow']}
        pass



class ViRule():

    def __init__(self):
        self.rule = {
            'hard_conditions': {
                'contents': ['boot', 'bin', 'run', 'dev', 'lib', 'media', 'opt', 'proc', 'lib', 'srv', 'sys', 'lib64', 'sbin'],
                'power': ['.txt', '.sh', '.html', '.log', '.html', '.py', '.js', '.json', '.yml', 'properties'],
            },
            'soft_conditions': {
                'sub_str': [],
                'owner' : '',
                'change_times': 1,
                'last_time': '',
            },
            'weights': {
                'w1': 0.6,
                'w2': 0.3,
                'w3': 0.1,
                'w4': 0.1,
            },
            'threshold':{
                'h1': 0.1,
                'h2': 0.5,
            },
        }
        self.show = {}
        pass

    def get_grade(self, command_dict):
        sql_result = None
        sql_file = 'match (n:file{path:\'' + command_dict['obje'][0] + '\'}) return n'
        sql_folder = 'match (n:folder{path:\'' + command_dict['obje'][0] + '\'}) return n'
        if graf.run(sql_file).data() != []:
            sql_result = graf.run(sql_file).data()[0]['n']
        else:
            sql_result = graf.run(sql_folder).data()[0]['n']
        name = sql_result['name']
        path = sql_result['path']
        u1_rwx = sql_result['u1_rwx']
        user_name = sql_result['user_name']
        change_ts = int(sql_result['change_ts'])
        time = sql_result['time']
        boot_path = sql_result['path'].split('/')[1]
        score = 0
        self.show = {
            '根目录': [boot_path, 'green'],
            '后缀': ['', 'yellow'],
            '名称': ['英文', 'yellow'],
            '创建者': [user_name, 'yellow'],
            '修改次数': [change_ts, 'yellow']
        }
        if boot_path in self.rule['hard_conditions']['contents'] or 'rwx' != graf.run('match (n:folder{path:\'' + '/'.join(sql_result['path'].split('/')[:-1])+ '/' + '\'}) return n').data()[0]['n']['u1_rwx']:
            self.show['根目录'] = [boot_path, 'red']
            self.show.update({'危险等级': ['危险等级：高', 'red']})
            return self.show
        else:
            for s in self.rule['hard_conditions']['power']:
                if s in path:
                    self.show['后缀'] = [s, 'green']
                    score += 0.6
            for c in name:
                if u'\u4e00' <= c <= u'\u9fff':
                    self.show['后缀'] = ['中文', 'green']
                    if score == 0:
                        score += 0.6
            if user_name != 'root':
                self.show['创建者'][1] = 'green'
                score += 0.3
            if change_ts > 1:
                self.show['修改次数'][1] = 'green'
                score += 0.1
            if score <= self.rule['threshold']['h1']:
                self.show.update({'危险等级': ['危险等级：高', 'red']})
                return self.show
            elif score > self.rule['threshold']['h1'] and self.rule['threshold']['h2'] >= score:
                self.show.update({'危险等级': ['危险等级：中', 'yellow']})
                return self.show
            else:
                self.show.update({'危险等级': ['危险等级：低', 'green']})
                return self.show
        pass



class ServiceRule():

    def __init__(self):
        self.rule = {
            'hard_conditions': {
                'contents': ['boot', 'bin', 'run', 'dev', 'lib', 'media', 'opt', 'proc', 'lib', 'srv', 'sys', 'lib64', 'sbin'],
                'power': ['.txt', '.sh', '.html', '.log', '.html', '.py', '.js', '.json', '.yml', 'properties'],
            },
            'soft_conditions': {
                'sub_str': [],
                'owner' : '',
                'change_times': 1,
                'last_time': '',
            },
            'weights': {
                'w1': 0.6,
                'w2': 0.3,
                'w3': 0.1,
                'w4': 0.1,
            },
            'threshold':{
                'h1': 0.1,
                'h2': 0.5,
            },
        }
        self.show = {}
        pass

    def get_grade(self, command_dict):
        print(command_dict['para'])
        if 'stop' in command_dict['para'] or 'restart' in command_dict['para']:
            self.show['是否重启或停止服务'] = ['是', 'red']
            self.show.update({'危险等级': ['危险等级：高', 'red']})
            return self.show
        else:
            self.show['是否重启或停止服务'] = ['否', 'green']
            self.show.update({'危险等级': ['危险等级：低', 'green']})
            return self.show
        pass



class SystemctlRule():

    def __init__(self):
        self.rule = {
            'hard_conditions': {
                'contents': ['boot', 'bin', 'run', 'dev', 'lib', 'media', 'opt', 'proc', 'lib', 'srv', 'sys', 'lib64', 'sbin'],
                'power': ['.txt', '.sh', '.html', '.log', '.html', '.py', '.js', '.json', '.yml', 'properties'],
            },
            'soft_conditions': {
                'sub_str': [],
                'owner' : '',
                'change_times': 1,
                'last_time': '',
            },
            'weights': {
                'w1': 0.6,
                'w2': 0.3,
                'w3': 0.1,
                'w4': 0.1,
            },
            'threshold':{
                'h1': 0.1,
                'h2': 0.5,
            },
        }
        self.show = {}
        pass

    def get_grade(self, command_dict):
        print(command_dict['para'])
        if 'stop' in command_dict['para'] or 'restart' in command_dict['para']:
            self.show['是否重启或停止服务'] = ['是', 'red']
            self.show.update({'危险等级': ['危险等级：高', 'red']})
            return self.show
        else:
            self.show['是否重启或停止服务'] = ['否', 'green']
            self.show.update({'危险等级': ['危险等级：低', 'green']})
            return self.show
        pass



class MysqlRule():

    def __init__(self):
        self.rule = {
            'hard_conditions': {
                'contents': ['boot', 'bin', 'run', 'dev', 'lib', 'media', 'opt', 'proc', 'lib', 'srv', 'sys', 'lib64', 'sbin'],
                'power': ['.txt', '.sh', '.html', '.log', '.html', '.py', '.js', '.json', '.yml', 'properties'],
            },
            'soft_conditions': {
                'sub_str': [],
                'owner' : '',
                'change_times': 1,
                'last_time': '',
            },
            'weights': {
                'w1': 0.6,
                'w2': 0.3,
                'w3': 0.1,
                'w4': 0.1,
            },
            'threshold':{
                'h1': 0.1,
                'h2': 0.5,
            },
        }
        self.show = {}
        pass

    def get_grade(self, command_dict):
        if '-e' in command_dict['para']:
            self.show['是否执行内部命令'] = ['是', 'yellow']
            self.show.update({'危险等级': ['危险等级：中', 'yellow']})
            return self.show
        else:
            self.show['是否执行内部命令'] = ['否', 'green']
            self.show.update({'危险等级': ['危险等级：低', 'green']})
            return self.show
        pass



class YumRule():

    def __init__(self):
        self.rule = {
            'hard_conditions': {
                'contents': ['boot', 'bin', 'run', 'dev', 'lib', 'media', 'opt', 'proc', 'lib', 'srv', 'sys', 'lib64', 'sbin'],
                'power': ['.txt', '.sh', '.html', '.log', '.html', '.py', '.js', '.json', '.yml', 'properties'],
            },
            'soft_conditions': {
                'sub_str': [],
                'owner' : '',
                'change_times': 1,
                'last_time': '',
            },
            'weights': {
                'w1': 0.6,
                'w2': 0.3,
                'w3': 0.1,
                'w4': 0.1,
            },
            'threshold':{
                'h1': 0.1,
                'h2': 0.5,
            },
        }
        self.show = {}
        pass

    def get_grade(self, command_dict):
        if 'remove' in command_dict['para'] or 'groupremove' in command_dict['para']:
            self.show['是否删除软件包'] = ['是', 'red']
            self.show.update({'危险等级': ['危险等级：高', 'red']})
            return self.show
        else:
            self.show['是否删除软件包'] = ['否', 'green']
            self.show.update({'危险等级': ['危险等级：低', 'green']})
            return self.show
        pass



class RpmRule():

    def __init__(self):
        self.rule = {
            'hard_conditions': {
                'contents': ['boot', 'bin', 'run', 'dev', 'lib', 'media', 'opt', 'proc', 'lib', 'srv', 'sys', 'lib64', 'sbin'],
                'power': ['.txt', '.sh', '.html', '.log', '.html', '.py', '.js', '.json', '.yml', 'properties'],
            },
            'soft_conditions': {
                'sub_str': [],
                'owner' : '',
                'change_times': 1,
                'last_time': '',
            },
            'weights': {
                'w1': 0.6,
                'w2': 0.3,
                'w3': 0.1,
                'w4': 0.1,
            },
            'threshold':{
                'h1': 0.1,
                'h2': 0.5,
            },
        }
        self.show = {}
        pass

    def get_grade(self, command_dict):
        if '-e' in command_dict['para']:
            self.show['是否删除软件包'] = ['是', 'red']
            self.show.update({'危险等级': ['危险等级：高', 'red']})
            return self.show
        else:
            self.show['是否删除软件包'] = ['否', 'green']
            self.show.update({'危险等级': ['危险等级：低', 'green']})
            return self.show
        pass



class IptablesRule():

    def __init__(self):
        self.rule = {
            'hard_conditions': {
                'contents': ['boot', 'bin', 'run', 'dev', 'lib', 'media', 'opt', 'proc', 'lib', 'srv', 'sys', 'lib64', 'sbin'],
                'power': ['.txt', '.sh', '.html', '.log', '.html', '.py', '.js', '.json', '.yml', 'properties'],
            },
            'soft_conditions': {
                'sub_str': [],
                'owner' : '',
                'change_times': 1,
                'last_time': '',
            },
            'weights': {
                'w1': 0.6,
                'w2': 0.3,
                'w3': 0.1,
                'w4': 0.1,
            },
            'threshold':{
                'h1': 0.1,
                'h2': 0.5,
            },
        }
        self.show = {}
        pass

    # 开放IP：-A INPUT ... ACCEPT
    # 屏蔽IP：-A INPUT ... DROP
    # 开放/屏蔽IP段：-I INPUT ... ACCEPT/DROP
    def get_grade(self, command_dict):
        self.show = {
            '是否清空所有的防火墙规则': ['否', 'green'],
            '是否删除用户自定义的空链': ['否', 'green'],
            '是否清空计数': ['否', 'green'],
            '是否允许访问': ['否', 'green'],
            '是否禁用访问': ['否', 'green'],
        }
        for para in command_dict['para']:
            if para in ['-F', '-X', '-Z']:
                if para == '-F':
                    self.show['是否清空所有的防火墙规则'] = ['是', 'red']
                elif para == '-X':
                    self.show['是否删除用户自定义的空链'] = ['是', 'red']
                elif para == '-Z':
                    self.show['是否清空计数'] = ['是', 'red']
                self.show.update({'危险等级': ['危险等级：高', 'red']})
                return self.show
        for para in command_dict['para']:
            if para in ['ACCEPT', 'DROP']:
                if para == 'ACCEPT':
                    self.show['是否允许访问'] = ['是', 'red']
                elif para == 'DROP':
                    self.show['是否禁用访问'] = ['是', 'red']
                self.show.update({'危险等级': ['危险等级：中', 'yellow']})
                return self.show
        self.show.update({'危险等级': ['危险等级：低', 'green']})
        return self.show
        pass



class DateRule():

    def __init__(self):
        self.rule = {
            'hard_conditions': {
                'contents': ['boot', 'bin', 'run', 'dev', 'lib', 'media', 'opt', 'proc', 'lib', 'srv', 'sys', 'lib64', 'sbin'],
                'power': ['.txt', '.sh', '.html', '.log', '.html', '.py', '.js', '.json', '.yml', 'properties'],
            },
            'soft_conditions': {
                'sub_str': [],
                'owner' : '',
                'change_times': 1,
                'last_time': '',
            },
            'weights': {
                'w1': 0.6,
                'w2': 0.3,
                'w3': 0.1,
                'w4': 0.1,
            },
            'threshold':{
                'h1': 0.1,
                'h2': 0.5,
            },
        }
        self.show = {}
        pass
    # 修改系统时间
    def get_grade(self, command_dict):
        self.show['是否修改系统时间'] = ['否', 'green']
        if '-s' in command_dict['para']:
            self.show['是否修改系统时间'] = ['是', 'red']
            self.show.update({'危险等级': ['危险等级：高', 'red']})
            return self.show
        else:
            self.show.update({'危险等级': ['危险等级：低', 'green']})
            return self.show
        pass



class EthtoolRule():

    def __init__(self):
        self.rule = {
            'hard_conditions': {
                'contents': ['boot', 'bin', 'run', 'dev', 'lib', 'media', 'opt', 'proc', 'lib', 'srv', 'sys', 'lib64', 'sbin'],
                'power': ['.txt', '.sh', '.html', '.log', '.html', '.py', '.js', '.json', '.yml', 'properties'],
            },
            'soft_conditions': {
                'sub_str': [],
                'owner' : '',
                'change_times': 1,
                'last_time': '',
            },
            'weights': {
                'w1': 0.6,
                'w2': 0.3,
                'w3': 0.1,
                'w4': 0.1,
            },
            'threshold':{
                'h1': 0.1,
                'h2': 0.5,
            },
        }
        self.show = {}
        pass

    # 修改配置信息
    def get_grade(self, command_dict):
        self.show['是否修改网卡中接收模块RX、发送模块TX和Autonegotiate模块的状态'] = ['否', 'green']
        self.show['是否修改网卡EEPROM byte'] = ['否', 'green']
        self.show['是否修改网卡Offload参数的状态'] = ['否', 'green']
        self.show['是否修改网卡的网卡速度、单工/全双工模式、mac地址等配置'] = ['否', 'green']
        for para in command_dict['para']:
            if para in ['-A', '-E', '-K', '-s']:
                if para=='-A':
                    self.show['是否修改网卡中接收模块RX、发送模块TX和Autonegotiate模块的状态'] = ['是', 'red']
                elif para=='-E':
                    self.show['是否修改网卡EEPROM byte'] = ['是', 'red']
                elif para=='-K':
                    self.show['是否修改网卡Offload参数的状态'] = ['是', 'red']
                elif para=='-s':
                    self.show['是否修改网卡的网卡速度、单工/全双工模式、mac地址等配置'] = ['是', 'red']
                self.show.update({'危险等级': ['危险等级：高', 'red']})
                return self.show
        self.show.update({'危险等级': ['危险等级：低', 'green']})
        return self.show
        pass



class IpRule():

    def __init__(self):
        self.rule = {
            'hard_conditions': {
                'contents': ['boot', 'bin', 'run', 'dev', 'lib', 'media', 'opt', 'proc', 'lib', 'srv', 'sys', 'lib64', 'sbin'],
                'power': ['.txt', '.sh', '.html', '.log', '.html', '.py', '.js', '.json', '.yml', 'properties'],
            },
            'soft_conditions': {
                'sub_str': [],
                'owner' : '',
                'change_times': 1,
                'last_time': '',
            },
            'weights': {
                'w1': 0.6,
                'w2': 0.3,
                'w3': 0.1,
                'w4': 0.1,
            },
            'threshold':{
                'h1': 0.1,
                'h2': 0.5,
            },
        }
        self.show = {}
        pass

    # 修改配置信息
    def get_grade(self, command_dict):
        self.show['是否关闭网卡'] = ['否', 'green']
        self.show['是否关闭网卡的混合模式'] = ['否', 'green']
        self.show['是否删除网卡ip地址'] = ['否', 'green']
        for para in command_dict['para']:
            if para in ['down', 'offi', 'del']:
                if para=='down':
                    self.show['是否关闭网卡'] = ['是', 'red']
                elif para=='offi':
                    self.show['是否关闭网卡的混合模式'] = ['是', 'red']
                elif para=='del':
                    self.show['是否删除网卡ip地址'] = ['是', 'red']
                self.show.update({'危险等级': ['危险等级：高', 'red']})
                return self.show
        self.show.update({'危险等级': ['危险等级：低', 'green']})
        return self.show
        pass



class ChkconfigRule():

    def __init__(self):
        self.rule = {
            'hard_conditions': {
                'contents': ['boot', 'bin', 'run', 'dev', 'lib', 'media', 'opt', 'proc', 'lib', 'srv', 'sys', 'lib64', 'sbin'],
                'power': ['.txt', '.sh', '.html', '.log', '.html', '.py', '.js', '.json', '.yml', 'properties'],
            },
            'soft_conditions': {
                'sub_str': [],
                'owner' : '',
                'change_times': 1,
                'last_time': '',
            },
            'weights': {
                'w1': 0.6,
                'w2': 0.3,
                'w3': 0.1,
                'w4': 0.1,
            },
            'threshold':{
                'h1': 0.1,
                'h2': 0.5,
            },
        }
        self.show = {}
        pass

    # 修改配置信息
    def get_grade(self, command_dict):
        self.show['是否删除指定的系统服务'] = ['否', 'green']
        for para in command_dict['para']:
            if para in ['--del']:
                self.show['是否删除指定的系统服务'] = ['是', 'red']
                self.show.update({'危险等级': ['危险等级：高', 'red']})
                return self.show
        self.show.update({'危险等级': ['危险等级：低', 'green']})
        return self.show
        pass



class CrontabRule():

    def __init__(self):
        self.rule = {
            'hard_conditions': {
                'contents': ['boot', 'bin', 'run', 'dev', 'lib', 'media', 'opt', 'proc', 'lib', 'srv', 'sys', 'lib64', 'sbin'],
                'power': ['.txt', '.sh', '.html', '.log', '.html', '.py', '.js', '.json', '.yml', 'properties'],
            },
            'soft_conditions': {
                'sub_str': [],
                'owner' : '',
                'change_times': 1,
                'last_time': '',
            },
            'weights': {
                'w1': 0.6,
                'w2': 0.3,
                'w3': 0.1,
                'w4': 0.1,
            },
            'threshold':{
                'h1': 0.1,
                'h2': 0.5,
            },
        }
        self.show = {}
        pass

    # 中：编辑   高：删除
    def get_grade(self, command_dict):
        self.show['是否编辑定时任务文件'] = ['否', 'green']
        self.show['是否删除定时任务文件'] = ['否', 'green']
        for para in command_dict['para']:
            if para in ['-r']:
                self.show['是否删除定时任务文件'] = ['是', 'red']
                self.show.update({'危险等级': ['危险等级：高', 'red']})
                return self.show
            elif para in ['-e']:
                self.show['是否编辑定时任务文件'] = ['是', 'yellow']
                self.show.update({'危险等级': ['危险等级：中', 'yellow']})
                return self.show
        self.show.update({'危险等级': ['危险等级：低', 'green']})
        return self.show
        pass



class HostnamectlRule():

    def __init__(self):
        self.rule = {
            'hard_conditions': {
                'contents': ['boot', 'bin', 'run', 'dev', 'lib', 'media', 'opt', 'proc', 'lib', 'srv', 'sys', 'lib64', 'sbin'],
                'power': ['.txt', '.sh', '.html', '.log', '.html', '.py', '.js', '.json', '.yml', 'properties'],
            },
            'soft_conditions': {
                'sub_str': [],
                'owner' : '',
                'change_times': 1,
                'last_time': '',
            },
            'weights': {
                'w1': 0.6,
                'w2': 0.3,
                'w3': 0.1,
                'w4': 0.1,
            },
            'threshold':{
                'h1': 0.1,
                'h2': 0.5,
            },
        }
        self.show = {}
        pass

    # 中：设置
    def get_grade(self, command_dict):
        for para in command_dict['para']:
            if para in ['set']:
                self.show['是否更改主机信息'] = ['是', 'yellow']
                self.show.update({'危险等级': ['危险等级：中', 'yellow']})
                return self.show
        self.show.update({'危险等级': ['危险等级：低', 'green']})
        return self.show
        pass



def judge_by_opers(opers):
    if len(opers)==2:
        if opers[0]=='cat':
            return {'危险等级', ['危险等级：低', 'green']}
        elif opers[0]=='cat' and opers[1]=='rm':
            return {'危险等级', ['危险等级：高', 'red']}
        else:
            return {'危险等级', ['编辑中...', 'yellow']}
    return {'危险等级', ['编辑中...', 'yellow']}