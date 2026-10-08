import requests
from dotenv import load_dotenv
import os
from langchain.tools import tool
from pydantic import BaseModel,Field

class WeatherParams(BaseModel):
    citycode:str = Field(...,description="地址编码")

@tool(args_schema=WeatherParams)
def weather_tool(citycode:str)->str:
    """
     查询对应地址的天气
    """
    load_dotenv()
    try:
        params = {
            "key":os.getenv("AMAP_KEY"),
            "city":citycode
        }
        rs = requests.get(
            url = "https://restapi.amap.com/v3/weather/weatherInfo?parameters",
            params = params
        )
        data = rs.json()
        if data["status"] == "1":
            ad_w = f"{data['lives'][0]['province']}{data['lives'][0]['city']}"
            w = (
                data["lives"][0]["weather"],
                data["lives"][0]["temperature"]
            )
            return ad_w, w
        return "天气查询失败", ("未知", "未知")

    except Exception as e:
        print(f"天气工具出现异常：{e}")
        return "天气查询失败", ("未知", "未知")

if __name__ == "__main__":
    ad = weather_tool.invoke("110105")
    print(ad)
    print(type(ad))
    # ad = weather_tool.invoke("110105,110108")
    # print(ad)