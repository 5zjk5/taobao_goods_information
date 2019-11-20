# -*- coding:utf-8 -*-
# import json
import requests
import re
import csv
import time


def getHTMLText(url):  # 读取页面
    # noinspection PyBroadException
    try:
        # Cookies的设置☆☆☆☆☆
        # Cookies的设置☆☆☆☆☆
        cookies = "miid=210889371187197889; thw=cn; cna=1Oq8FP/MeDcCAbfGVS/u5fXs; hng=CN%7Czh-CN%7CCNY%7C156; t=d268befdce3c2bc21e991678dd859810; uc3=vt3=F8dBy3kawzNBGJ2neq4%3D&id2=UojVcsjf4gtMcQ%3D%3D&nk2=saL09X%2FKpQ%3D%3D&lg2=V32FPkk%2Fw0dUvg%3D%3D; tracknick=%5Cu591C%5Cu732B_%5Cu4E36; lgc=%5Cu591C%5Cu732B_%5Cu4E36; _cc_=UIHiLt3xSw%3D%3D; tg=0; enc=w7bniI67yiS8q4MKbtdqjWBcP6x54S0N%2BG47f4jqIDLiCZ8M5b1NP5Vl1hV7Ex816hR%2FOZyuwZz4MU4Wc9Xd2A%3D%3D; x=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0%26__ll%3D-1%26_ato%3D0; mt=ci=-1_0; v=0; cookie2=1dec05f10e41750b0ede3ae3055ba86d; _tb_token_=f056ae8137565; alitrackid=www.taobao.com; lastalitrackid=www.taobao.com; swfstore=19027; JSESSIONID=7DB994CF34EC54BD6407833C05A303B8; uc1=cookie14=UoTaG70NVpbZdg%3D%3D; l=cBNXH4gmv8ebbJrDBOfZquI8LG7OqIOb4oVzw4OGXICPOuCHJcYFWZnBi-YMCnGVp6CMJ3SgKvQUBeYBqCmWfdW22j-la; isg=BICAfZxgyW5YA7SgEKakY2eqUQ6SoWW40BlDSvoQGRsudSCfoxmgY0dPjZ0QQRyr"
        jar = requests.cookies.RequestsCookieJar()
        for cookie in cookies.split(';'):
            key, value = cookie.split('=', 1)
            jar.set(key, value)
        # print(jar)
        # Cookies的设置☆☆☆☆☆
        # Cookies的设置☆☆☆☆☆
        hd = {'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"}
        r = requests.get(url, headers=hd, cookies=jar, timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except Exception:
        print("'getHtmlText'中出现错误")


def parsePage(ilt, html):  # 解析页面，存入列表
    # noinspection PyBroadException
    try:
        recomp_price = re.compile(r'\"view_price\"\:\"[\d\.]*\"')
        price = recomp_price.findall(html)
        recomp_name = re.compile(r'\"raw_title\"\:\".*?\"')
        name = recomp_name.findall(html)
        recomp_loc = re.compile(r'\"item_loc\"\:\".*?\"')
        location = recomp_loc.findall(html)
        recomp_sol = re.compile(r'\"view_sales\"\:\".*?\"')
        sale_solution = recomp_sol.findall(html)
        recomp_store = re.compile(r'\"nick\"\:\".*?\"')
        store_name = recomp_store.findall(html)
        # print(len(price))
        # for i in range(len(price)):
        #     print(eval(price[i].split(':')[1]))  此处发现错误 eval少加括号！
        for i in range(len(price)):
            price1 = eval((price[i]).split(':')[1])
            name1 = eval((name[i]).split(':')[1])
            location1 = eval((location[i]).split(':')[1])
            sale_solution1 = eval((sale_solution[i]).split(':')[1])
            store_name1 = eval((store_name[i]).split(':')[1])
            ilt.append([name1, price1, location1, sale_solution1, store_name1])
    except Exception:
        print("parsePage'过程中出现错误，一般不影响结果，请忽略")


def printGoodsList(ilt):  # 输出结果
    tplt = "{0:{5}<4}\t{1:{5}^40}\t{2:^6}\t{3:{5}^8}\t{4:{5}^10}\t{6:{5}^15}"
    tplt1 = "{0:{5}<4}\t{1:{5}<40}\t{2:>6}\t{3:{5}>8}\t\t{4:{5}>10}\t{6:{5}^15}"
    print(tplt.format("序号", "商品名称", "价格", "商品所在地", "销售数据", chr(12288), "商家店铺名"))
    for i in range(len(ilt)):
        print(tplt1.format(i, ilt[i][0], ilt[i][1], ilt[i][2], ilt[i][3], chr(12288), ilt[i][4]))


def wfile(ilt):  # 写入文件
    s = 0
    file_name = input("请输入文件名称：\n")
    print('\n')
    with open('C:/GoodsSale/' + file_name + '.csv', 'w+', encoding='gbk') as f:
        writer = csv.writer(f, lineterminator='\n')  # 删除默认输出的空白行，因为csv的输出效果是行末是CR，然后是CRIF的换行符
        writer.writerow(["序号", "商品名称", "价格", "商品所在地", "销售数据", "商家店铺名"])
        for i in range(len(ilt)):
            # noinspection PyBroadException
            try:
                writer.writerow([str(i), ilt[i][0], ilt[i][1], ilt[i][2], ilt[i][3], ilt[i][4]])
            except Exception:
                print("由于获得的商品名称含有gbk等编码形式非法字符，写入操作出现了一些错误，因此您获得的商品信息可能不完整!")
                print('当前错误位于第'+str(i)+'条商品,名称为', ilt[i][0], '\n')
                s += 1
                continue
    print('The file has bean writen Successfully!')
    print('本次写入共缺失商品数:', str(s), '件。')
    print("The FilePosition is located at "+'C://GoodsSale/' + file_name + '.csv'+'\n')


def main():
    goods = input('输入您要查询的商品:\n')
    depth = int(input('输入查询页数:\n'))
    print('欢迎使用“欢呼熊”淘宝商品信息查询系统:')
    time.sleep(1)
    print('正在获取商品信息:>>>')
    print('操作完成后您将在屏幕上看到所得商品信息>>>')
    print('如需写入文件保存，请根据程序提示操作。')
    print('请注意，由于格式问题，请将获得的文件另存为xls等可编辑格式。')
    start_url = 'https://s.taobao.com/search?q=' + goods
    infoList = []
    for i in range(depth):
        print("\r正在解析第", i + 1, "页，共", depth, "页。")
        print("当前进度：", '%.2f' % (int(i)*100/depth), "%", end='')
        # noinspection PyBroadException
        try:
            url = start_url + '&s=' + str(44*i)
            html = getHTMLText(url)
            parsePage(infoList, html)
        except Exception:
            continue
    printGoodsList(infoList)
    wfile0 = input("\n是否写入文件到'C:/GoodsSale/'下？(Y/N)\n")
    if wfile0 == 'Y' or wfile0 == 'y':
        wfile(infoList)
    else:
        pass


if __name__ == '__main__':
    main()
    input('操作已完成，按任意键退出:)\n')
