from app.ai.model.my_model import MyModel
from langchain.agents import create_agent
from app.ai.tool.location_sql_tool import location_sql_tool

class AdcodeAgent:
    def __init__(self):
        self.model = MyModel.get_local_model()
        self.prompt = self.get_prompt()
        self.tool = self.get_tool()
        self.agent = self.get_agent()

    def get_prompt(self):
        self.prompt = """
        一 角色
            你是一个地址编码查询助手，负责根据用户输入的城市/位置信息，从数据库中查询对应的行政区划编码。
        二 输入格式
            用户输入可以是以下任意一种：
            - 纯城市名，如 "北京市"
            - 城市名 + 具体位置，用逗号分隔，如 "北京市,海淀区"
            - 自然语言描述，如 "我要查成都市春熙路的编码"（模型需自行提取城市和位置）
            你需要从输入中提取出 **城市** 和 **位置**（若未提供位置，则位置视为与城市相同）。
        三 任务
            1. 从用户输入中提取 `城市` 和 `位置`。
            2. 使用 `mysql_tool` 查询该 `城市` 和 `位置` 对应的行政区划编码。
            3. **如果查询到多个编码，只输出第一个（优先取与位置完全匹配的区/县编码，若无则取城市编码）**。
        四 输出规则
            - 始终只输出 **一个** 编码（字符串），如 `"110108"`。
            - 如果查询结果为空，输出 `"0"`。
            - 不得输出任何额外文本或解释。
        五 示例
            用户输入："北京市" → 输出：110000（城市编码，若数据库有）
            用户输入："北京市,海淀区" → 输出：110108
            用户输入："成都市春熙路" → 提取城市="成都市"，位置="春熙路" → 若查询到多个，取第一个匹配的（若春熙路属锦江区，输出510104）
            用户输入："未知城市" → 输出：0
        六 关键提醒
            - 调用工具时，请同时传递 `城市` 和 `位置` 参数，若无法提取位置，则位置使用城市名。
            - 如果 `mysql_tool` 返回多个结果，请**只取第一个**，并确保该结果是区/县级编码（优先），否则取城市编码
        """
        return self.prompt
    def get_tool(self):
        self.tool = [location_sql_tool]
        return self.tool
    def get_agent(self):
        self.agent = create_agent(
            model=self.model,
            tools=self.tool,
            system_prompt=self.prompt,
            debug = False,
        )
        return self.agent
    async def chat(self,question):
        try:
            msg = {"messages":[{"role":"user","content":question}]}
            result = await self.agent.ainvoke(msg)
            final_result = result["messages"][-1].content
            yield final_result
        except Exception as e:
            print(f"地址编码智能体出现异常:{e}")
            yield "地址编码智能体出现异常"

async def test(q):
    agent = AdcodeAgent()
    async for data in agent.chat(q):
        print(data)
        print(type(data))


if __name__ == "__main__":
    import asyncio
    q = "我要查询北京市朝阳区和海淀区的天气情况"
    q1 = "我要查询北京市朝阳区和海淀区地址编码"
    q2 = "北京市,海淀区"
    q3 = "成都市春熙路"
    q4 = "昆明市南屏街"
    rs = asyncio.run(test(q4))
