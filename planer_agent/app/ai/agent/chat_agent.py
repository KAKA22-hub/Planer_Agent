import traceback
from app.ai.tool.getadm_tool import get_administration_tool
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.memory import InMemorySaver
import redis
from langchain.agents import create_agent
from app.ai.tool.location_sql_tool import location_sql_tool
from app.ai.model.my_model import MyModel
from app.ai.tool.send_email_tool import send_email_tool
from app.ai.memory.memory_manager import MemoryManager
from app.ai.memory.save.conversation_manger import ConversationManager

"""
 聊天的智能体
"""
class ChatAgent:

     def __init__(self):
       # self.client = redis.StrictRedis(host="localhost", port=6379, db=0)
        self.model_memory = MyModel.get_local_model()
        self.model = MyModel.get_line_model()
        self.prompt = self.get_prompt()
        self.tool  = self.get_tool()
        self.agent = self.get_agent()

    # 加载提示词
     def get_prompt(self):
         self.prompt ="""
            一 角色：你是一个AI多功能助手
            二 任务：
                - 若用户问题含义有'发送通知'，'发送邮件','发送消息',请走发送邮件流程
                - 若用户问题含义包含“行政区域查询”、“行政区划”、“地区查询”、“省份/城市/区县查询”等关键词，请走行政区域查询流程。
            三 发送邮件流程步骤如下：
                你必须严格按照以下步骤来执行
                    步骤一：请根据用户问题分析出邮件的收件人，邮件标题，邮件内容，邮件内容模板必须是以下格式
                        xxx 你好：
                            邮件内容
                                    发送人：xxx（若没有明确指出发送人，则默认填为boss）
                                公司地址：成都市金牛区二环路北一段53号4-5层
                                手机号码：18030730086
                                电话号码：028-85405115
                                咨询热线：400-611-6270
                                电子邮件：yanzz_cd@hqyj.com
                                集团官网：www.hqyj.com 
                                创客学院：www.makeru.com.cn 
                                研发中心：www.fsdev.com.cn
                    步骤二：调用工具 send_email_tool 发送邮件
            四 行政区域查询流程步骤如下：
                严格按照下列步骤进行执行任务：
                    步骤一: 根据用户的问题，分析出希望查询的行政区域地址作为'keywords'，以及查询的行政区域级数作为'subdistrict'
                    步骤二：若用户没有明确说明想查询行政区域级数，则默认查询2级
                    步骤三：调用工具 get_administration_tool 传入 'keywords' 和 'subdistrict' 参数，查询地址行政区域信息。
            四 规则
                - 你必须严格按照上述流程步骤执行，不可跳过或合并步骤。
                - 若用户输入不完整或信息缺失（如缺少收件人、邮件标题、地名等），应主动向用户询问补充，而非自行猜测。
                - 所有工具调用前需确保参数格式正确，若调用失败，需向用户说明错误原因并建议修改输入。
         """
         return self.prompt
     #加载工具
     def get_tool(self):
         self.tool =[send_email_tool,get_administration_tool]
         return self.tool

     #加载智能体
     def get_agent(self):

         self.agent=create_agent(
             model=self.model,
             tools=self.tool,
             system_prompt=self.prompt,
             middleware=[SummarizationMiddleware(
                 model=self.model_memory,
                 max_tokens_before_summary=150,  # 超过多少 Token 就触发摘要
                 max_tokens_after_summary=150,  # 摘要完成后，希望压缩到多少 Token 左右
                 min_tokens=150,  # 最低 Token 阈值，低于这个值不进行摘要
                 # messages_to_keep=2  # 摘要时保留最近多少条原始消息
             )],
             checkpointer=InMemorySaver(), # 添加记忆功能检测点
         )
         return self.agent


     #同步聊天
     def chat_invoke(self,question):
         try:
            msg ={"messages":[{"role":"user","content":question}]}
            rs = self.agent.invoke(msg)
            return rs["messages"][-1].content
         except Exception as e:
            print(f"同步聊天出现异常:{e}")
            return "同步聊天出现异常"
     #异步聊天
     async  def chat(self,question,user_id):
         try:
            # 添加四层记忆
            c = ConversationManager(user_id,user_id,question)
            m = MemoryManager(c)
            # 添加窗口记忆用户问题
            c.add_window("user",question)
            # 构建记忆的提示词
            memory_prompt = c.add_prompt()
            # 构建一个系统角色消息
            sys_msg = {"role":"system","content":memory_prompt}
            msg ={"messages":[{"role":"user","content":question},sys_msg]}
            config = {"configurable":{"thread_id":user_id}}

            rs =self.agent.astream_events(msg,config,version="v2")
            ai_msg = ""
            async for event in rs:
                #获取事件类型
                event_type = event["event"]
                if event_type =="on_tool_start":
                    yield f"\n 开始执行工具:{event["name"]}\n"
                if event_type == "on_tool_end":
                    yield f"\n 工具:{event["name"]} 执行完毕\n"
                if event_type == "on_chat_model_stream":
                    metadata = event.get("metadata",{})
                    # 摘要模型的输出，不发送给前端
                    if metadata.get("lc_source") == "summarization":
                        continue
                    if event["data"]["chunk"].content:
                        # 累计ai回复消息
                        ai_msg += event["data"]["chunk"].content
                        yield f"{event["data"]["chunk"].content}"

            # 添加窗口记忆ai问题
            c.add_window("ai",ai_msg)
            m.update(question)

         except Exception as e:
            print(f"同步聊天出现异常:{e}")
            traceback.print_exc()
            yield "同步聊天出现异常"
#测试流式输出
async def test_stream(question):
    agent = ChatAgent()
    async for data in  agent.chat(question,1):
        print(data,end="")
if __name__ =="__main__":
    import asyncio
    q2 = "你是谁"
    asyncio.run(test_stream(q2))

