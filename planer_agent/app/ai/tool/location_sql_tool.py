import pymysql
from pydantic import BaseModel,Field
from langchain.tools import tool
from dotenv import load_dotenv
import os

load_dotenv()
class LocationsqlParams(BaseModel):
    city:str = Field(...,description="所属城市")
    location:str = Field(...,description="具体位置")


@tool(args_schema=LocationsqlParams)
def location_sql_tool(city:str,location:str)->str:
    """
        通过语句查找数据库中对应城市编码
        数据库模式：
            amap_adcode_citycode 地址信息编码表 字段：name (地址中文名称) adcode（地址编码）citycode(城市编码)
    """
    # 数据链接
    con = None
    # 游标对象
    cursor = None
    try:
        # 读取配置
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_name = os.getenv("DB_NAME")
        if not db_name or not db_host or not db_port or not db_user or not db_password:
            return "请检查数据库配置"
        con = pymysql.connect(
            host=db_host,
            port=int(db_port),
            user=db_user,
            password=db_password,
            db=db_name,
            charset = "utf8"
        )
        # 创建游标对象
        cursor = con.cursor()
        # 执行sql语句
        sql_city = """
            SELECT DISTINCT citycode FROM amap_adcode_citycode WHERE name = %s
        """
        cursor.execute(sql_city,(city,))
        # 获取结果
        rs = cursor.fetchall()
        citycode = str(rs[0][0])
        ad_list = []
        sql_ad = """
            SELECT adcode FROM amap_adcode_citycode WHERE name = %s AND citycode = %s
        """
        cursor.execute(sql_ad, (location,citycode))
        result = cursor.fetchall()
        if result:
            ad_list.append(str(result[0][0]))
        con.commit()
        # print(ad_list)
        return ",".join(ad_list)

    except Exception as e:
        print(f"出现异常{e}")
        return "数据库出现异常"
    finally:
        # 资源释放
        if cursor:
            cursor.close()
        if con:
            con.close()

if __name__=="__main__":
    rs=location_sql_tool.invoke({"city":"北京市", "location":"海淀区"})
    print(rs)
