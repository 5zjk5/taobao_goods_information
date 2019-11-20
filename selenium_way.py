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
        """��ʼ������"""
        url = 'https://login.taobao.com/member/login.jhtml'
        self.url = url

        options = webdriver.ChromeOptions()

        # ����Ϊ������ģʽ�����ⱻʶ��
        options.add_experimental_option('excludeSwitches',
                                        ['enable-automation'])
        self.browser = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.browser, 10)
        # ��ʼ���û���
        self.username = username
        # ��ʼ������
        self.password = password
        # ��ʼ����Ҫ����Ʒ��
        self.goods = goods

    def run(self):
        """��½�ӿ�"""
        self.browser.get(self.url)
        try:
            # �������õȴ����ȴ��������Ϊ�ȳ��ֵĿ����Ƕ�ά���¼��������Ҫ�ȡ������¼��ѡ�����
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

            # ����Ժ�������֤�룬�ȴ���֤�����֣���֤���ύ
            WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'info_list')))
            code = input('������֤�룺')
            self.browser.find_element_by_xpath('//*[@id="pl_login_logged"]/div/div[4]/div/input').send_keys(code)

            # �ٴε����½
            submit = self.browser.find_element_by_css_selector('.btn_tip > a > span')
            submit.click()

            taobao_name = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                                  '.site-nav-bd > ul.site-nav-bd-l > li#J_SiteNavLogin > div.site-nav-menu-hd > div.site-nav-user > a.site-nav-login-info-nick ')))
            # ��½�ɹ���ӡ��ʾ��Ϣ
            print("��½�ɹ���%s" % taobao_name.text)

            # ��ȡ��Ҫ������
            self.find_goods(self.browser)
        except Exception as e:
            print("��½ʧ��,ԭ��:\n",e)
        finally:
            self.browser.close()

    def find_goods(self,broswer):
        """������Ҫ����Ʒ"""
        # �ҵ��������գ��ݽ���Ʒ�������ȷ��
        broswer.find_element_by_xpath('//*[@id="q"]').send_keys(self.goods)
        broswer.find_element_by_xpath('//*[@id="J_TSearchForm"]/div[1]/button').click()

        # ������ȡ����ҳ
        self.how_many_page(self.browser)

    def how_many_page(self,broswer):
        """������Ҫ����ҳ����ѭ�����ٴ�"""
        for page in range(2,100): # ��ȡ 100 ҳ���ɸ��ݾ����������
            # ÿ����ת���µ�һҳ�ȴ�ҳ�������
            self.wait.until(EC.presence_of_element_located((By.ID,'q')))
            # ������������������
            for i in range(8):  # ���������� 8 �Σ�����ҳ������
                ActionChains(broswer).send_keys(Keys.PAGE_DOWN).perform()
            # ��ҳʧ�ܵ�����
            try:
                page_box = broswer.find_element_by_xpath('//input[@class="input J_Input"]').clear()
                # �ݽ�
                page_box = broswer.find_element_by_xpath('//input[@class="input J_Input"]').send_keys(page)
                # ��ҳ��ȷ����ť
                next_page_btn = broswer.find_element_by_xpath('//span[@class="btn J_Submit"]')

                # ��ȡ��һҳ����Ʒ��Ϣ
                self.get_info(broswer)
                # ��� ����һҳ�� ������ȡ��һҳ����
                next_page_btn.click()
            except:
                pass

    def get_info(self,broswer):
        """��ȡ��һҳ����Ʒ��Ϣ"""
        # ��ҳ��ȡԴ����
        html =  broswer.page_source
        html = etree.HTML(html)

        # ��ȡ�۸�
        prices = html.xpath('//div[@class="price g_price g_price-highlight"]/strong/text()')
        # ��ȡ����
        links = html.xpath('//div[@class="row row-2 title"]/a/@href')
        # ��ȡ����
        names_target = html.xpath('//div[@class="row row-2 title"]/a')
        names = [name.xpath('string(.)').strip() for name in names_target]

        # ��ÿ����Ʒ��Ԫ�ֵ����һ��д�� csv
        dic = {}
        for name,price,link in zip(names,prices,links):
            dic = {
                'name' : name,
                'price' : price,
                'link' : link
            }
            self.write_to_csv(dic)

    def write_to_csv(self,dic):
        """����Ʒ��Ϣд�� csv �ļ�"""
        f = open(self.goods + '.csv','a+', encoding='utf-8',newline='')  # ���� csv
        writer = csv.writer(f)  # д��Ķ���  ?
        name,price,link = dic['name'],dic['price'],dic['link']
        writer.writerow((name,price,link))  # д������
        f.close()

    def write_csv_header(self):
        """д�� csv �ĵ�һ��ͷ��Ϣ"""
        f = open(self.goods + '.csv', 'w+', encoding='utf-8',newline='')  # ���� csv
        writer = csv.writer(f)  # д��Ķ���
        writer.writerow(('name','price','link'))  # д��header����
        f.close()


if __name__ == "__main__":
    start_time = time.time()
    username = 13532287396 #input("���������΢���û���:")
    password = 'Zjkpython.' #input("����������:")
    goods = '��������Ů' #input('������Ҫ��ȡ����Ʒ����')

    spider = Taobao_Spider(username, password,goods)

    # �Ȱ� csv �ļ�ͷ��Ϣд��
    spider.write_csv_header()

    spider.run()
    end_time = time.time()
    print(end_time - start_time)













