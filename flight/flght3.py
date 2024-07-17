import hashlib
import json
import logging
import random
import time

import requests
from fake_useragent import UserAgent

ua = UserAgent()

def get_cookie_bfa():
    random_str = "abcdefghijklmnopqrstuvwxyz1234567890"
    random_id = ""
    for _ in range(6):
        random_id += random.choice(random_str)
    t = str(int(round(time.time() * 1000)))

    bfa_list = ["1", t, random_id, "1", t, t, "1", "1"]
    bfa = "_bfa={}".format(".".join(bfa_list))
    # e.g. _bfa=1.1639722810158.u3jal2.1.1639722810158.1639722810158.1.1
    return bfa

# 获取调用携程 API 查询航班接口 Header 中所需的参数 sign
def get_sign(transaction_id, departure_city_code, arrival_city_code, departure_date):
    sign_value = transaction_id + departure_city_code + arrival_city_code + departure_date
    _sign = hashlib.md5()
    _sign.update(sign_value.encode('utf-8'))
    return _sign.hexdigest()

def get_transaction_id(departure_city_code, arrival_city_code, departure_date, cabin):
    flight_list_url = "https://flights.ctrip.com/international/search/api/flightlist" \
                      "/oneway-{}-{}?_=1&depdate={}&cabin={}&containstax=1" \
        .format(departure_city_code, arrival_city_code, departure_date, cabin)
    flight_list_req = requests.get(url=flight_list_url)
    if flight_list_req.status_code != 200:
        logging.error("get transaction id failed, status code {}".format(flight_list_req.status_code))
        return "", None

    try:
        flight_list_data = flight_list_req.json()["data"]
        transaction_id = flight_list_data["transactionID"]
    except Exception as e:
        logging.error("get transaction id failed, {}".format(e))
        return "", None

    return transaction_id, flight_list_data

def generate_v_parameter():
    return f"{random.uniform(0.1, 0.2):.19f}"

# 获取航线具体信息与航班数据
def get_flight_info(departure_city_code, arrival_city_code, departure_date, cabin):
    # 获取 transactionID 及航线数据
    transaction_id, flight_list_data = get_transaction_id(departure_city_code, arrival_city_code, departure_date, cabin)
    if transaction_id == "" or flight_list_data is None:
        return False, None

    # 获取调用携程 API 查询航班接口 Header 中所需的参数 sign
    sign = get_sign(transaction_id, departure_city_code, arrival_city_code, departure_date)

    # cookie 中的 bfa
    bfa = get_cookie_bfa()

    # 构造请求，查询数据
    search_url = "https://flights.ctrip.com/international/search/api/search/batchSearch?v=" + generate_v_parameter()
    search_headers = {
        "transactionid": transaction_id,
        "sign": sign,
        "scope": flight_list_data["scope"],
        "origin": "https://flights.ctrip.com",
        # "referer": "https://flights.ctrip.com/online/list/oneway-{}-{}"
        #            "?_=1&depdate={}&cabin={}&containstax=1".format(departure_city_code, arrival_city_code,
        #                                                            departure_date, cabin),
        "content-type": "application/json;charset=UTF-8",
        "user-agent": ua.chrome,
        "cookie": bfa,
    }
    r = requests.post(url=search_url, headers=search_headers, data=json.dumps(flight_list_data))

    if r.status_code != 200:
        logging.error("get flight info failed, status code {}".format(r.status_code))
        return False, None

    try:
        result_json = r.json()
        if result_json["data"]["context"]["flag"] != 0:
            logging.error("get flight info failed, {}".format(result_json))
            return False, None
    except Exception as e:
        logging.error("get flight info failed, {}".format(e))
        return False, None

    if "flightItineraryList" not in result_json["data"]:
        result_data = []
    else:
        result_data = result_json["data"]["flightItineraryList"]
    return True, result_data

if __name__ == '__main__':
    departure_city_code = "nkg"
    arrival_city_code = "sha"
    departure_date = "2024-07-16"
    cabin = "Y_S_C_F"
    transaction_id, flight_list_data = get_transaction_id(departure_city_code, arrival_city_code, departure_date, cabin)
    get_flight_info(departure_city_code, arrival_city_code, departure_date, cabin)
