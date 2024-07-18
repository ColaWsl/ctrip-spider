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
    city = "上海"
    des_city = "深圳"
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
            "city": "深圳",
            "address": "深圳市盐田区盐葵路大梅沙段148号"
        },
        {
            "city": "深圳",
            "address": "深圳市南山区华侨城侨城西路"
        },
        # {
        #     "city": "深圳",
        #     "address": "深圳市福田区益田路5033号平安金融中心116层"
        # },
        # {
        #     "city": "深圳",
        #     "address": "深圳市南山区华侨城深南大道9003号"
        # },
        # {
        #     "city": "深圳",
        #     "address": "深圳市盐田区大梅沙东部华侨城"
        # }
    ]
    events_loc = get_events_loc(events)
    e1 = events_loc[0]
    e2 = events_loc[1]
    res = get_distance_and_transit(e1["location"], e1["citycode"], e2["location"], e2["citycode"])
    return res


if __name__ == '__main__':
    app.run()
