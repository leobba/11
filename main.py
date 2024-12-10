import random
from requests import get, post
import sys
import os
from datetime import datetime, date

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
            "feel_temp": realtime["sendibleTemp"] + "°C"
        }
    except Exception as e:
        print(f"获取天气信息失败：{str(e)}")
        return None

def get_countdown_days():
    today = date.today()
    countdown_days = {}
    
    # 处理倒计时日期
    for key, value in config.items():
        if key.startswith("countdown_"):
            target_date = datetime.strptime(value["date"], "%Y-%m-%d").date()
            days = (target_date - today).days
            if days >= 0:
                countdown_days[key] = {
                    "name": value["name"],
                    "days": days
                }
    
    return countdown_days

def send_message(to_user, access_token, region_name):
    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(access_token)
    
    # 获取天气信息
    weather_info = get_weather()
    if not weather_info:
        print("未能获取天气信息")
        return
    
    # 获取倒计时信息
    countdown_info = get_countdown_days()
    
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
            }
        }
    }
    
    # 添加倒计时数据
    for key, value in countdown_info.items():
        data["data"][key] = {
            "value": f"距离{value['name']}还有{value['days']}天",
            "color": get_color()
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
        with open("config.txt", encoding="utf-8") as f:
            config = eval(f.read())
    except FileNotFoundError:
        print("推送消息失败，请检查config.txt文件是否与程序位于同一路径")
        os.system("pause")
        sys.exit(1)
    except SyntaxError:
        print("推送消息失败，请检查配置文件格式是否正确")
        os.system("pause")
        sys.exit(1)

    accessToken = get_access_token()
    users = config["user"]
    region = config["region"]
    
    # 公众号推送消息
    for user in users:
        send_message(user, accessToken, region)
