from app.ai.memory.retrieval.long_agent import LongAgent
from app.ai.memory.retrieval.profile_agent import ProfileAgent
from app.ai.memory.retrieval.summary_agent import SummaryAgent
import os
from dotenv import load_dotenv

load_dotenv()
"""
记忆管理
"""
class MemoryManager:
    def __init__(self,conversation):
        self.long_agent = LongAgent(conversation.long_memory)
        self.profile_agent = ProfileAgent(conversation.profile_memory)
        self.summary_agent = SummaryAgent(conversation.summary_memory)
        self.window_memory = conversation.window_memory
        self.session_id = conversation.session_id
        self.user_id = conversation.user_id
    def update(self,question):
        self.long_agent.update(self.user_id,question)
        self.profile_agent.update(question)
        self.summary_agent.update(self.session_id,self.window_memory.load())