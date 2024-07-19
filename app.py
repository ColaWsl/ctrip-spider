from flask import Flask

from nav import *
from aggregation import *
import concurrent.futures

app = Flask(__name__)


#
@app.route('/travel')
def travel():
    data = travel_data("北京", "上海")
    return data


@app.route('/food')
def food():
    data = food_data("北京", "上海", 3, 5)
    return data


@app.route('/sight')
def sight():
    data = sight_data("天津", "北京", 3, 5)
    return data


@app.route('/entertainment')
def entertainment():
    city = "厦门"
    des_city = "深圳"
    food = food_data(city, des_city)
    sight = sight_data(city, des_city)
    return {
        "food": food,
        "sight": sight
    }


@app.route('/aggr')
def aggr():
    min_ = 3
    max_ = 8
    start_time = time.time()
    city = "杭州"
    des_city = "北京"
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 提交每个任务到线程池
        future_food = executor.submit(food_data, city, des_city, min_, max_)
        future_sight = executor.submit(sight_data, city, des_city, 5, 10)
        future_travel = executor.submit(travel_data, city, des_city)

        # 等待所有任务完成并获取结果
        food = future_food.result()
        sight = future_sight.result()
        travel = future_travel.result()

    end_time = time.time()
    # 计算执行时间
    execution_time_ms = (end_time - start_time) * 1000
    print("aggr time: " + str(execution_time_ms))
    return {
        "food": food,
        "sight": sight,
        "travel": travel
    }


@app.route('/location')
def loc():
    events = [
        {
            "city": "北京",
            "address": "北京市延庆区G6京藏高速58号出口"
        },
        {
            "city": "北京",
            "address": "北京市西城区前海西街17号"
        },
        {
            "city": "北京",
            "address": "北京市通州区北京环球度假区"
        },
        {
            "city": "北京",
            "address": "北京市海淀区新建宫门路19号"
        },
        {
            "city": "北京",
            "address": "北京市东城区景山前街4号"
        },
        {
            "city": "北京",
            "address": "北京市东城区天坛路甲1号"
        }
    ]
    # 前提 events 的第一元素是起点
    event = events[0]
    events.remove(event)
    # 解析events 经纬度数据
    events_loc = get_events_loc(events)
    events_loc.insert(0, loc_info(event))
    # 生成最优路线
    events_loc = generate_optimal_path(events_loc)

    # 生成导航路线方案
    res = get_nav_route(events_loc)
    return res


if __name__ == '__main__':
    app.run()
