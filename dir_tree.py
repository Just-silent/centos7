# coding:UTF-8
# author    :Just_silent
# init time :2021/7/7 9:25
# file      :dir_tree.py
# IDE       :PyCharm

## 获得某个路径下所有文件夹与子文件的树形结构
import csv
import os, json
from reformat_file import rf_file
from py2neo import Graph, Node, Relationship, NodeMatcher, RelationshipMatcher, Subgraph


graf = Graph(
    "http://192.168.8.115/:7474/",
    user="neo4j",
    password="123456"
)

tree = {'centos7': '/'}
main_dir = ['boot', 'dev', 'proc', 'run', 'sys', 'etc', 'root', 'var', 'tmp', 'usr', 'bin', 'sbin', 'lib', 'lib64',
            'home', 'media', 'mnt', 'opt', 'srv']

k = 1
ids = [i for i in range(2, 1000000)]
file_node_file = open('./neo4j_file/file_node.csv', 'w', encoding='utf-8')
folder_node_file = open('./neo4j_file/folder_node.csv', 'w', encoding='utf-8')
fol2fol_rel_file = open('./neo4j_file/fol2fol_rel.csv', 'w', encoding='utf-8')
fol2fi_rel_file = open('./neo4j_file/fol2fi_rel.csv', 'w', encoding='utf-8')
file_node_writer = csv.writer(file_node_file, dialect = "excel")
folder_node_writer = csv.writer(folder_node_file, dialect = "excel")
fol2fol_rel_writer = csv.writer(fol2fol_rel_file, dialect = "excel")
fol2fi_rel_writer = csv.writer(fol2fi_rel_file, dialect = "excel")

# 完成节点属性->sql
# 字符错误
# 权限的设计
# id可以使用路径


def get_properties_sql(properties):
    properties_sql = '{'
    for k in zip(properties):
        properties_sql += k[0] + ':\'' + str(properties[k[0]]) + '\','
    properties_sql = properties_sql[:-1] + '}'
    return properties_sql
    pass

def replace_char(s):
    return s.replace('\\x', '****')

def back_char(s):
    return s.replace('xxxx', '\\x')

def get_father_power(filename):
    path = ''
    if filename[-1] == '/':
        ps = filename.split('/')[:-2]
        for p in ps:
            if p == '':
                path += '/'
            else:
                path += p
        if path != '/':
            path += '/'
    else:
        ps = filename.split('/')[:-2]
        for p in ps:
            if p == '':
                path += '/'
            else:
                path += p
        if path != '/':
            path += '/'
    w = int(os.access(path, os.W_OK))
    r = int(os.access(path, os.R_OK))
    x = int(os.access(path, os.X_OK))
    return [w, r, x]

def get_properties(path):
    result = {}
    try:
        if os.path.isdir(path):
            s = os.popen('ls -all {}'.format(path)).read().split('\n')[1].strip().split()
        else:
            s = os.popen('ls -all {}'.format(path[:-1])).read().strip().split()
        result['file_type'] = s[0][0]
        result['u1_rwx'] = s[0][1:4]
        result['u2_rwx'] = s[0][4:7]
        result['u3_rwx'] = s[0][7:10]
        result['change_ts'] = s[1]
        result['user_name'] = s[2]
        result['group_name'] = s[3]
        result['size'] = s[4]
        result['time'] = s[5:8]
        result['path'] = path
    except Exception:
        print('path error')
    return result

def check_node(properties):
    properties_sql = '{id:' + '\'' + str(properties['id']) + '\'' + '}'
    check_sql = 'match (n:{}{}) return n'.format(properties['kind'], properties_sql)
    if graf.run(check_sql).data()==[]:
        return False
    else:
        return True

def check_rel(fid, fkind, id, kind):
    id_sql = '{id:\'' + str(id) + '\'}'
    fid_sql = '{id:\'' + str(fid) + '\'}'
    check_sql = 'match (m:{}{})-[r:link]->(n:{}{}) return r'.format(fkind, fid_sql, kind, id_sql)
    if graf.run(check_sql).data()==[]:
        return False
    else:
        return True

