import requests
from datetime import datetime


# 根据城市名获取携程城市字母代码编号（城市名可以精确到县区）
def get_city_num(city):
    now = datetime.now()
    timestamp = int(datetime.timestamp(now) * 1000)

    base_url = "https://m.ctrip.com/restapi/h5api/globalsearch/search"
    params = {
        "action": "gsonline",
        "source": "globalonline",
        "keyword": city,  # 替换成你想要搜索的城市
        "t": timestamp  # 替换成你的时间戳
    }
    try:
        # 发送请求
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # 如果请求失败，抛出异常

        # 解析返回的 JSON 数据
        data = response.json()

        # 获取data数组的第一个元素
        first_item = data['data'][0]

        # 提取id和eName属性
        id_value = first_item['id']
        eName_value = first_item['eName']

        # 拼接eName和id
        res = "{}{}".format(eName_value, id_value)
        print(res)
        return res

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


# 示例用法
if __name__ == "__main__":

    city = "佛山"
    result = get_city_num(city)
    if result:
        print("拼接结果:", result)
