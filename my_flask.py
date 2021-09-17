# coding:UTF-8
# author    :Just_silent
# init time :2021/7/8 11:37
# file      :my_flask.py
# IDE       :PyCharm

import os
from flask import Flask, render_template, request

from judge.main import *

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False


@app.route("/", methods=["GET", "POST"])
def hello():
    path = request.values.get('path')
    command = request.values.get('command')
    result = {}
    if command is not '' and command is not None:
        result, command_dict = get_result(path, command)
        if command_dict['command'] != []:
            result.update(command_dict)
        else:
            result.update({'command': [command]})
    else:
        result['command'] = '命令输入不能为空'
        result['危险等级'] = ['-', 'yellow']

    return render_template('main.html', result=result)

if __name__ == "__main__":
    app.run()