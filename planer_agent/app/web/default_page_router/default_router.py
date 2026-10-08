from fastapi import APIRouter
from fastapi.responses import RedirectResponse
default_router = APIRouter()

@default_router.get("/")
async def default_page():
    return RedirectResponse(url="/static/login.html")