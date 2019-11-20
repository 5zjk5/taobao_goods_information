# -*- coding: gb2312 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import etree
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import csv
import time


class Taobao_Spider:

    def __init__(self, username, password,goods):
        """初始化参数"""
        url = 'https://login.taobao.com/member/login.jhtml'
        self.url = url

        options = webdriver.ChromeOptions()

        # 设置为开发者模式，避免被识别
        options.add_experimental_option('excludeSwitches',
                                        ['enable-automation'])
        self.browser = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.browser, 10)
        # 初始化用户名
        self.username = username
        # 初始化密码
        self.password = password
        # 初始化想要的商品名
        self.goods = goods

    def run(self):
        """登陆接口"""
        self.browser.get(self.url)
        try:
            # 这里设置等待：等待输入框，因为先出现的可能是二维码登录，所以需要等【密码登录】选项出现
            #login_element = self.wait.until(
             #           EC.presence_of_element_located((By.CSS_SELECTOR, '.qrcode-login > .login-links > .forget-pwd')))
            #login_element.click()

            sina_login = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.weibo-login')))
            sina_login.click()

            weibo_user = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.username > .W_input')))
            weibo_user.send_keys(self.username)

            sina_password = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.password > .W_input')))
            sina_password.send_keys(self.password)

            submit = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.btn_tip > a > span')))
            submit.click()

            # 点击以后会出现验证码，等待验证码框出现，验证码提交
            WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'info_list')))
            code = input('输入验证码：')
            self.browser.find_element_by_xpath('//*[@id="pl_login_logged"]/div/div[4]/div/input').send_keys(code)

            # 再次点击登陆
            submit = self.browser.find_element_by_css_selector('.btn_tip > a > span')
            submit.click()

            taobao_name = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                                  '.site-nav-bd > ul.site-nav-bd-l > li#J_SiteNavLogin > div.site-nav-menu-hd > div.site-nav-user > a.site-nav-login-info-nick ')))
            # 登陆成功打印提示信息
            print("登陆成功：%s" % taobao_name.text)

            # 提取想要的数据
            self.find_goods(self.browser)
        except Exception as e:
            print("登陆失败,原因:\n",e)
        finally:
            self.browser.close()

    def find_goods(self,broswer):
        """搜索需要的商品"""
        # 找到输入框清空，递交商品名，点击确定
        broswer.find_element_by_xpath('//*[@id="q"]').send_keys(self.goods)
        broswer.find_element_by_xpath('//*[@id="J_TSearchForm"]/div[1]/button').click()

        # 决定提取多少页
        self.how_many_page(self.browser)

    def how_many_page(self,broswer):
        """决定想要多少页，就循环多少次"""
        for page in range(2,100): # 爬取 100 页，可根据具体情况设置
            # 每次跳转到新的一页等待页面加载完
            self.wait.until(EC.presence_of_element_located((By.ID,'q')))
            # 下拉滚动条到最下面
            for i in range(8):  # 下拉滚动条 8 次，拉到页码那里
                ActionChains(broswer).send_keys(Keys.PAGE_DOWN).perform()
            # 翻页失败的跳过
            try:
                page_box = broswer.find_element_by_xpath('//input[@class="input J_Input"]').clear()
                # 递交
                page_box = broswer.find_element_by_xpath('//input[@class="input J_Input"]').send_keys(page)
                # 翻页的确定按钮
                next_page_btn = broswer.find_element_by_xpath('//span[@class="btn J_Submit"]')

                # 提取这一页的商品信息
                self.get_info(broswer)
                # 点击 ’下一页‘ 继续爬取下一页数据
                next_page_btn.click()
            except:
                pass

    def get_info(self,broswer):
        """提取这一页的商品信息"""
        # 网页获取源代码
        html =  broswer.page_source
        html = etree.HTML(html)

        # 提取价格
        prices = html.xpath('//div[@class="price g_price g_price-highlight"]/strong/text()')
        # 提取链接
        links = html.xpath('//div[@class="row row-2 title"]/a/@href')
        # 提取名称
        names_target = html.xpath('//div[@class="row row-2 title"]/a')
        names = [name.xpath('string(.)').strip() for name in names_target]

        # 把每个商品以元字典放在一起，写入 csv
        dic = {}
        for name,price,link in zip(names,prices,links):
            dic = {
                'name' : name,
                'price' : price,
                'link' : link
            }
            self.write_to_csv(dic)

    def write_to_csv(self,dic):
        """把商品信息写入 csv 文件"""
        f = open(self.goods + '.csv','a+', encoding='utf-8',newline='')  # 创建 csv
        writer = csv.writer(f)  # 写入的对象  ?
        name,price,link = dic['name'],dic['price'],dic['link']
        writer.writerow((name,price,link))  # 写入数据
        f.close()

    def write_csv_header(self):
        """写入 csv 的第一行头信息"""
        f = open(self.goods + '.csv', 'w+', encoding='utf-8',newline='')  # 创建 csv
        writer = csv.writer(f)  # 写入的对象
        writer.writerow(('name','price','link'))  # 写入header部分
        f.close()


if __name__ == "__main__":
    start_time = time.time()
    username = 13532287396 #input("请输入你的微博用户名:")
    password = 'Zjkpython.' #input("请输入密码:")
    goods = '生日礼物女' #input('输入想要提取的商品名：')

    spider = Taobao_Spider(username, password,goods)

    # 先把 csv 文件头信息写入
    spider.write_csv_header()

    spider.run()
    end_time = time.time()
    print(end_time - start_time)













