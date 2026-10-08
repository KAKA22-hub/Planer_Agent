import traceback

from fastapi import APIRouter
from fastapi import Request
import json
from starlette.responses import StreamingResponse
import redis
# 创建一个子路由程序
chat_router = APIRouter()

client = redis.StrictRedis(host='localhost', port=6379, db=0)
# 定义一个聊天接口
@chat_router.get("/chat")
async def chat(question:str,user_id,req:Request):
    key = f"plan:{user_id}"
    key1 = f"weather:{user_id}"
    try:
        if client.get(key):
            agent = req.app.state.m_agent
        elif client.get(key1):
            agent = req.app.state.manager_agent
        else:
            # 获取路由智能体返回结果
            router_agent = req.app.state.router_agent
            rs = router_agent.chat_invoke(question)
            # 获取智能体对象
            if rs["agent"] == "m_agent":
                agent = req.app.state.m_agent
                # 记录标识，表示当前会话是考试模式

                client.set(key,question,ex=60)
            elif rs["agent"] == "manager_agent":
                agent = req.app.state.manager_agent
                client.set(key1, question, ex=60)
            else:
                agent = req.app.state.chat_agent
        # 创建一个异步的流式输出迭代器
        async def generate(questiong: str):
            try:
                async for c in agent.chat(questiong, user_id):
                    if isinstance(c, dict):
                        if (
                                "address" in c
                                and "weather" in c
                                and "temperature" in c
                        ):
                            content = (
                                f"\n当前 {c['address']} 的天气为"
                                f"{c['weather']}，"
                                f"气温 {c['temperature']}℃。\n"
                            )
                        else:
                            content = json.dumps(c,ensure_ascii=False)
                    else:
                        content = c
                    data = {
                        "data": content,
                        "done": False
                    }
                    yield (
                        f"data:"
                        f"{json.dumps(data, ensure_ascii=False)}"
                        f"\n\n"
                    )
                # 流式输出结束，设置 done=True 表示关闭
                data = {"data":"","done":True}
                yield f"data:{json.dumps(data)}\n\n"
            except Exception as e:
                print(f"聊天流式异常:{e}")
                traceback.print_exc()
                data = {"data": "聊天流式异常", "done": True,"error":True}
                yield f"data:{json.dumps(data)}\n\n"
    except Exception as e:
        client.delete(key)
        client.delete(key1)
    return StreamingResponse(generate(question), media_type="text/event-stream")