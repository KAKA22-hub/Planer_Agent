from dotenv import load_dotenv
import os
from pydantic import BaseModel,Field
from langchain.tools import tool
from email.mime.text import MIMEText
import smtplib
'''
    用 pydantic 封装邮件工具需要的参数
'''

class EmailParams(BaseModel):
    #...参数必填，description 必须描述准确，否则无法调用
    to:str = Field(...,description="收件人邮箱")
    subject:str = Field(...,description="邮件主题")
    content:str = Field (...,description="邮件内容")

load_dotenv()

#函数调用方式改变，必须符合 langchain 的 invoke 接口
@tool("send_email_tool",args_schema=EmailParams)#（）中方法名称，可以省略，默认下面第一个
def send_email_tool(to:str,subject:str,content:str)->str:
    # 这也是提示词一部分，帮助ai判断是否调用
    """
    功能描述：发送邮件，发送信息，发送通知
    """
    # 防止模型卡住，设置异常处理
    try:
        #读取邮件的配置
        host = os.getenv("EMAIL_HOST")
        user = os.getenv("EMAIL_USER")
        password = os.getenv("EMAIL_PASSWORD")
        port = os.getenv("EMAIL_PORT")
        if not host or not user or not password or not port:
            return "请检查邮件配置"
        #1 创建邮件对象，并引入正文,python 自带发送邮件的包
        msg = MIMEText(content)
        #2 收件人
        msg["To"] = to
        #3标题
        msg["Subject"] = subject
        #4 发件人
        msg["From"] = user
        #5 登录邮件服务器
        with smtplib.SMTP_SSL(host,int(port)) as smtp:
            # 登录
            smtp.login(user,password)
            #发送邮件
            smtp.sendmail(msg["From"],msg["To"],msg.as_string())
        return "邮件发送成功"

    except Exception as e:
        print(f"出现异常{e}")
        return "发送邮件异常"

if __name__=="__main__":
    send_email_tool.invoke({
        "to":"3335281906@qq.com",
        "subject":"测试邮件",
        "content":"测试邮件内容"
    })