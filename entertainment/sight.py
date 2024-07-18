# -*- coding: utf-8 -*-
import json

import requests
import io
from bs4 import BeautifulSoup as BS
import time
import re
import concurrent.futures

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
    print(requestlist[0])
    return requestlist


def request_url(req):
    # start_time = time.time()
    response = requests.get(req["url"], headers=headers)
    soup = BS(response.text, 'html.parser')
    vs = soup.find_all(name="div", attrs={"class": "titleModule_name__Li4Tv"})
    # class ="titleModule_name__Li4Tv" > < span > < a href="https://you.ctrip.com/sight/xiamen21/8625.html?scene=online" 厦门园林植物
    # end_time = time.time()
    # 计算执行时间
    # execution_time_ms = (end_time - start_time) * 1000
    # print("request_url time:")
    # print(execution_time_ms)
    return vs


def request_real_link(link, req):
    response = requests.get(link, headers=headers)
    soup = BS(response.text, 'html.parser')

    baseInfoModule = soup.find("div", attrs={"class": "baseInfoModule"})
    baseInfoMain = baseInfoModule.find("div", attrs={"class": "baseInfoMain"})

    name = baseInfoMain.find("div", attrs={"class": "title"}).find("h1").get_text()
    addr = baseInfoMain.find("p", attrs={"class": "baseInfoText"}).get_text()

    # 简介
    div = soup.find_all(name="div", attrs={"class": "detailModuleRef"})
    div = div[0].find(name="div", attrs={"class": "LimitHeightText"})
    p = div.find_all(name="p")
    intro = ""
    if len(p) == 0:
        intro = div.find(name="div").text
    if len(p) == 1:
        intro = p[0].text
    if len(p) == 2:
        intro = p[0].text + p[1].text
    if len(p) >= 3:
        intro = p[0].text + p[1].text + p[2].text

    score = soup.find_all(name="p", attrs={"class": "commentScoreNum"})[0].get_text()
    rank = soup.find_all(name="p", attrs={"class": "rankText"})[0].get_text()
    imgs = []
    img = soup.find_all(name="div", attrs={"class": "swiperItem"})
    for img_tag in img:
        style_attr = img_tag.get('style')
        # print(style_attr)
        if style_attr:
            # 使用正则表达式提取 URL
            url_match = re.search(r'background-image:url\(([^)]+)\)', style_attr)
            if url_match:
                background_image_url = url_match.group(1)
                imgs.append(background_image_url)
                # print(background_image_url)
            else:
                print("未找到 background-image 的 URL")
        else:
            print("未找到 style 属性")
    data = {
        "name": name,
        "introduce": intro,
        "imgs": imgs,
        "imgCount": len(imgs),
        "city": req['place'],
        "address": addr,
        "score": score,
        "rank": rank,
    }

    return data


def sight_items(places, placenames, scope):
    base = "https://you.ctrip.com/sight/"
    base2 = "https://you.ctrip.com"
    requestlist = []
    result_list = []

    requestlist = build_url(base, places, placenames)

    # 发送请求并解析数据
    for req in requestlist:
        try:
            vs = request_url(req)
            size = min(len(vs), scope)
            # for j in range(size):
            #     data = process_item(vs[j], req)
            #     if data is not None:
            #         result_list.append(data)
            #     time.sleep(0.3)
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # 创建一个并发任务列表
                futures = [executor.submit(process_item, vs[j], req) for j in range(size)]

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


def process_item(v, req):
    try:
        a_tag = v.find("a")
        link = ""
        text = ""
        if a_tag:
            # 获取链接和文本
            link = a_tag['href']
            text = a_tag.get_text()
            print(f"名称: {text}, 链接: {link}")
        data = request_real_link(link, req)
        return data
    except Exception as e:
        print(f"Error processing item: {e}")
        return None


# 示例用法
if __name__ == "__main__":
    start_time = time.time()
    city = "厦门"
    place = get_city_num(city)
    places = [place]  # 例如，选择一个地点
    placenames = [city]  # 对应地点的名称
    scope = 10  # 数量
    sight_data = sight_items(places, placenames, scope)
    print(json.dumps(sight_data, indent=2, ensure_ascii=False))
    end_time = time.time()
    # 计算执行时间
    execution_time_ms = (end_time - start_time) * 1000
    print(f"程序执行时间（毫秒）: {execution_time_ms} ms")
