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
    登陆
    :param username:
    :param pwd:
    :param url:
    :return:
    """
    # 实例化浏览器，并显示浏览器，防止被识别的参数
    broswer = await launch(headless=False, args=['--disable-infobars'])
    # 打开新窗口
    page = await broswer.newPage()
    # 设置请求头
    await page.setUserAgent(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
    )
    # 跳转到登陆页面
    await page.goto(url)

    # 执行 js 防止被识别
    await page.evaluate(js1)
    await page.evaluate(js3)
    await page.evaluate(js4)
    await page.evaluate(js5)

    # 点击账号密码输入
    pwd_login = await page.querySelector('#J_Quick2Static')
    await pwd_login.click()
    # 点击微博输入
    weibo_login = await page.querySelector('.weibo-login')
    await weibo_login.click()
    await asyncio.sleep(1)

    # 写入账号密码
    await page.type('[name="username"]', username, {'delay': random.randint(100, 151) - 50})
    await page.type('[name="password"]', pwd, {'delay': random.randint(100, 151)})

    # 点击登陆后，会出现验证码
    login_btn = await page.querySelector('a.W_btn_g')
    await login_btn.click()

    # 等待验证码出现，输入验证码，点击登陆后验证码会缓冲 5 秒左右出现
    await asyncio.sleep(6)
    code = input('输入验证码：')

    # 提交验证码
    await page.type('[name="verifycode"]', code, {'delay': random.randint(100, 151) - 50})

    # 点击登陆
    login_btn = await page.querySelector('a.W_btn_g')
    await login_btn.click()

    await asyncio.sleep(3) # 等待页面跳转，调试时登录次数多了会有2,3次验证，就手动验证了，在这里打断点

    # 爬虫逻辑
    await spider(page,goods)


async def spider(page,goods):
    """
    爬虫逻辑
    :param broswer:
    :return:
    """
    # 输入搜索的商品，回车
    await page.type('#q', goods, {'delay': random.randint(100, 151) - 50})
    await page.keyboard.press('Enter')
    await asyncio.sleep(2)

    # 爬取前 100页。可根据具体情况设置
    for i in range(2,101):
        try: # 翻页失败跳过
            # 滚动条拉到最底下
            await page.evaluate('window.scrollBy(0, document.body.scrollHeight)')
            # 找到下一页按钮
            next_btn = await page.querySelector('a.J_Ajax.num.icon-tag')
            # 爬取数据
            await get_data(page)
            # 点击下一页
            await next_btn.click()
        except:
           pass


async def get_data(page):
    """获取数据"""
    # 获取网页源代码
    html = await page.content()
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
    for name, price, link in zip(names, prices, links):
        dic = {
            'name': name,
            'price': price,
            'link': link
        }
        await write_to_csv(dic,goods)


async def write_to_csv(dic,goods):
    """把商品信息写入 csv 文件"""
    f = open(goods + '.csv', 'a+', encoding='utf-8', newline='')  # 创建 csv
    writer = csv.writer(f)  # 写入的对象  ?
    name, price, link = dic['name'], dic['price'], dic['link']
    f.close()


def write_csv_header(goods):
    """写入 csv 的第一行头信息"""
    f = open(goods + '.csv', 'a+', encoding='utf-8', newline='')  # 创建 csv
    writer = csv.writer(f)  # 写入的对象
    writer.writerow(('name', 'price', 'link'))  # 写入header部分
    f.close()




if __name__ == '__main__':
    start_time = time.time()
    username = '13532287396'
    pwd = 'Zjkpython.'
    goods = '书包'  # input('输入商品名：')
    write_csv_header(goods) # 写入第一行
    url = 'https://login.taobao.com/member/login.jhtml?redirectURL=https%3A%2F%2Fs.taobao.com%2Fsearch%3Finitiative_id%3Dtbindexz_20170306%26ie%3Dutf8%26spm%3Da21bo.2017.201856-taobao-item.2%26sourceId%3Dtb.index%26search_type%3Ditem%26ssid%3Ds5-e%26commend%3Dall%26imgfile%3D%26q%3D%25E5%258C%2585%26suggest%3Dhistory_1%26_input_charset%3Dutf-8%26wq%3D%26suggest_query%3D%26source%3Dsuggest'
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(username, pwd, url,goods))
    end_time = time.time()
    print(end_time - start_time)
























