import redis
import json
from app.ai.agent.wether_agent.manager_agent import ManagerAgent
from app.ai.agent.walk_agent import WalkAgent
from app.ai.agent.recommendation_agent import RecommendationAgent
from app.ai.model.my_model import MyModel

class MAgent:
    def __init__(self):
        self.manager_agent = ManagerAgent()
        self.walk_agent = WalkAgent()
        self.recommendation_agent = RecommendationAgent()
        self.model = MyModel.get_local_model()
        self.client = redis.StrictRedis(host='localhost', port=6379, db=0)

    def save_session(self,user_id,session):
        key = f"session:{user_id}"
        self.client.set(key,json.dumps(session,ensure_ascii=False),ex=60)

    def load_session(self,user_id):
        key = f"session:{user_id}"
        data = self.client.get(key)
        if data:
            return json.loads(data)
        else:
            return {}

    async def chat(self,question,user_id):
        try:
            session = self.load_session(user_id)
            if session == {}:
                weather_data = None
                async for data in self.manager_agent.chat(question,user_id):
                    if isinstance(data, dict):
                        weather_data = data
                    yield data
                yield "\n正在为您查询附近推荐...\n"
                async for dt in self.recommendation_agent.chat(question):
                    yield dt
                session = {
                    "user_id":user_id,
                    "end_location":weather_data["address"],
                    "states":"wait"
                }
                self.save_session(user_id, session)
                yield "\n是否需要步行导航？（请回复“是”或“否”）\n"
            elif session["states"] == "wait":
                affirmative = ["是", "是的", "好", "可以", "行", "嗯", "yes", "y"]
                if question.strip() in affirmative:
                    session["states"] = "walk"
                    self.save_session(user_id, session)
                    yield "\n请输入您的位置\n"
                else:
                    yield "\n推荐结束！\n"
                    key = f"session:{user_id}"
                    self.client.delete(key)
            elif session["states"] == "walk":
                # start_location = question
                # end_location = session["end_location"]
                start_location = question
                end_location = session["end_location"]
                q = f"从{start_location}步行到{end_location}"
                async for rs in self.walk_agent.chat(q):
                    yield rs
                key = f"session:{user_id}"
                self.client.delete(key)
        except Exception as e:
            print(f"聊天智能体出现异常：{e}")
            yield "聊天智能体出现异常"


import asyncio
async def interactive_test():
    agent = MAgent()
    user_id = 1  # 可固定或让用户输入
    while True:
        question = input("\n您: ")
        if question.strip() == "退出":
            print("对话结束。")
            break
        print("\n智能体: ", end="")
        async for response in agent.chat(question, user_id):
            if isinstance(response, dict):
                print(response)
            else:
                print(response, end="", flush=True)  # 不换行，让流式输出更自然
        print()  # 换行

if __name__ == "__main__":
    asyncio.run(interactive_test())
