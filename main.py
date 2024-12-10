import random
from requests import get, post
import sys
import os
import json

def get_color():
    # 获取随机颜色
    get_colors = lambda n: list(map(lambda i: "#" + "%06x" % random.randint(0, 0xFFFFFF), range(n)))
    color_list = get_colors(100)
    return random.choice(color_list)

def get_access_token():
    # appId
    app_id = config["app_id"]
    # appSecret
    app_secret = config["app_secret"]
    post_url = ("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}"
                .format(app_id, app_secret))
    try:
        access_token = get(post_url).json()['access_token']
    except KeyError:
        print("获取access_token失败，请检查app_id和app_secret是否正确")
        os.system("pause")
        sys.exit(1)
    return access_token

def get_weather():
    # 获取天气信息
    weather_url = "https://aider.meizu.com/app/weather/listWeather?cityIds=101100301"
    try:
        response = get(weather_url).json()
        if response["code"] != "200":
            return None
        
        weather_data = response["value"][0]
        realtime = weather_data["realtime"]
        
        # 获取指定的指数信息
        indexes = weather_data["indexes"]
        gm_index = next((index for index in indexes if index["abbreviation"] == "gm"), None)
        ct_index = next((index for index in indexes if index["abbreviation"] == "ct"), None)
        
        return {
            "temp": realtime["temp"] + "°C",
            "weather": realtime["weather"],
            "wind": realtime["wD"] + realtime["wS"],
            "gm_index": gm_index["content"] if gm_index else "",
            "ct_index": ct_index["content"] if ct_index else "",
            "feel_temp": realtime["sendibleTemp"] + "°C"  # 体感温度
        }
    except Exception as e:
        print(f"获取天气信息失败：{str(e)}")
        return None

def send_message(to_user, access_token, region_name, note_ch, note_en):
    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(access_token)
    
    # 获取天气信息
    weather_info = get_weather()
    if not weather_info:
        print("未能获取天气信息")
        return
    
    data = {
        "touser": to_user,
        "template_id": config["template_id"],
        "url": "https://test.leobba.cn/weather.php",
        "topcolor": "#FF0000",
        "data": {
            "region": {
                "value": region_name,
                "color": get_color()
            },
            "weather": {
                "value": weather_info["weather"],
                "color": get_color()
            },
            "temp": {
                "value": weather_info["temp"],
                "color": get_color()
            },
            "feel_temp": {
                "value": weather_info["feel_temp"],
                "color": get_color()
            },
            "wind": {
                "value": weather_info["wind"],
                "color": get_color()
            },
            "gm_index": {
                "value": weather_info["gm_index"],
                "color": get_color()
            },
            "ct_index": {
                "value": weather_info["ct_index"],
                "color": get_color()
            },
            "note_en": {
                "value": note_en if note_en else "Have a nice day!",
                "color": get_color()
            },
            "note_ch": {
                "value": note_ch if note_ch else "祝你今天开心！",
                "color": get_color()
            }
        }
    }
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    response = post(url, headers=headers, json=data).json()
    
    if response["errcode"] == 40037:
        print("推送消息失败，请检查模板id是否正确")
    elif response["errcode"] == 40036:
        print("推送消息失败，请检查模板id是否为空")
    elif response["errcode"] == 40003:
        print("推送消息失败，请检查微信号是否正确")
    elif response["errcode"] == 0:
        print("推送消息成功")
    else:
        print(response)

if __name__ == "__main__":
    try:
        with open("config.json", encoding="utf-8") as f:
            config = json.loads(f.read())
    except FileNotFoundError:
        print("推送消息失败，请检查config.json文件是否与程序位于同一路径")
        os.system("pause")
        sys.exit(1)
    except json.JSONDecodeError:
        print("推送消息失败，请检查配置文件格式是否正确")
        os.system("pause")
        sys.exit(1)

    # 获取accessToken
    accessToken = get_access_token()
    # 接收的用户
    users = config["user"]
    # 地区
    region = config["region"]
    # 获取自定义消息
    note_ch = config["note_ch"]
    note_en = config["note_en"]
    
    # 公众号推送消息
    for user in users:
        send_message(user, accessToken, region, note_ch, note_en)
