import json
import traceback

from langchain.agents import create_agent
from app.ai.model.my_model import MyModel

"""
    意图智能体
"""
class IntentAgent:
    def __init__(self):
        self.model = MyModel.get_local_model()
        self.prompt = self.get_prompt()
        self.tool = self.get_tool()
        self.agent = self.get_agent()

    def get_prompt(self):
        self.prompt = """
 一：角色
                你是一个意图识别与参数提取智能体，负责根据用户输入，判断用户想要查询哪个位置的天气，并提取位置信息。

            二：任务
                从用户输入中识别目标城市（仅限中国所属城市）以及具体位置信息（相同或位于该城市下一级的行政区），并按指定 JSON 格式输出。

            三：规则
                1. 目标城市必须从用户输入中明确识别。若输入中同时出现多个城市或多个位置，则以最后描述的位置为准，只保留最后出现的区。
                   例如：我要查询北京市朝阳区和海淀区的天气情况。
                   结果：
                   {"city": "北京市", "location": "海淀区"}

                2. 首先识别 city，具体位置信息 location 必须从用户输入中明确识别。
                   若用户只描述了市，没有明确下一级行政区，则 location 返回与 city 相同的值。
                   例如：查询成都市气温。
                   结果：
                   {"city": "成都市", "location": "成都市"}

                3. 若无法从用户输入中识别任何城市或地址，则 city 和 location 都返回字符串 "0"。
                   例如：我想查询天气。
                   结果：
                   {"city": "0", "location": "0"}

                4. 不允许出现例如：
                   {"city": "", "location": "成都市"}
                   这样的结果。
                   若只识别到一个地址，则 city 和 location 都填写该地址。

                5. city 和 location 的值必须使用英文双引号包裹。

                6. 仅输出一个合法 JSON 对象，不附加任何解释、标记或额外文字。

                7. 不允许输出 ```json，不允许输出 Markdown 代码块，不允许输出分析过程。

            四：输出
                输出格式固定为：
                {"city": "<上级行政区>", "location": "<相同或下一级行政区>"}

            五：示例
                用户输入：“我要查询北京市朝阳区和海淀区的天气情况”
                输出：
                {"city": "北京市", "location": "海淀区"}

                用户输入：“北京市朝阳区天气怎么样”
                输出：
                {"city": "北京市", "location": "朝阳区"}

                用户输入：“查询吉林省长春市朝阳区气温”
                输出：
                {"city": "长春市", "location": "朝阳区"}

                用户输入：“查询成都市气温”
                输出：
                {"city": "成都市", "location": "成都市"}

                用户输入：“我想查询天气”
                输出：
                {"city": "0", "location": "0"} 
        """
        return self.prompt
    def get_tool(self):
        self.tool = None
        return self.tool
    def get_agent(self):
        self.agent = create_agent(
            model=self.model,
            tools=self.tool,
            system_prompt=self.prompt,
        )
        return self.agent
    def parse_json(self,st):
        if st.startswith("```json"):
            data = st.replace("```json","").replace("```","")
            return data
        else:
            return st
    def chat(self,question):
        try:
            msg = {"messages":[{"role":"user","content":question}]}
            rs = self.agent.invoke(msg)
            # print(rs["messages"][-1].content)
            data = self.parse_json(rs["messages"][-1].content)
            return json.loads(data)
        except Exception as e:
            print(
                f"意图智能体出现异常："
                f"{type(e).__name__}: {e}"
            )
            traceback.print_exc()
            return {
                "city": "0",
                "location": "0",
                "error": True
            }

if __name__ == "__main__":
    agent = IntentAgent()
    q1 = "我要查询北京市朝阳区和海淀区的天气情况"
    q2 = "我想查询昆明天气"
    q3 = "我想查询天气"
    rs = agent.chat(q2)
    print(rs)
    print(type(rs))