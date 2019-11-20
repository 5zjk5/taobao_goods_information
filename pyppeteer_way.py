# -*- coding: gb2312 -*-
import asyncio
from pyppeteer import launch
import time
import random
from exe_js import js1, js3, js4, js5
from lxml import etree
import csv


async def main(username,pwd,url,goods):
    """
    ��½
    :param username:
    :param pwd:
    :param url:
    :return:
    """
    # ʵ���������������ʾ���������ֹ��ʶ��Ĳ���
    broswer = await launch(headless=False, args=['--disable-infobars'])
    # ���´���
    page = await broswer.newPage()
    # ��������ͷ
    await page.setUserAgent(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
    )
    # ��ת����½ҳ��
    await page.goto(url)

    # ִ�� js ��ֹ��ʶ��
    await page.evaluate(js1)
    await page.evaluate(js3)
    await page.evaluate(js4)
    await page.evaluate(js5)

    # ����˺���������
    pwd_login = await page.querySelector('#J_Quick2Static')
    await pwd_login.click()
    # ���΢������
    weibo_login = await page.querySelector('.weibo-login')
    await weibo_login.click()
    await asyncio.sleep(1)

    # д���˺�����
    await page.type('[name="username"]', username, {'delay': random.randint(100, 151) - 50})
    await page.type('[name="password"]', pwd, {'delay': random.randint(100, 151)})

    # �����½�󣬻������֤��
    login_btn = await page.querySelector('a.W_btn_g')
    await login_btn.click()

    # �ȴ���֤����֣�������֤�룬�����½����֤��Ỻ�� 5 �����ҳ���
    await asyncio.sleep(6)
    code = input('������֤�룺')

    # �ύ��֤��
    await page.type('[name="verifycode"]', code, {'delay': random.randint(100, 151) - 50})

    # �����½
    login_btn = await page.querySelector('a.W_btn_g')
    await login_btn.click()

    await asyncio.sleep(3) # �ȴ�ҳ����ת������ʱ��¼�������˻���2,3����֤�����ֶ���֤�ˣ��������ϵ�

    # �����߼�
    await spider(page,goods)


async def spider(page,goods):
    """
    �����߼�
    :param broswer:
    :return:
    """
    # ������������Ʒ���س�
    await page.type('#q', goods, {'delay': random.randint(100, 151) - 50})
    await page.keyboard.press('Enter')
    await asyncio.sleep(2)

    # ��ȡǰ 100ҳ���ɸ��ݾ����������
    for i in range(2,101):
        try: # ��ҳʧ������
            # ���������������
            await page.evaluate('window.scrollBy(0, document.body.scrollHeight)')
            # �ҵ���һҳ��ť
            next_btn = await page.querySelector('a.J_Ajax.num.icon-tag')
            # ��ȡ����
            await get_data(page)
            # �����һҳ
            await next_btn.click()
        except:
           pass


async def get_data(page):
    """��ȡ����"""
    # ��ȡ��ҳԴ����
    html = await page.content()
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
    for name, price, link in zip(names, prices, links):
        dic = {
            'name': name,
            'price': price,
            'link': link
        }
        await write_to_csv(dic,goods)


async def write_to_csv(dic,goods):
    """����Ʒ��Ϣд�� csv �ļ�"""
    f = open(goods + '.csv', 'a+', encoding='utf-8', newline='')  # ���� csv
    writer = csv.writer(f)  # д��Ķ���  ?
    name, price, link = dic['name'], dic['price'], dic['link']
    f.close()


def write_csv_header(goods):
    """д�� csv �ĵ�һ��ͷ��Ϣ"""
    f = open(goods + '.csv', 'a+', encoding='utf-8', newline='')  # ���� csv
    writer = csv.writer(f)  # д��Ķ���
    writer.writerow(('name', 'price', 'link'))  # д��header����
    f.close()




if __name__ == '__main__':
    start_time = time.time()
    username = '13532287396'
    pwd = 'Zjkpython.'
    goods = '���'  # input('������Ʒ����')
    write_csv_header(goods) # д���һ��
    url = 'https://login.taobao.com/member/login.jhtml?redirectURL=https%3A%2F%2Fs.taobao.com%2Fsearch%3Finitiative_id%3Dtbindexz_20170306%26ie%3Dutf8%26spm%3Da21bo.2017.201856-taobao-item.2%26sourceId%3Dtb.index%26search_type%3Ditem%26ssid%3Ds5-e%26commend%3Dall%26imgfile%3D%26q%3D%25E5%258C%2585%26suggest%3Dhistory_1%26_input_charset%3Dutf-8%26wq%3D%26suggest_query%3D%26source%3Dsuggest'
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(username, pwd, url,goods))
    end_time = time.time()
    print(end_time - start_time)
























