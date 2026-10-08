from app.ai.model.my_model import MyModel
from langchain.agents import create_agent
from app.ai.tool.recommendation_tool import get_recommendation_tool
import ast

class RecommendationAgent:
    def __init__(self):
        self.model = MyModel.get_local_model()
        self.prompt = self.get_prompt()
        self.tool = self.get_tool()
        self.agent = self.get_agent()

    def get_prompt(self):
        self.prompt = """
            一 角色：你是一个为用户推荐目的地附近场所的助手。
            二 任务：根据用户输入，提取以下参数并调用工具 `get_recommendation_tool` 获取推荐结果：
                - `boundary`：用户想要查询的**地点名称**（字符串），例如“成都市天府广场”“上海市外滩”。  
                **注意**：必须直接使用用户提到的地点名称作为字符串，不要构造坐标对象或字典。
                - `keyword`：用户希望查询的类型（字符串），例如“美食”“电影院”“景点”。  
                   如果用户没有明确指定，默认为空。
                - `radius`：查询半径（整数，单位：米），默认为 `5000`。
            三 调用规则：
                1. 根据用户问题，准确提取 `boundary`、`keyword`、`radius`。
                2. 调用 `get_recommendation_tool` 时，必须严格按照工具参数类型传递字典类型：{"boundary": xxx,"keyword": xxx,"radius": xxx}
                   - `boundary`: `str`
                   - `keyword`: `str`
                   - `radius`: `int`
                3. 如果用户没有提供半径，使用默认值 `5000`。
                4. 如果用户没有提供关键词，使用默认值 `餐厅`。
                5. 必须严格从用户问题中提取地点 `boundary`，不能编造。
            四 输出：
                工具返回的结果通常是一些场所信息，你需要将这些信息组织成**人性化、友好的自然语言回答**，介绍推荐的地点、地址、评分等，让用户感觉贴心。
        """
        return self.prompt

    def get_tool(self):
        self.tool = [get_recommendation_tool]
        return self.tool

    def get_agent(self):
        agent = create_agent(
            model=self.model,
            system_prompt=self.prompt,
            tools=self.tool,
        )
        return agent

    async def chat(self,question):
        try:
            msg = {"messages":[{"role":"user","content":question}]}
            rs = self.agent.astream_events(msg, version="v2")
            async for event in rs:
                event_type = event["event"]
                if event_type == "on_chat_model_stream":
                    if event["data"]["chunk"].content:
                        yield f"{event["data"]["chunk"].content}"
            # rs = self.agent.astream(msg,stream_mode="messages")
            # async for r,m in rs:
            #     if r.content:
            #         yield r.content
        except Exception as e:
            print(f"推荐智能体出现异常：{e}")
            yield "推荐智能体出现异常"

async def test(q):
    agent = RecommendationAgent()
    async for r in agent.chat(q):
        print(r,end="")

if __name__ == "__main__":
    import asyncio
    q1 = "成都市天府广场附近有什么"
    q2 = "成都市宽窄巷子周围有什么"
    q3 = "昆明南屏街附近有哪些饭店"
    rs = asyncio.run(test(q1))