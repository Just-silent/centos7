# coding:UTF-8
# author    :Just_silent
# init time :2021/7/8 17:04
# file      :get_operation_dict.py
# IDE       :PyCharm

# 实现无可视化界面
from selenium.webdriver.chrome.options import Options
# 实现规避检测
from selenium.webdriver import ChromeOptions

from selenium import webdriver

from lxml import etree

import json, time

from py2neo import Graph, Node, Relationship, NodeMatcher, RelationshipMatcher

class Reptile():
    def __init__(self):
        # 实现无可视化界面的操作
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        # 实现规避检测
        option = ChromeOptions()
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.browser = webdriver.Chrome(executable_path='chromedriver', options=chrome_options)
        self.graph = Graph(
            "http://114.116.247.159:7474/",
            user="neo4j",
            password="123456")
        self.inserted_file = open('./inserted.txt', 'a', encoding='UTF-8')
        self.nm = NodeMatcher(self.graph)
        self.rm = RelationshipMatcher(self.graph)
        self.ns = 0
        self.rs = 0
        pass


    def _get_one_page(self, event):
        # 可能存一个浏览器多窗口的问题，需要锁定一个新的句柄
        # current_window_handle = self.browser.current_window_handle
        # 搜索
        self.browser.find_element_by_xpath('//*[@id="search-wrapper"]/div/div[1]/input').send_keys(event)
        button = self.browser.find_element_by_xpath('//*[@id="search-wrapper"]/button')
        button.click()
        time.sleep(1)

        # 更新页面句柄
        # all_Handles = self.browser.window_handles
        # 如果新的pay_window句柄不是当前句柄，用switch_to_window方法切换
        # for pay_window in all_Handles:
        #     if pay_window != current_window_handle:
        #         self.browser.switch_to_window(pay_window)
        dic = {'event' : event}
        try:
            # 利用etree.HTML，将字符串转换为Element对象->Element对象具有xpath的方法
            reason = etree.HTML(str(self.browser.page_source)).xpath(
                '//*[@id="result"]/main[2]/div[1]/div/section[2]/div//text()')
            dic['reason'] = reason
        except BaseException:
            dic['reason'] = None
        try:
            result = etree.HTML(str(self.browser.page_source)).xpath(
                '//*[@id="result"]/main[2]/div[1]/div/section[3]/div//text()')
            dic['result'] = result
        except BaseException:
            dic['result'] = None
        # 清除搜索框内容
        self.browser.find_element_by_xpath('//*[@id="search-wrapper"]/div/div/input').clear()
        return dic
        pass


    def _import(self, node1, node2, label):
        n1 = self.nm.match('event', name=node1).first()
        n2 = self.nm.match('event', name=node2).first()
        if n1 is None:
            n1 = Node('event', name=node1)
            self.graph.create(n1)
            self.ns+=1
            print('node:{}，累计创建节点:{}'.format(node1, self.ns))
        if n2 is None:
            n2 = Node('event', name=node2)
            self.graph.create(n2)
            self.ns+=1
            print('node:{}，累计创建节点:{}'.format(node2, self.ns))
        rel = self.rm.match(nodes=[n1, n2], r_type=label).first()
        if rel is None:
            rel = Relationship(n1, label, n2)
            self.graph.create(rel)
            self.rs+=1
            print('{}-{}->{}，累计创建关系:{}'.format(node1, label, node2, self.rs))
        # 批量导入
        pass


    def _import_data(self, dic):
        event = dic['event']
        reasons = dic['reason']
        results = dic['result']
        if reasons is not None:
            for reason in reasons:
                self._import(event, reason, '是因为')
        if results is not None:
            for result in results:
                self._import(event, result, '导致')
        pass



    def get_data(self, url):
        self.browser.get(url)
        # 若元素未找到不立即返回错误，间隔重复查询，若查处限制还未找到，返回错误
        self.browser.implicitly_wait(2)
        input = ['新中国成立']
        inserted_event = []
        while len(input)!=0:
            inserted_event.append(input[0])
            dic = self._get_one_page(input[0])
            # print(json.dumps(dic, indent=4, ensure_ascii=False))
            input.pop(0)
            if dic['reason'] != None:
                for reason in dic['reason']:
                    if reason not in inserted_event:
                        input.append(reason)
            if dic['result'] != None:
                for result in dic['result']:
                    if result not in inserted_event:
                        input.append(result)
            self._import_data(dic)
        self.inserted_file.writelines([line+'\n' for line in inserted_event])
        self.inserted_file.close()
        print('完成以{}开始的递归爬虫，并导入neo4j'.format(inserted_event))
        pass


if __name__ == '__main__':
    url = 'https://wangchujiang.com/linux-command/hot.html'
    reptile = Reptile()
    reptile.get_data(url)