def list_dir(tree, key, id, b_id):
    global k, ids, file_node_file, folder_node_file, fol2fol_rel_file, fol2fi_file
    if k % 100 == 0:
        print(k)
    k += 1
    sql = ''
    sub_tree = None
    # print(tree[key])
    # 创建属性sql
    properties = {  # folder or file
        'name': key,
        # urllib.parse.unquote(key.encode('unicode_escape').decode('utf-8').replace('\\x', '%')).replace('\ ', '\\')
        'kind': 'folder',
        'id': id,
        'path': replace_char(tree[key]),
        # urllib.parse.unquote(tree[key].encode('unicode_escape').decode('utf-8').replace('\\x', '%')).replace('\ ', '\\')
        'properties': get_properties(tree[key]),
    }
    if os.path.isdir(tree[key]):
        # 创建当前节点
        properties_sql = get_properties_sql(properties)
        # if not check_node(properties):
            # create_node_sql = 'create (n:{}{})'.format(properties['kind'], properties_sql)
            # graf.run(create_node_sql)
            # pass
        folder_node_writer.writerow([properties['name'], properties['kind'], properties['id'], properties['path'], properties['properties']])
        # 创建当前节点-父节点的关系
        flag = False
        if key == 'centos7':
            a=0
            # sql = 'match (n:' + properties['kind'] + '{id:\'' + str(id) + '\'}), ''(m:' + 'start' + '{id:\'' + str(
            #     b_id) + '\'}) create (m)-[:link]->(n)'
            # flag = check_rel(b_id, 'start', id, properties['kind'])
        else:
            # sql = 'match (n:' + properties['kind'] + '{id:\'' + str(id) + '\'}), ''(m:' + 'folder' + '{id:\'' + str(
            #     b_id) + '\'}) create (m)-[:link]->(n)'
            # flag = check_rel(b_id, 'folder', id, properties['kind'])
            fol2fol_rel_writer.writerow([b_id, id])
        # if not flag:
            # graf.run(sql)
        if not os.path.islink(tree[key][:-1]):
            sub_tree = {}
            try:
                for i in os.listdir(tree[key]):
                    if i not in sub_tree.keys():
                        sub_tree[i] = tree[key] + i + '/'
                tree[key] = sub_tree
                rtree = tree[key]
                for key in rtree.keys():
                    index = ids.pop(0)
                    list_dir(rtree, key, index, id)
            except Exception:
                print('isdir error')
        else:
            print('root in ..............', tree[key])
    else:
        # 创建当前节点
        properties['path'] = properties['path'][:-1]
        properties['kind'] = 'file'
        properties_sql = get_properties_sql(properties)
        # if not check_node(properties):
            # create_node_sql = 'create (n:{}{})'.format(properties['kind'], properties_sql)
            # graf.run(create_node_sql)
            # pass
        file_node_writer.writerow([properties['name'], properties['kind'], properties['id'], properties['path'], properties['properties']])
        # 创建当前节点-父节点的关系
        # if not check_rel(b_id, 'folder', id, properties['kind']):
            # sql = 'match (n:' + properties['kind'] + '{id:\'' + str(id) + '\'}), ''(m:' + 'folder' + '{id:\'' + str(
            # b_id) + '\'}) create (m)-[:link]->(n)'
            # graf.run(sql)
            # pass
        fol2fi_rel_writer.writerow([b_id, id])
    return (tree)


if __name__ == '__main__':
    sql = 'create (n:' + 'start' + '{name:\'' + 'start' + '\', id:\'' + str(0) + '\'})'
    # graf.run(sql)
    print(json.dumps(list_dir(tree, 'centos7', 1, 0), indent=4, sort_keys=True))
    files = ['./neo4j_file/file_node.csv', './neo4j_file/folder_node.csv']
    new_files = ['./new_neo4j_file/file_node.csv', './new_neo4j_file/folder_node.csv']
    for path, new_path in zip(files, new_files):
        rf_file(path, new_path)
