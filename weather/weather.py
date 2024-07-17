import requests
import json


def get_weather_info(city_adcode, extensions="all"):
    api_key = "8cbeeb681cf4926a0087edd8b2734c49"
    url = "https://restapi.amap.com/v3/weather/weatherInfo"
    params = {
        "key": api_key,
        "city": city_adcode,
        "extensions": extensions
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json().get("lives")[0]
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None


def main():
    # Example usage:
    city_adcode = "110000"
    extensions = "base"  # all/base
    weather_info = get_weather_info(city_adcode, extensions)
    if weather_info:
        print(json.dumps(weather_info, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
