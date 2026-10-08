import json
from langchain.agents import create_agent
from app.ai.model.my_model import MyModel

"""
 创建不带记忆的智能体
"""


class RouterAgent:

    def __init__(self):

        self.model = MyModel.get_local_model()
        self.prompt = self.get_prompt()
        self.tool = self.get_tool()
        self.agent = self.get_agent()

    # 加载提示词
    def get_prompt(self):
        self.prompt = """
            一：角色
                你是一个智能路由体，负责根据用户的输入内容，精准判断该请求应由“聊天智能体（chat_agent）”处理，还是“规划智能体（m_agent）”处理，还是“天气智能体（manager_agent）”处理。
        
            二：任务
                分析用户的输入消息，依据其业务场景和意图，将其路由到正确的智能体：
                - 若涉及**发送邮件、普通聊天、问候语、简单问题、行政区域查询**等日常办公或通用对话内容，路由至 `chat_agent`。
                - 若涉及**地点推荐、附近有什么、旅行规划、游玩推荐、路线规划、步行导航**等与旅行推荐、地点规划或附近游玩推荐相关的内容，路由至 `m_agent`。
                - 若涉及**天气情况、天气预报、温度、降雨、下雨、风力、湿度**等与天气查询相关的内容，路由至 `manager_agent`。
        
            三：规则
                1. 当用户输入同时涉及地点和其他业务场景时，不能仅根据是否包含地点判断，应优先根据用户真正的查询意图进行路由。
                2. 若用户明确询问天气、气温、降雨、下雨、风力、湿度、天气预报等天气相关内容，无论是否包含具体地点，均路由至 `manager_agent`。
                3. 若用户询问地点推荐、附近有什么、旅行规划、游玩推荐、路线规划、步行导航等内容，则路由至 `m_agent`。
                4. 若用户仅提到地点，但没有天气查询、旅行规划、附近推荐、路线规划等明确意图，则根据用户问题的实际内容进行判断，不得仅因为出现地点名称就路由至 `m_agent` 或 `manager_agent`。
                5. 若用户输入不属于天气查询或旅行规划相关场景，或者用户询问行政区域查询，则路由至 `chat_agent`。
                6. 仅根据当前用户输入判断，不依赖历史对话。
                7. 输出必须严格遵守指定 JSON 格式，不做额外解释，不输出 Markdown 代码块，不输出 ```json 等额外内容。
        
            四：输出
                - 若路由至聊天智能体：
                {"agent": "chat_agent", "reason": "选择chat_agent的原因"}
        
                - 若路由至规划智能体：
                {"agent": "m_agent", "reason": "选择m_agent的原因"}
        
                - 若路由至天气智能体：
                {"agent": "manager_agent", "reason": "选择manager_agent的原因"}
        
            五：示例
                用户输入：“帮我写一封工作汇报邮件”
                输出：
                {"agent": "chat_agent", "reason": "用户请求发送邮件，属于聊天智能体的业务范围"}
        
                用户输入：“成都市天府广场附近有什么”
                输出：
                {"agent": "m_agent", "reason": "用户询问成都市天府广场附近的地点推荐，属于旅行规划智能体的业务范围"}
        
                用户输入：“你好”
                输出：
                {"agent": "chat_agent", "reason": "用户仅为普通问候，属于聊天智能体的业务范围"}
        
                用户输入：“昆明南屏街天气怎么样”
                输出：
                {"agent": "manager_agent", "reason": "用户询问昆明南屏街的天气情况，属于天气查询的业务场景"}
        
                用户输入：“我要北京市海淀区的规划”
                输出：
                {"agent": "m_agent", "reason": "用户请求北京市海淀区相关的规划内容，属于规划智能体的业务范围"}
        
                用户输入：“北京市海淀区今天会下雨吗”
                输出：
                {"agent": "manager_agent", "reason": "用户询问北京市海淀区是否下雨，属于天气查询的业务场景"}
         """
        return self.prompt.strip()  # 取消空格和换行，减少token消耗

    # 加载工具
    def get_tool(self):
        self.tool = []
        return self.tool

    # 加载智能体
    def get_agent(self):

        self.agent = create_agent(
            model=self.model,
            tools=self.tool,
            system_prompt=self.prompt
        )
        return self.agent

    # 同步聊天
    def chat_invoke(self, question):
        try:
            msg = {"messages": [{"role": "user", "content": question}]}
            rs = self.agent.invoke(msg)
            data = self.parse_json(rs["messages"][-1].content)
            return json.loads(data)
        except Exception as e:
            print(f"路由智能体出现异常:{e}")
            return "路由智能体出现异常"

    # 解析代码```json 格式的json字符串,兜底处理
    def parse_json(self, str):
        if str.startswith("```json"):
            data = str.replace("```json", "").replace("```", "")
            return data
        else:
            return str


if __name__ == "__main__":
    # ---------同步测试----------
    agent = RouterAgent()
    q = "你好"
    q1 = "帮我发一邮件"
    q2 = "我要北京市海淀区的规划"
    q3 = "双流区天气情况是什么"
    q4 = "为我查询云南省行政区域"
    rs = agent.chat_invoke(q4)
    print(rs)

