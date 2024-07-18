import json
import time

import requests
from dotenv import load_dotenv
import os

load_dotenv()  # 从.env文件加载环境变量
api_key = os.getenv('API_KEY')


# 根据结构化地址和城市得到具体信息
# {"location": "118.068351,24.444549", "citycode": "0592", "adcode": "350203", "city": "厦门", "address": "厦门市思明区鼓浪屿"}
def loc_info(event):
    base_url = "https://restapi.amap.com/v3/geocode/geo"
    params = {
        "key": api_key,
        "address": event["address"],  # 结构化信息 上海市浦东新区川沙新镇黄赵路310号
        "city": event["city"],
    }
    # 发送GET请求
    response = requests.get(base_url, params=params)
    # 检查响应状态
    if response.status_code == 200:
        data = response.json()
        if data['status'] == '1' and data['count'] != '0':
            geocode_info = data['geocodes'][0]
            location = geocode_info['location']
            citycode = geocode_info['citycode']
            adcode = geocode_info['adcode']
            # return location, citycode, adcode
            return {
                'location': location,
                'citycode': citycode,
                'adcode': adcode,
                'city': event["city"],
                'address': event["address"],
            }
        else:
            print("No results found or request failed:", data['info'])
            return None
    else:
        print("HTTP request failed with status code:", response.status_code)
        return None


def parse_formatted_address(location):
    start_time = time.time()
    key = api_key
    # 构建API请求的URL
    url = f"https://restapi.amap.com/v3/geocode/regeo?location={location}&key={key}"

    try:
        # 发送GET请求到API
        response = requests.get(url)
        data = response.json()

        # 检查返回的数据中是否包含formatted_address字段
        if 'regeocode' in data and 'formatted_address' in data['regeocode']:
            formatted_address = data['regeocode']['formatted_address']
            end_time = time.time()
            # 计算执行时间
            execution_time_ms = (end_time - start_time) * 1000
            print(f"parse_formatted_address: {execution_time_ms} ms")
            return formatted_address
        else:
            return "未能找到formatted_address字段"

    except requests.exceptions.RequestException as e:
        return f"请求发生错误: {e}"

if __name__ == "__main__":
    event = {
        "city": "厦门",
        "address": "深圳市盐田区盐葵路大梅沙段148号"
    }
    print(loc_info(event))
