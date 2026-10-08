import pymysql
from pydantic import BaseModel,Field
from langchain.tools import tool
from dotenv import load_dotenv
import os


class MysqlParams(BaseModel):
    sql:str = Field(...,description="sql语句")

load_dotenv()

@tool(args_schema=MysqlParams)
def mysql_tool(sql:str)->str:
    """
        执行sql语句
        数据库模式：
            user_info 用户信息表 字段: user_id user_name email 邮箱 depaetment 部门
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
        # 工具禁止ai操作数据库
        if sql.startswith("DELETE") or sql.startswith("DROP") or sql.startswith("UPDATE") or sql.startswith("INSERT"):
            return "禁止执行"
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
        cursor.execute(sql)
        # 获取结果
        rs = cursor.fetchall()
        # 事务提交,用于删除增加数据库
        con.commit()
        return str(rs)

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
    rs=mysql_tool.invoke(
        {"sql":"select * from user_info"}
    )
    print(rs)
