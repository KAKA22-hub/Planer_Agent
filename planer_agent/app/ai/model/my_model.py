from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from openai.types.admin.organization.projects.service_account_create_response import APIKey
load_dotenv()
"""
    模型封装：
    目的：方便后期代码维护更改，以及实例对象资源创建
"""
class MyModel:
    # 在线大模型的私有属性
    _line_model = None
    _local_model = None
    # 单例模式或软加载
    @staticmethod
    def get_line_model():
        # 第一次创建
        if MyModel._line_model is None:
            MyModel._line_model = ChatOpenAI(
                model = os.getenv("MODEL_LINE_NAME"),
                extra_body={
                    "enable_thinking": False # 关闭模型的固定思考模式（深度思考模式），想要json输出必须设为 False
                },
                api_key = os.getenv("DASHSCOPE_API_KEY")
            )
        #返回模型对象
        return MyModel._line_model


    @staticmethod
    def get_local_model():
        # 第一次创建
        if MyModel._local_model is None:
            MyModel._local_model = ChatOpenAI(
                model = os.getenv("MODEL_LOCAL_NAME"),
                base_url = os.getenv("LOCAL_URL"),
                api_key="None"
            )
        #返回模型对象
        return MyModel._local_model

if __name__ == "__main__":
    model = MyModel.get_local_model()
    rs = model.invoke(input="你好")
    print(rs)