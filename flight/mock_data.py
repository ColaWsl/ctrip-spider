# 通过模拟生成 假的航班 车票 信息
import json
from datetime import datetime, timedelta
import random

# 定义航空公司的信息
airlines = {
    "CA": "中国国际航空公司",
    "MU": "东方航空公司",
    "CZ": "南方航空公司",
    "HU": "海南航空公司",
    "MF": "厦门航空公司",
    "ZH": "深圳航空公司",
    "3U": "四川航空公司",
    "8L": "祥鹏航空公司",
    "HO": "吉祥航空公司",
    "SC": "山东航空公司",
    "JD": "首都航空公司",
    "FM": "上海航空公司",
    "G5": "华夏航空公司",
    "KY": "昆明航空公司",
    "NS": "河北航空公司",
    "PN": "西部航空公司",
    "CN": "大新华航空公司",
    "QW": "青岛航空公司",
    "EU": "成都航空公司"
}

trains = {
    "G": "高铁",
    "D": "动车",
    "T": "普通列车"
}


def generate_size():
    return random.randint(2, 6)


# 随机生成航班信息
def generate_flights(start_location, end_location):
    flights = []
    now = datetime.now()
    size = generate_size()
    for i in range(size):
        airline_code = random.choice(list(airlines.keys()))
        airline_name = airlines[airline_code]

        # 计算起飞时间
        departure_time = now + timedelta(hours=i * 2, minutes=random.randint(-20, 20))

        # 确保到达时间在起飞时间之后
        flight_duration = timedelta(hours=2, minutes=random.randint(-20, 20))
        arrival_time = departure_time + flight_duration

        flight_number = f"{airline_code}{i + 1}"

        flight_info = {
            "flight_number": flight_number,
            "airline": airline_name,
            "departure_time": departure_time.strftime("%Y-%m-%d %H:%M"),
            "arrival_time": arrival_time.strftime("%Y-%m-%d %H:%M"),
            "start_location": start_location,
            "end_location": end_location
        }
        flights.append(flight_info)

    flight = {
        "data": flights,
        "count": size
    }

    return flight


# 生成车次信息的函数
def generate_trains(start_location, end_location):
    trains_info = []
    now = datetime.now()
    size = generate_size()
    for i in range(size):
        train_type = random.choice(list(trains.keys()))
        train_name = trains[train_type]

        # 生成车次代号
        train_number = f"{train_type}{random.randint(1000, 9999)}"

        # 计算出发时间
        departure_time = now + timedelta(hours=i * 2, minutes=random.randint(-20, 20))

        # 确保到达时间在出发时间之后
        travel_duration = timedelta(hours=6, minutes=random.randint(-20, 20))
        arrival_time = departure_time + travel_duration

        train_info = {
            "train_number": train_number,
            "train_type": train_name,
            "departure_time": departure_time.strftime("%Y-%m-%d %H:%M"),
            "arrival_time": arrival_time.strftime("%Y-%m-%d %H:%M"),
            "start_location": start_location,
            "end_location": end_location
        }

        trains_info.append(train_info)
    train = {
        "data": trains_info,
        "count": size
    }

    return train


def transportation(start_location, end_location):
    flight_data = generate_flights(start_location, end_location)
    trains_data = generate_trains(start_location, end_location)
    res = {
        "data": {
            "flights": flight_data,
            "trains": trains_data,
        },
        "total": len(flight_data) + len(trains_data),
    }
    return res
    # return json.dumps(res, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    # 定义起始地和目的地
    start_location = "北京"
    end_location = "上海"
    flight_data = generate_flights(start_location, end_location)
    trains_data = generate_trains(start_location, end_location)
    res = {
        "data": {
            "flights": flight_data,
            "trains": trains_data,
        },
        "total": len(flight_data) + len(trains_data),
    }
    print(json.dumps(res, indent=2, ensure_ascii=False))
