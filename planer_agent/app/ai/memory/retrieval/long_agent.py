from langchain.agents import create_agent
from app.ai.model.my_model import MyModel
"""
长期智能体：负责提取用户长期记忆
"""
class LongAgent:
    def __init__(self,long_memory):
        self.model = MyModel.get_local_model()
        self.prompt = self.get_prompt()
        self.long_memory = long_memory
        self.agent = self.get_agent()
    def get_prompt(self):
        self.prompt = """
            一: 你是一个长期记忆提取助手
            二：任务：
                 1 从用户的问题中提取关键信息，例如：
                    兴趣，偏好，技能，
                    身份
                    示例：我是一个人工智能工程师
                    则返回：人工智能工程师
                 2 只返回提取的关键信息，只返回一句话，不需要做任何解释
                 3 如果没有关键信息，则返回0
        """
        return self.prompt
    def get_agent(self):
        self.agent = create_agent(
            model=self.model,
            tools=[],
            system_prompt=self.prompt,
        )
        return self.agent
    def update(self,user_id,question):
        rs = self.agent.invoke({"messages":[{"role":"user","content":question}]})
        answer = rs["messages"][-1].content
        if answer != 0:
            self.long_memory.add_memory(user_id,answer)
        return answer

def test():
    from app.ai.memory.save.long_memory import LongMemory
    l = LongMemory()
    agent = LongAgent(l)
    q1="我喜欢编程"
    q2="我是一个人工智能工程师"
    q3="你好，你是谁"
    rs = agent.update(1,q2)
    print(rs)

if __name__ == "__main__":
    test()