from app.ai.model.my_model import MyModel
from langchain.agents import create_agent
from app.ai.tool.getadm_tool import get_administration_tool
import ast

class AdmAgent:
    def __init__(self):
        self.model = MyModel.get_local_model()
        self.prompt = self.get_prompt()
        self.tool = self.get_tool()
        self.agent = self.get_agent()

    def get_prompt(self):
        self.prompt = """
            一 角色：你是一个辅助查询目的地天气的助手，用于查询行政区域方便数据库分级
            二 任务：
                严格按照下列步骤进行执行任务：
                    步骤一: 根据用户的问题，分析出希望查询的行政区域地址作为'keywords'，以及查询的行政区域级数作为'subdistrict'
                    步骤二：调用工具 get_administration_tool 来查询地址行政区域
            三 规则：
                若用户没有明确说明想查询行政区域级数，则默认查询2级
        """
        return self.prompt
    def get_tool(self):
        self.tool = [get_administration_tool]
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
            rs = self.agent.astream_events(msg,version="v2")
            async for event in rs:
                event_type = event["event"]
                if event_type == "on_tool_end":
                    result = event["data"]["output"].content
                    if result:
                        # print(f"待解析的字符串: {repr(result)}")
                        # print(type(result))
                        yield result
            # rs = await self.agent.ainvoke(msg)
            # yield rs["messages"][-1].content
        except Exception as e:
            print(f"行政区域智能体查询出现异常：{e}")
            yield "行政区域智能体查询出现异常"

async def test(q):
    agent = AdmAgent()
    async for rs in agent.chat(q):
        print(rs)
        #print(type(rs))

if __name__ == "__main__":
    import asyncio
    q1 = "成都"
    rs = asyncio.run(test(q1))