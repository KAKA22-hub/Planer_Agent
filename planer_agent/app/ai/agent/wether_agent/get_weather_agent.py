import ast
from app.ai.model.my_model import MyModel
from langchain.agents import create_agent
from app.ai.tool.weather_tool import weather_tool

class WeatherAgent:
    def __init__(self):
        self.model = MyModel.get_local_model()
        self.prompt = self.get_prompt()
        self.tool = self.get_tool()
        self.agent = self.get_agent()

    def get_prompt(self):
        self.prompt = """
            一 角色：你是一个查询目的地天气的助手
            二 任务：
                严格按照下列步骤进行执行任务：
                    步骤一: 根据调用工具 weather_tool 来查询对应地址天气
                    步骤二：返回对应地址的天气
            三 规则：
                使用工具根据用户问题返回一个或多个地址的天气
            四 输出：
                输出格式必须为：{'address': 'xxxx', 'weather': 'xx', 'temperature': 'xx'}
        """
        return self.prompt
    def get_tool(self):
        self.tool = [weather_tool]
        return self.tool
    def get_agent(self):
        self.agent = create_agent(
            model=self.model,
            system_prompt=self.prompt,
            tools=self.tool,
        )
        return self.agent
    async def chat(self,question):
        try:
            for q in question.split(","):
                msg = {"messages":[{"role":"user","content":q}]}
                rs = self.agent.astream_events(msg, version="v2")
                async for event in rs:
                    event_type = event["event"]
                    if event_type == "on_tool_end":
                        result = event["data"]["output"].content
                        if result:
                            data = ast.literal_eval(result)
                            yield {
                                "address":data[0],
                                "weather":data[1][0],
                                "temperature":data[1][1]
                            }
        except Exception as e:
            print(f"天气智能体出现异常:{e}")
            yield "天气智能体出现异常"

async def test(question):
    agent = WeatherAgent()
    async for data in agent.chat(question):
        print(data,end="")



if __name__ == "__main__":
    import asyncio
    q1 = "110105,110108"
    q2 = "510103"
    q3 = "510104"
    rs = asyncio.run(test(q3))
