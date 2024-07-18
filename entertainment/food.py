# -*- coding: utf-8 -*-
import concurrent.futures

import requests
import io
from bs4 import BeautifulSoup as BS
import time
import re

from entertainment import get_city_num

headers = {
    "Origin": "https://piao.ctrip.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
}

def build_url(base, places, placenames):
    requestlist = []
    # 构建请求列表
    for j in range(len(places)):
        requestlist.append({"url": base + places[j] + ".html", "place": placenames[j]})
        for i in range(1, 1):  # 只爬取第2页的数据，如果需要爬取更多页，请调整这里的范围
            tmp = base + places[j] + "/s0-p" + str(i) + ".html"
            requestlist.append({"url": tmp, "place": placenames[j]})
    # 计算执行时间
    return requestlist


def request_url(req):
    # https: // you.ctrip.com / fooditem / wuhan145.html
    response = requests.get(req["url"], headers=headers)
    html = response.text
    soup = BS(html, 'html.parser')
    vs = soup.find_all(name="div", attrs={"class": "rdetailbox"})
    return vs


def scrape_food_items(places, placenames, scope):
    base = "https://you.ctrip.com/fooditem/"
    base2 = "https://you.ctrip.com"
    requestlist = []
    result_list = []

    requestlist = build_url(base, places, placenames)
    # [{'place': '武汉', 'url': 'https://you.ctrip.com/fooditem/wuhan145.html'}]

    # 发送请求并解析数据
    for req in requestlist:
        try:
            vs = request_url(req)
            size = min(len(vs), scope)
            print("size: " + str(size))
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # 创建一个并发任务列表
                futures = [executor.submit(process_item, vs[j], req, base2) for j in range(size)]

                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    if result is not None:
                        result_list.append(result)
                    # 控制请求频率，避免被网站反爬虫策略限制
                    time.sleep(0.2)

        except Exception as e:
            print(f"Error fetching URL: {req['url']}, {e}")
            continue
    ret = {
        "data": result_list,
        "count": len(result_list),
    }
    return ret


def process_item(v, req, base2):

    try:
            href = v.find(name="a", attrs={"target": "_blank"}).attrs["href"]
            print("food item")
            print(base2 + href)
            res = requests.get(base2 + href, headers=headers)
            soupi = BS(res.text, "html.parser")
            li = soupi.find(name="div", attrs={"class": "f_restaurant_list"}).find(name="li")
            addr = li.find(name="p", attrs={"class": "ellipsis"}).text
            if "地址：" in addr:
                addr = addr.replace("地址：", "")
            store = li.find(name="span", attrs={"class": "ellipsis"}).text
            name = soupi.find_all(name="li", attrs={"class": "title ellipsis"})
            introduce = soupi.find_all(name="li", attrs={"class": "infotext"})
            imglinks = soupi.find_all(name="a", attrs={"href": "javascript:void(0)"})
            img = imglinks[0].find_all(name="img")[0].attrs["src"]
            imgs = [img]
            tmp = {}
            tmp["name"] = name[0].get_text()
            tmp["introduce"] = introduce[0].get_text()
            tmp["imgs"] = imgs
            tmp["imgCount"] = len(imgs)
            tmp["city"] = req["place"]
            tmp["address"] = addr
            tmp["store"] = store
            return tmp
    except Exception as e:
        print(f"Error processing item: {e}")
        return None

# 示例用法
if __name__ == "__main__":
    start_time = time.time()
    city = "佛山"
    place = get_city_num(city)
    places = [place]  # 例如，选择一个地点
    placenames = [city]  # 对应地点的名称

    food_items = scrape_food_items(places, placenames, 2)
    for item in food_items:
        print(item)
    end_time = time.time()
    # 计算执行时间
    execution_time_ms = (end_time - start_time) * 1000
    print(f"程序执行时间（毫秒）: {execution_time_ms} ms")
