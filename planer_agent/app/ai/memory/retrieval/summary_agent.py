from langchain.agents import create_agent
from app.ai.model.my_model import MyModel
"""
摘要智能体：负责提取用户摘要记忆
"""
class SummaryAgent:
    def __init__(self,summary_memory):
        self.model = MyModel.get_local_model()
        self.summary_memory = summary_memory
        self.prompt = self.get_prompt()
        self.agent = self.get_agents()
    def get_prompt(self):
        self.prompt = """
            一: 你是一个对话摘要助手
              你的任务：根据【历史摘要】和【最近聊天记录】生成新的摘要。
              要求：
              1、保留重要信息
              2、去掉闲聊内容
              3、避免重复
              4、控制在200字以内
              5、使用第三人称描述
              6、只返回新的摘要 
              7、如果历史摘要或最近聊天记录为空，则返回0
        """
        return self.prompt
    def get_agents(self):
        self.agent = create_agent(
            model=self.model,
            tools=[],
            system_prompt=self.prompt
        )
        return self.agent
    def update(self,session_id,message):
        # 获取历史摘要记录
        history = self.summary_memory.load_memory(session_id)
        # 最新消息
        new_msg = ""
        # 获取窗口记忆信息
        for x in message:
            new_msg += f"{x["role"]}:{x["content"]}\n"
        #print(f"最新消息：{new_msg}")
        #print(f"历史摘要：{history}")
        # 拼接问题
        question = f"历史摘要：{history}\n最新消息：{new_msg}"
        # 提问
        rs = self.agent.invoke({"messages":[{"role":"user","content":question}]})
        # 答案
        answer = rs["messages"][-1].content
        # 保存摘要记忆
        if answer != '0':
            self.summary_memory.add_memory(session_id,answer)
        return answer

# 测试方法
def test():
    from app.ai.memory.save.summary_memory import SummaryMemory
    from app.ai.memory.save.window_memory import WindowMemory
    s = SummaryMemory()
    w = WindowMemory(4)
    agent = SummaryAgent(s)
    rs = agent.update(4,w.load())
    print(rs)
if __name__ == "__main__":
    test()