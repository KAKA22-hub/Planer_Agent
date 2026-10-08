from langchain.agents import create_agent
from app.ai.model.my_model import MyModel
import json
"""
用户画像记忆提取智能体：负责提取用户结构化数据，例如 姓名，年龄，性别，公司，职位
"""
class ProfileAgent:
    def __init__(self,profile_memory):
        self.model = MyModel.get_local_model()
        self.prompt = self.get_prompt()
        self.profile_memory = profile_memory
        self.agent = self.get_agent()
    def get_prompt(self):
        self.prompt = """
              一: 你是一个用户画像记忆提取助手
              二：任务
                     1 从用户问题提取结构化数据，例如 姓名，年龄，性别，公司，职位
                     2 如果没有结构化数据，则返回0
                     3 如果用结构化数据，则返回：键名:键值 键名必须是英文
                       示例：
                          我叫张三 ，返回 name:张三
              三：输出  
                  - 只输出 JSON
                  - 不允许输出 Markdown
                  - 不允许输出 ```json
                  - 不允许输出解释说明
                  - 不允许输出多个 JSON
                  - 不允许输出任何额外文字
                  - JSON 必须能够被 `json.loads()` 正确解析
        """
        return self.prompt
    def get_agent(self):
        self.agent = create_agent(
            model=self.model,
            tools=[],
            system_prompt=self.prompt,
        )
        return self.agent
    def update(self,question):
        rs = self.agent.invoke({"messages":[{"role":"user","content":question}]})
        answer = rs["messages"][-1].content
        data = json.loads(answer)
        if not data:
            return {}
        for key,value in data.items():
            self.profile_memory.add(key,value)
        return data


def test():
    from app.ai.memory.save.profile_memory import ProfileMemory
    p = ProfileMemory(1)
    agent = ProfileAgent(p)
    q1="我叫王五"
    q2="我的公司是华清远见"
    q3="你好，你是谁"
    rs = agent.update(q2)
    print(rs)

if __name__ == "__main__":
    test()