import os
import requests
import urllib
import pprint
import json
import struct
import subprocess
from dotenv import load_dotenv


def main():
    url = make_url()
    json_data = get_weather_info(url)

    current_rainfall  = currentRainfall(json_data)
    one_hour_rainfall = oneHourRainfall(json_data)
    print("Railfall Predict:%s -> %s" % (current_rainfall, one_hour_rainfall))

    if is_railfall(current_rainfall, one_hour_rainfall):
        message = ("雨が振りそうです。1時間後の降水確率は、%sパーセントです" % (round(one_hour_rainfall)))
        notify(message)


def make_url():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(env_path)

    APP_ID      = os.environ.get("APP_ID")
    BASE_URL    = os.environ.get("BASE_URL")
    COORDINATES = os.environ.get("COORDINATES")
    OUTPUT      = "json"

    yolp_url = BASE_URL + "?appid=%s&coordinates=%s&output=%s" % (APP_ID, COORDINATES, OUTPUT)
    return yolp_url


def get_weather_info(url):
    req = requests.get(url)
    json_data = req.json()

    return json_data


# YOLPの結果から天気情報が入っている箇所の抜き出し
def wetherData(json_data):
    return json_data['Feature'][0]['Property']['WeatherList']['Weather']


# 現在の降水確率
def currentRainfall(json_data):
    weather = wetherData(json_data)
    return weather[0]['Rainfall']


# 1時間後の降水確率
def oneHourRainfall(json_data):
    weather = wetherData(json_data)
    return weather[6]['Rainfall']


# GoogleHomeへの通知条件判定
# <条件>
#  - 1時間後の降水確率の方が、現在より高い
#  - 1時間後の降水確率が、50%以上で今より20%高い
def is_railfall(current_rainfall, one_hour_rainfall):
    if one_hour_rainfall > current_rainfall:
        diff = one_hour_rainfall - current_rainfall
        if one_hour_rainfall > 50 and diff > 20:
            return True

    return False


def notify(message):
    GOOGLEHOME_NOTIFIER_IP = os.environ.get("GOOGLEHOME_NOTIFIER_IP")
    GOOGLEHOME_NOTIFIER_PORT = os.environ.get("GOOGLEHOME_NOTIFIER_PORT")

    url = "http://" + GOOGLEHOME_NOTIFIER_IP + ":" + GOOGLEHOME_NOTIFIER_PORT + "/google-home-notifier"
    data = [("text", message),]
    req = requests.post(url, data=data)

if __name__ == '__main__':
    main()
