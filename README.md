### 安装环境
```
pip install -r ./requirements.txt
pip install py2neo==4.3.0
pip install flask
```
### 代码运行
```
1. 运行 dir_tree.py
2. 运行 reformat_file.py
```
### 目录结构
```
centos7                         项目
└── judge                       危险等级判断
    ├── main.py                 判断主函数
    ├── methods.py              判断方法流
    ├── rules.py                具体的规则
    neo4j_file                  
    ├── file_node.csv           文件节点（不可用）
    ├── fol2fi_rel.csv          文件夹-文件
    ├── fol2fol_rel.csv         文件夹-文件夹
    ├── folder_node.csv         文件夹节点（不可用）
    new_neo4j_file
    ├── file_node.csv           文件节点（可用）
    ├── folder_node.csv         文件夹节点（可用）
    source
    ├── commands                    规则命令
    |       ├── low.txt             低风险-无管道
    |       ├── mid.txt             中风险-无管道
    |       ├── high.txt            高风险-无管道
    |       ├── low_tupe.txt        低风险-管道
    |       ├── mid_tupe.txt        中风险-管道
    |       ├── high_tupe.txt       高风险-管道
    |       ├── many2one.json       命令组合->单命令
    |       ├── need_oper_tupe.txt  管道命令组合
    |       ├── oper.csv            命令集合
    |       ├── oper.txt            命令集合
    |       └── paras.txt           参数集合
    |
    ├── templates
    |       ├── main.html           前段界面
    |       └── test.html           前段界面
    ├──dir_tree.py              获取系统目录
    ├──my_flask.py              前段测试
    ├──reformat_file.py         修改节点信息
    └── requirements.txt        安装包
```