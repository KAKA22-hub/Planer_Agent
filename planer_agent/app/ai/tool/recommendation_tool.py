import requests
from dotenv import load_dotenv
import os
from langchain.tools import tool
from pydantic import BaseModel,Field


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

# 高德地图推荐
class RecommendationMap(BaseModel):
    boundary:str = Field(...,description="需要查询的地点名称或详细地址")
    keyword: str|None = Field(None,description="搜索关键词（可选）")
    radius: int = Field(5000, description="搜索半径（米），默认1000")

@tool(args_schema=RecommendationMap)
def get_recommendation_tool(boundary:str,keyword:str = None,radius:int = 5000)->str:
    """
    周边5km内容推荐
    """
    load_dotenv()
    try:
        location = get_location(boundary)
        params={
            "key":os.getenv("AMAP_KEY"),
            "location":location,
            "keywords":keyword,
            "radius":radius
        }
        rs = requests.get(
            url="https://restapi.amap.com/v3/place/around?parameters ",
            params = params
        )
        data = rs.json()
        if data["status"] == "1":
            d = data["pois"]
            dic = {}
            new_list = []
            for i in d:
                dic[i["name"]]=i["address"]
            # print(dic)
                # new_list.append(i["name"])
                # new_list.append(i["address"])
            return dic
    except Exception as e:
        print(f"推荐出现异常：{e}")
        return "推荐出现异常!"

if __name__ == "__main__":
    q = {"boundary":"成都市天府广场"}
    q1 = {"boundary":"成都市天府广场","keyword":"美食","radius":1000}
    q2 = "成都市天府广场"
    ad = get_recommendation_tool.invoke(q2)
    print(ad)

    # ad = get_location("成都市天府广场")
    # lng,lat = ad.split(",")
    # print(lng,lat)