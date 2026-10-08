from langchain.tools import tool
import os
import requests
from dotenv import load_dotenv
from pydantic import BaseModel,Field

class GetAdministrationParams(BaseModel):
    keywords:str = Field(...,description="查询地址")
    subdistrict:int = Field(1,description="查询级数")

@tool(args_schema=GetAdministrationParams)
def get_administration_tool(keywords:str,subdistrict:int = 1)->str:
    """
    行政区域查询
    """
    load_dotenv()
    try:
        params = {
            "key":os.getenv("AMAP_KEY"),
            "keywords":keywords,
            "subdistrict":subdistrict
        }
        rs = requests.get(
            url="https://restapi.amap.com/v3/config/district?parameters",
            params=params,
        )
        data = rs.json()
        if data["status"] == "1":
            d = data["districts"]
            new_list = []
            stack = list(d)
            while stack:
                district = stack.pop()
                name = district["name"]
                if name:
                    new_list.append(name)
                children = district["districts"]
                if children:
                    stack.extend(children)
        return new_list
    except Exception as e:
        print(f"出现异常{e}")
        return "查找失败"


if __name__ == "__main__":
    ad = get_administration_tool.invoke({"keywords":"北京","subdistrict":1})
    print(ad)