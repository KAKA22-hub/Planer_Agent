from app.ai.model.my_model import MyModel
from langchain.agents import create_agent
from app.ai.tool.amap_tool import amap_tool
import ast

class WalkAgent:
    def __init__(self):
        self.model = MyModel.get_local_model()
        self.prompt = self.get_prompt()
        self.tool = self.get_tool()
        self.agent = self.get_agent()

    def get_prompt(self):
        self.prompt = """
            一 角色：
                你是一个步行路线规划助手，专注于为用户提供精准、便捷的步行导航服务。
    
            二 任务：
                严格按以下步骤执行，不可跳步或自行推断：
                    步骤1：解析用户问题，提取“起点”和“终点”。
                          - 起点字段名：start_location
                          - 终点字段名：end_location
                    步骤2：调用工具 `amap_tool` 获取步行路线规划结果。
                          - 工具参数必须为字典类型，格式：
                            {"start_location": "起点", "end_location": "终点"}
                          - 参数值必须为字符串，直接从用户输入中提取。
                    步骤3：工具调用成功后，以工具返回的步行路线作为最终结果。
    
            三 输入：
                调用 `amap_tool` 时，必须严格按照工具参数类型传递：
                {"start_location": "xxx", "end_location": "xxx"}
    
                - `start_location`: `str`，表示起始点位置。
                - `end_location`: `str`，表示目的地位置。
                - 用户输入格式通常为：
                  “从xxx步行到xxx”
                - “从”后面的地点为 start_location。
                - “到”后面的地点为 end_location。
    
            四 规则：
                1. 若用户已经明确提供起点和终点，必须直接调用 `amap_tool`，不得询问用户补充地址。
                2. 不允许在工具调用前输出“缺少起点”“缺少终点”等内容。
                3. 工具调用成功后，不得再次分析起点和终点。
                4. 不得将工具返回的路线描述再次当作用户问题进行分析。
                5. 不得编造起点和终点。
                6. 最终回答应以 `amap_tool` 返回的路线规划结果为准。
        """
        return self.prompt
    def get_tool(self):
        self.tool = [amap_tool]
        return self.tool
    def get_agent(self):
        self.agent = create_agent(
            model=self.model,
            tools=self.tool,
            system_prompt=self.prompt,
        )
        return self.agent
    async def chat(self,question):
        try:
            msg = {"messages":[{"role":"user","content":question}]}
            # rs = self.agent.astream_events(msg,version="v2")
            # async for event in rs:
            #     event_type = event["event"]
            #     if event_type == "on_chat_model_stream":
            #         if event["data"]["chunk"].content:
            #             yield f"{event["data"]["chunk"].content}"
            rs = self.agent.astream(msg,stream_mode="messages")
            async for r,m in rs:
                if r.content:
                    yield r.content
        except Exception as e:
            print(f"步行智能体查询出现异常：{e}")
            yield "步行智能体查询出现异常"

async def test(q):
    agent = WalkAgent()
    async for rs in agent.chat(q):
        print(rs,end="")
        #print(type(rs))

if __name__ == "__main__":
    import asyncio
    q1 = "从成都市天府广场到成都市武侯祠怎么走"
    rs = asyncio.run(test(q1))