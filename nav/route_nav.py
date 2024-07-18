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


def get_distance_and_transit(origin, city1code, destination, city2code):
    url = "https://restapi.amap.com/v5/direction/transit/integrated"
    params = {
        "key": api_key,
        "origin": origin,
        "destination": destination,
        "city1": city1code,
        "city2": city2code,
        "AlternativeRoute": 5,
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
                "transits": transits,
                "origin": origin,
                "destination": destination,
                "description": parse_transits(transits),
                "description2": parse_transits2(transits),

            }
        else:
            print(f"Error: {data['info']}")
            return None

    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return None


def parse_transits2(transits):
    result = []

    for index, transit in enumerate(transits):
        total_duration = float(transit['cost']['duration']) / 60.0  # 转换为分钟
        total_distance = float(transit['distance']) / 1000.0  # 转换为公里
        walking_distance = float(transit['walking_distance']) / 1000.0  # 转换为公里
        total_cost = float(transit['cost']['transit_fee'])  # 转换为元

        template = f"### 方案{index + 1}\n"
        template += f"- **总时长**: {total_duration:.2f} 分钟\n"
        template += f"- **总距离**: {total_distance:.3f} 公里\n"
        template += f"- **步行距离**: {walking_distance:.3f} 公里\n"
        template += f"- **总费用**: {total_cost:.1f} 元\n\n"

        for segment in transit['segments']:
            if 'bus' in segment:
                busline = segment['bus']['buslines'][0]
                departure_stop = busline['departure_stop']
                arrival_stop = busline['arrival_stop']
                bus_type = busline['type']
                segment_distance = float(busline['distance']) / 1000.0  # 转换为公里
                segment_duration = float(busline['cost']['duration']) / 60.0  # 转换为分钟

                template += f"**交通类型**: {bus_type}\n"
                template += f"   - 路线: {busline['name']} \n"
                template += f"   - 出发站: {departure_stop['name']} ({departure_stop['location']})\n"
                template += f"   - 到达站: {arrival_stop['name']} ({arrival_stop['location']})\n"
                template += f"   - 距离: {segment_distance:.2f} 公里\n"
                template += f"   - 时间: {segment_duration:.1f} 分钟\n\n"

            if 'walking' in segment:
                walking_start = segment['walking']['origin']
                walking_start = parse_formatted_address(walking_start)
                walking_end = segment['walking']['destination']
                walking_end = parse_formatted_address(walking_end)
                walking_distance = float(segment['walking']['distance']) / 1000.0  # 转换为公里
                walking_duration = float(segment['walking']['cost']['duration']) / 60.0  # 转换为分钟

                template += f"步行详情:\n"
                template += f"   - 起始位置: {walking_start}\n"
                template += f"   - 目的地: {walking_end}\n"
                template += f"   - 距离: {walking_distance:.3f} 公里\n"
                template += f"   - 时间: {walking_duration:.0f} 分钟\n"
                template += f"   - 步行路线:\n"

                for step in segment['walking']['steps']:
                    template += f"     - {step['instruction']}\n"

                template += "\n"

        result.append(template)

    return result



def parse_transits(transits):
    result = []

    for index, transit in enumerate(transits):
        total_duration = float(transit['cost']['duration']) / 60.0  # 转换为分钟
        total_distance = float(transit['distance']) / 1000.0  # 转换为公里
        walking_distance = float(transit['walking_distance']) / 1000.0  # 转换为公里
        total_cost = float(transit['cost']['transit_fee'])  # 转换为元

        template = f"### 方案{index + 1}\n"
        template += f"- **总时长**: {total_duration:.2f} 分钟\n"
        template += f"- **总距离**: {total_distance:.3f} 公里\n"
        template += f"- **步行距离**: {walking_distance:.3f} 公里\n"
        template += f"- **总费用**: {total_cost:.1f} 元\n\n"

        for segment in transit['segments']:
            if 'bus' in segment:
                busline = segment['bus']['buslines'][0]
                departure_stop = busline['departure_stop']
                arrival_stop = busline['arrival_stop']
                bus_type = busline['type']
                segment_distance = float(busline['distance']) / 1000.0  # 转换为公里
                segment_duration = float(busline['cost']['duration']) / 60.0  # 转换为分钟

                template += f"**交通类型**: {bus_type}\n"
                template += f"   - 出发站: {departure_stop['name']} ({departure_stop['location']})\n"
                template += f"   - 到达站: {arrival_stop['name']} ({arrival_stop['location']})\n"
                template += f"   - 距离: {segment_distance:.2f} 公里\n"
                template += f"   - 时间: {segment_duration:.1f} 分钟\n\n"

            if 'walking' in segment:
                walking_start = segment['walking']['origin']
                walking_end = segment['walking']['destination']
                walking_distance = float(segment['walking']['distance']) / 1000.0  # 转换为公里
                walking_duration = float(segment['walking']['cost']['duration']) / 60.0  # 转换为分钟

                template += f"步行详情:\n"
                template += f"   - 起始位置: {walking_start}\n"
                template += f"   - 目的地: {walking_end}\n"
                template += f"   - 距离: {walking_distance:.3f} 公里\n"
                template += f"   - 时间: {walking_duration:.0f} 分钟\n"
                template += f"   - 步行路线:\n"

                for step in segment['walking']['steps']:
                    template += f"     - {step['instruction']}\n"

                template += "\n"

        result.append(template)

    return result

if __name__ == '__main__':
    # events_loc = get_events_loc(events)
    # e1 = events_loc[2]
    # e2 = events_loc[3]
    e1 = events[0]
    e2 = events[1]
    res = get_distance_and_transit(e1["location"], e1["citycode"], e2["location"], e2["citycode"])
    print(res)
