import os

import requests
from dotenv import load_dotenv

from nav import loc_info

load_dotenv()  # 从.env文件加载环境变量
api_key = os.getenv('API_KEY')




# 根据位置获取附近酒店信息
def get_hotel_info(event):
    # {"location": "118.068351,24.444549", "citycode": "0592", "adcode": "350203", "city": "厦门", "address": "厦门市思明区鼓浪屿"}
    loc = loc_info(event)
    base_url = "https://restapi.amap.com/v5/place/around"
    params = {
        "key": api_key,
        "location": loc['location'],
        "radius": 5000,  # 5km范围内
        "types": 100105,  # 经济连锁酒店类型
    }
    # 发送GET请求
    response = requests.get(base_url, params=params)
    # 检查响应状态
    if response.status_code == 200:
        data = response.json()
        return parse_poi_response(data)
    else:
        print("HTTP request failed with status code:", response.status_code)
        return None


def parse_poi_response(response_json):
    # 检查响应中的POI数量
    poi_count = int(response_json.get('count', 0))
    if poi_count == 0:
        print("没有找到任何POI")
        return {
            "count": 0,
            "hotels": None
        }

    # 提取POI信息
    pois = response_json.get('pois', [])
    hotels = []
    for poi in pois:
        name = poi.get('name', 'N/A')
        address = poi.get('address', 'N/A')
        distance = poi.get('distance', 'N/A')
        cityname = poi.get('cityname', 'N/A')
        adname = poi.get('adname', 'N/A')
        location = poi.get('location', 'N/A')
        type = poi.get('type', 'N/A')
        hotel = {
            "name": name,
            "address": cityname + adname + address,
            "distance": str(distance) + '米',
            "type": type
        }
        hotels.append(hotel)
    return {
        "count": poi_count,
        "hotels": hotels
    }

if __name__ == '__main__':
    event = {
        "city": "上海",
        "address": "上海市浦东新区川沙新镇黄赵路310号"
    }
    hotel = get_hotel_info(event)
    for h in hotel['hotels']:
        print(h)
