import numpy as np
from math import radians, sin, cos, sqrt, atan2


# Haversine 公式计算地球表面两点间的距离
def haversine(lon1, lat1, lon2, lat2):
    R = 6371.0  # 地球半径，单位为公里
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c

    return distance


# 生成距离矩阵
def create_distance_matrix(coords):
    num_points = len(coords)
    dist_matrix = np.zeros((num_points, num_points))
    for i in range(num_points):
        for j in range(num_points):
            if i != j:
                dist_matrix[i][j] = haversine(coords[i][1], coords[i][0], coords[j][1], coords[j][0])
    return dist_matrix


# 最近邻算法生成路径
def nearest_neighbor(dist_matrix):
    num_points = len(dist_matrix)
    visited = [False] * num_points
    path = [0]
    visited[0] = True

    for _ in range(num_points - 1):
        last = path[-1]
        next_city = np.argmin([dist_matrix[last][j] if not visited[j] else float('inf') for j in range(num_points)])
        path.append(next_city)
        visited[next_city] = True

    return path


# 示例经纬度坐标
coords = [
    (116.4074, 39.9042),  # 北京
    (121.4737, 31.2304),  # 上海
    (114.3055, 30.5928),  # 武汉
    (113.2644, 23.1291),  # 广州
    (104.0665, 30.5723),  # 成都
]

# 生成距离矩阵
dist_matrix = create_distance_matrix(coords)

# 求解最优化路径
optimal_path = nearest_neighbor(dist_matrix)
optimal_path_coords = [coords[i] for i in optimal_path]

print("最优化路径:", optimal_path_coords)