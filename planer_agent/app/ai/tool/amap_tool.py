import requests
from dotenv import load_dotenv
import os
from langchain.tools import tool
from pydantic import BaseModel,Field

from psycopg.abc import Params

def get_location(address):
    load_dotenv()

    params={
        "key":os.getenv("AMAP_KEY"),
        "address":address
    }

    rs = requests.get(
        url="https://restapi.amap.com/v3/geocode/geo?parameters",
        params=params
    )
    data = rs.json()
    return data["geocodes"][0]["location"]

# 高德地图参数模型类
class AmapParams(BaseModel):
    start_location: str = Field(...,description="出发点")
    end_location: str = Field(...,description="目的地")

@tool(args_schema=AmapParams)
def amap_tool(start_location:str,end_location:str)->str:
    """
        步行查询路线
    """
    try:
        # 获取出发点目的地经纬度坐标
        start = get_location(start_location)
        end = get_location(end_location)
        # 定义参数
        params={
            "key":os.getenv("AMAP_KEY"),
            "origin":start,
            "destination":end
        }
        # 发送请求
        rs = requests.get(
            url="https://restapi.amap.com/v3/direction/walking?parameters",
            params=params
        )
        data = rs.json()
        if data["status"] == "1":
            d = data["route"]["paths"][0]["steps"]
            new_list = []
            for i in d:
                new_list.append(i["instruction"])
            return "\n".join(new_list)
    except Exception as e:
        print(f"出现异常{e}")
        return "查询失败"


if __name__ =='__main__':
    # ad = amap_tool.invoke({
    #     "start_location":"成都市天府广场",
    #     "end_location":"成都市武侯祠",
    # })
    ad = amap_tool.invoke({
        "start_location":"天府广场",
        "end_location":"武侯祠",
    })
    # ad = get_location("天府广场")
    print(ad)
