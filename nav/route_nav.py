import concurrent.futures
import time

import requests
from dotenv import load_dotenv
import os

from nav import loc_info, parse_formatted_address

event = {
    "city": "深圳",
    "address": "深圳市盐田区盐葵路大梅沙段148号"
}

events = [
    {
        "city": "深圳",
        "address": "深圳市盐田区盐葵路大梅沙段148号"
    },
    {
        "city": "深圳",
        "address": "深圳市南山区华侨城侨城西路"
    },
    {
        "city": "深圳",
        "address": "深圳市福田区益田路5033号平安金融中心116层"
    },
    {
        "city": "深圳",
        "address": "深圳市南山区华侨城深南大道9003号"
    },
    {
        "city": "深圳",
        "address": "深圳市盐田区大梅沙东部华侨城"
    }
]

load_dotenv()  # 从.env文件加载环境变量
api_key = os.getenv('API_KEY')


def get_nav_route(events_loc):
    nav_route = []
    for i in range(len(events_loc) - 1):
        e1 = events_loc[i]
        e2 = events_loc[i + 1]
        res = get_distance_and_transit(e1, e2)
        if res is not None:
            nav_route.append(res)
    return {
        "route": nav_route
    }


def get_events_loc(events):
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 并发调用 loc_info 函数
        futures = [executor.submit(loc_info, event) for event in events]
        # 收集结果
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    end_time = time.time()
    execution_time_ms = (end_time - start_time) * 1000
    print("get_events_loc time:" + str(execution_time_ms))
    return results


def get_distance_and_transit(event_loc1, event_loc2):
    # {'adcode': '330102', 'address': '杭州市西湖风景名胜区', 'city': '杭州', 'citycode': '0571', 'location': '120.158108,30.241651'}

    url = "https://restapi.amap.com/v5/direction/transit/integrated"
    params = {
        "key": api_key,
        "origin": event_loc1["location"],
        "destination": event_loc2["location"],
        "city1": event_loc1["citycode"],
        "city2": event_loc2["citycode"],
        # "AlternativeRoute": route_num,
        "show_fields": "cost"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if data["status"] == "1" and data["info"] == "OK":
            route = data["route"]
            # 距离
            distance = route["distance"]
            # 方案
            transits = route["transits"]
            return {
                "distance": str(float(distance) / 1000.0) + "km",
                "origin": event_loc1["address"],
                "destination": event_loc2["address"],
                "description": parse_transits(transits),

            }
        else:
            print(f"Error: {data['info']}")
            return None

    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return None


def parse_transit(transit):
    total_duration = float(transit['cost']['duration']) / 60.0
    total_distance = float(transit['distance']) / 1000.0
    walking_distance = float(transit['walking_distance']) / 1000.0
    total_cost = float(transit['cost']['transit_fee'])

    total_info = {
        "total_duration": total_duration,
        "duration_unit": "minute",
        "total_distance": total_distance,
        "distance_unit": "km",
        "total_cost": total_cost,
        "cost_unit": "rmb",
        "walking_distance": walking_distance
    }

    route = []

    for segment in transit['segments']:
        # item = {
        #     "departure": None,
        #     "arrival": None,
        #     "traffic_type": None,
        #     "distance": None,
        #     "duration": None,
        #     "name": None
        # }
        if 'bus' in segment:
            busline = segment['bus']['buslines'][0]
            departure_stop = busline['departure_stop']
            arrival_stop = busline['arrival_stop']
            bus_type = busline['type']
            segment_distance = float(busline['distance']) / 1000.0
            segment_duration = float(busline['cost']['duration']) / 60.0
            item = {'departure': {
                "departure_info": departure_stop,
                "name": departure_stop['name']
            }, 'arrival': {
                "arrival_info": arrival_stop,
                "name": arrival_stop['name']
            }, 'traffic_type': bus_type, 'distance': segment_distance, 'duration': segment_duration,
                'name': busline['name']}

            route.append(item)

        if 'walking' in segment:
            walking_start = segment['walking']['origin']
            walking_start = parse_formatted_address(walking_start)
            walking_end = segment['walking']['destination']
            walking_end = parse_formatted_address(walking_end)
            walking_distance = float(segment['walking']['distance']) / 1000.0
            walking_duration = float(segment['walking']['cost']['duration']) / 60.0
            item = {'departure': {
                "name": walking_start,
            }, 'arrival': {
                "name": walking_end
            }, 'traffic_type': "walking", 'distance': walking_distance, 'duration': walking_duration,
                'name': "步行没有线路名称"}

            route.append(item)

            # for step in segment['walking']['steps']:
            #     template += f"     - {step['instruction']}\n"

    return {
        "info": total_info,
        "route": route
    }


def parse_transits(transits):
    result = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for index, transit in enumerate(transits):
            transit['index'] = index
            futures.append(executor.submit(parse_transit, transit))

        for future in concurrent.futures.as_completed(futures):
            result.append(future.result())
    data = []
    cnt = 0
    for item in result:
        data.append({
            "index": cnt,
            "content": item
        })
        cnt += 1
    return data


if __name__ == '__main__':
    e1 = events[0]
    e2 = events[1]
    res = get_distance_and_transit(e1["location"], e1["citycode"], e2["location"], e2["citycode"])
    print(res)
