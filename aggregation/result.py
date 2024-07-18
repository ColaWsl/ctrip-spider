import json

import requests

from flight import *

from weather import get_weather_info
from entertainment import *


def get_city_code(city):
    api_key = "8cbeeb681cf4926a0087edd8b2734c49"
    url = "https://restapi.amap.com/v3/geocode/geo?parameters"
    params = {
        "key": api_key,
        "city": city,
        "address": city,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json().get("geocodes")[0].get("adcode")
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None


# 旅游情况
def travel_data(city, des_city):
    # 天气
    city_adcode = get_city_code(des_city)
    extensions = "base"  # all/base
    weather_info = get_weather_info(city_adcode, extensions)
    # 交通
    trans = transportation(city, des_city)
    ret = {
        "weather": weather_info,
        "transportation": trans
    }
    return ret

# 娱乐相关 聚合接口
def entertainment_data(city, des_city):
    place = get_city_num(des_city)
    places = [place]  # 例如，选择一个地点
    placenames = [des_city]  # 对应地点的名称
    scope = random.randint(2, 5)  # 景点数量可以控制

    sight_data = sight_items(places, placenames, scope)
    print(json.dumps(sight_data, indent=2, ensure_ascii=False))
    food_items = scrape_food_items(places, placenames, scope)
    print(json.dumps(food_items, indent=2, ensure_ascii=False))

    ret = {
        "sight": sight_data,
        "food": food_items,
    }
    return ret

def food_data(city, des_city, min_, max_):
    start_time = time.time()
    place = get_city_num(des_city)
    places = [place]  # 例如，选择一个地点
    placenames = [des_city]  # 对应地点的名称
    scope = random.randint(min_, max_)  # 景点数量可以控制
    print("food scope" + str(scope))
    food_items = scrape_food_items(places, placenames, scope)
    end_time = time.time()
    # 计算执行时间
    execution_time_ms = (end_time - start_time) * 1000
    print("food_data time:")
    print(execution_time_ms)
    return food_items

def sight_data(city, des_city, min_, max_):
    start_time = time.time()
    place = get_city_num(des_city)
    places = [place]  # 例如，选择一个地点
    placenames = [des_city]  # 对应地点的名称
    scope = random.randint(min_, max_)  # 景点数量可以控制
    print("sight scope" + str(scope))

    sight_data = sight_items(places, placenames, scope)
    end_time = time.time()
    # 计算执行时间
    execution_time_ms = (end_time - start_time) * 1000
    print("sight_data time:")
    print(execution_time_ms)
    return sight_data
