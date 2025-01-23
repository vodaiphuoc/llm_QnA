from src.agent_v1 import Agent

from fastapi import FastAPI, Request, Response, Body, status, Depends, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder

from pydantic import BaseModel, Field
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from typing import List, Any, Annotated, Literal, Union, Dict
from typing import Annotated

import json
import re
from contextlib import asynccontextmanager
from loguru import logger
import asyncio
import uvicorn

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Setting up System")
    app.manager = ConnectionManager()
    app.agent = Agent()

    yield
    logger.info("Turning down system")
    app.agent = None
    app.manager = None

app = FastAPI(lifespan = lifespan)
app.mount(path = '/templates', 
          app = StaticFiles(directory='src/front_end/templates', html = True), 
          name='templates')

app.mount(path = '/static',
          app = StaticFiles(directory='src/front_end/static', html = False), 
          name='static')

origins = [
    "http://localhost",
    "http://localhost:8080/",
    "http://localhost:8000/",
    "http://127.0.0.1:8000/",
    "http://127.0.0.1:8000"
]
app.add_middleware(CORSMiddleware, 
                   allow_origins=origins,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"]
                   )
templates = Jinja2Templates(directory='src/front_end/templates')

@app.get("/", response_class=HTMLResponse)
async def index_router(request: Request):
    return templates.TemplateResponse(
		request = request,
		name = "index.html"
		)


@app.websocket("/ws")
async def chat_router(websocket: WebSocket):
    await websocket.app.manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            user_message = data['user_message']
            agent_response = websocket.app.agent(user_message)
            await websocket.app.manager.send_personal_message(message = agent_response, 
                                                websocket= websocket)

    except WebSocketDisconnect:
        websocket.app.manager.disconnect(websocket)


async def main_run():
    config = uvicorn.Config("main:app", 
    	port=8080, 
    	log_level="info", 
    	reload=True,
		reload_dirs= ["src/front_end/static", "src/front_end/templates"]
    	)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main_run())