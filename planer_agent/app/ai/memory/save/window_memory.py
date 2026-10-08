import redis
import os
from dotenv import load_dotenv
import json

# 读取配置
load_dotenv()
"""
窗口记忆，记录最近4轮的窗口记忆
"""
class WindowMemory:
    def __init__(self,sessiong_id:int):
        self.client = redis.StrictRedis(host="localhost",port=6379,db=0)
        # 设置key
        self.key = f"chat_window_{sessiong_id}"
        # 获取轮次
        self.window_size = int(os.getenv("WINDOW_SIZE"))
        # 获取过期时间
        self.window_time = int(os.getenv("WINDOW_TIME"))
    # 添加记忆
    def add(self,role:str,content:str):
        # 构建一个字典
        msg = {"role":role,"content":content}
        # 序列化
        msg_json = json.dumps(msg,ensure_ascii=False)
        # 列表完成数据追加
        self.client.rpush(self.key,msg_json)
        # 设置窗口限制条数，剩下删除
        self.client.ltrim(self.key,-self.window_size,-1)
        # 设置过期时间
        self.client.expire(self.key,self.window_time)
    # 查询记忆
    def load(self):
        msg = self.client.lrange(self.key,0,-1)
        return [json.loads(x) for x in msg]

# 测试函数
def test():
    w = WindowMemory(1)
    # 模拟人类的消息添加
    w.add("user","你好")
    # 模拟AI回复消息
    w.add("ai","你好我是AI助手")
    # 模拟人类的消息添加
    w.add("user","你好1")
    # 模拟AI回复消息
    w.add("ai","你好1我是AI助手")
    # 模拟人类的消息添加
    w.add("user","你2好")
    # 模拟AI回复消息
    w.add("ai","你好2我是AI助手")
    # 查询记忆
    rs = w.load()
    print(rs)

if __name__ == "__main__":
    test()