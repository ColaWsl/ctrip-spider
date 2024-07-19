import math


# 计算两点间的距离（使用 Haversine 公式）
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # 地球平均半径（单位：公里）

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

# 最近邻算法生成路径
def generate_optimal_path(events):
    # 提取每个事件点的经纬度
    points = [(float(event['location'].split(',')[1]), float(event['location'].split(',')[0])) for event in events]

    # 确定起点和终点的索引
    start_index = 0
    end_index = len(points) - 1

    unvisited = set(points)
    current_point = points[start_index]
    path = [events[start_index]]

    unvisited.remove(current_point)

    while unvisited:
        nearest_point = min(unvisited, key=lambda x: haversine(current_point[0], current_point[1], x[0], x[1]))
        path.append(events[points.index(nearest_point)])
        current_point = nearest_point
        unvisited.remove(nearest_point)

    return path


# 示例用法
events = [
    {'location': '113.978615,22.537872', 'citycode': '0755', 'adcode': '440305', 'city': '深圳', 'address': '深圳市南山区华侨城侨城西路'},
    {'location': '114.304642,22.594236', 'citycode': '0755', 'adcode': '440308', 'city': '深圳', 'address': '深圳市盐田区盐葵路大梅沙段148号'},
    {'location': '113.997275,22.531446', 'citycode': '0755', 'adcode': '440304', 'city': '深圳', 'address': '深圳市南山区华侨城深南大道9003号'},
    {'location': '114.287666,22.626673', 'citycode': '0755', 'adcode': '440308', 'city': '深圳', 'address': '深圳市盐田区大梅沙东部华侨城'},
    {'location': '114.055482,22.534040', 'citycode': '0755', 'adcode': '440304', 'city': '深圳', 'address': '深圳市福田区益田路5033号平安金融中心116层'}
]

# 生成路径
optimal_path = generate_optimal_path(events)
for item in optimal_path:
    print(item)