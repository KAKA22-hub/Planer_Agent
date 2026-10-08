from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from app.ai.agent import router_agent
from app.ai.agent.m_agent import MAgent
from app.ai.agent.chat_agent import ChatAgent
from app.ai.agent.router_agent import RouterAgent
from app.ai.agent.wether_agent.manager_agent import ManagerAgent
from app.web.chat_router.chat_router import chat_router
from app.web.system_router.system_router import system_router
from fastapi.staticfiles import StaticFiles
from app.web.default_page_router.default_router import default_router


@asynccontextmanager
async def  contenttextManger(app: FastAPI):
    app.state.chat_agent = ChatAgent()
    app.state.manager_agent = ManagerAgent()
    app.state.m_agent = MAgent()
    app.state.router_agent = RouterAgent()
    print("创建智能体")
    yield
    print("销毁智能体")
    app.state.chat_agent = None
    app.state.manager_agent = None
    app.state.m_agent = None
    app.state.router_agent = None

app  = FastAPI(lifespan=contenttextManger)

app.include_router(system_router)

app.include_router(chat_router)

app.include_router(default_router)
app.mount("/static", StaticFiles(directory="./html"), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8001)