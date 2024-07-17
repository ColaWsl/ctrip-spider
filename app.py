from flask import Flask
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
    data = food_data("北京", "上海")
    return data

@app.route('/sight')
def sight():
    data = sight_data("天津", "北京")
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
    start_time = time.time()
    city = "厦门"
    des_city = "深圳"
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 提交每个任务到线程池
        future_food = executor.submit(food_data, city, des_city)
        future_sight = executor.submit(sight_data, city, des_city)
        future_travel = executor.submit(travel_data, city, des_city)

        # 等待所有任务完成并获取结果
        food = future_food.result()
        sight = future_sight.result()
        travel = future_travel.result()

    end_time = time.time()
    # 计算执行时间
    execution_time_ms = (end_time - start_time) * 1000
    print(execution_time_ms)
    return {
        "food": food,
        "sight": sight,
        "travel": travel
    }

if __name__ == '__main__':
    app.run()
