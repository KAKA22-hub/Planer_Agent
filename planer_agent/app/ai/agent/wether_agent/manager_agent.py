import redis
import json
from app.ai.agent.wether_agent.get_adcode_agent import AdcodeAgent
from app.ai.agent.wether_agent.get_weather_agent import WeatherAgent
from app.ai.agent.wether_agent.getadm_agent import AdmAgent
from app.ai.agent.wether_agent.intent_agent import IntentAgent

"""
    天气查询主管智能体
"""
class ManagerAgent:
    def __init__(self):
        self.adcode_agent = AdcodeAgent()
        self.weather_agent = WeatherAgent()
        self.intent_agent = IntentAgent()
        self.adm_agent = AdmAgent()
        self.client = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.ad_list = []

    def save_session(self,user_id,session):
        key = f"session:{user_id}"
        self.client.set(key,json.dumps(session,ensure_ascii=False),ex=3600)

    def load_session(self,user_id):
        key = f"session:{user_id}"
        data = self.client.get(key)
        if data:
            return json.loads(data)
        else:
            return {}

    async def judgment(self,c,l,user_id,session):
        ad_l = []
        async for ad in self.adm_agent.chat(c):
            ad_l.append(ad)
        if l in ad_l:
            session["state"] = 0
            yield True
        else:
            yield False

    async def chat(self,question,user_id):
        session = self.load_session(user_id)
        if session == {}:
            yield "\n正在识别地址...\n"
            intent = self.intent_agent.chat(question)
            session = {
                "city":intent["city"],
                "location":intent["location"],
                "state":1
            }
            self.save_session(user_id,session)
        if session["state"] == 1:
            jud = self.judgment(session["city"],session["location"],user_id,session)
            if jud:
                ad = f"{session["city"]},{session["location"]}"
                # print(ad)
                async for code in self.adcode_agent.chat(ad):
                    # print(code)
                    async for weather in self.weather_agent.chat(code):
                        yield weather
                key = f"session:{user_id}"
                self.client.delete(key)
            else:
                yield "该地址不存在，请重新输入"
                key = f"session:{user_id}"
                self.client.delete(key)

async def test(q):
    manager = ManagerAgent()
    async for data in manager.chat(q,1):
        print(data)

if __name__ == "__main__":
    import asyncio
    q = "我要查询北京市朝阳区和海淀区的天气情况"
    q1 = "双流区天气情况是什么"
    q2 = "我想查询昆明天气"
    asyncio.run(test(q))
