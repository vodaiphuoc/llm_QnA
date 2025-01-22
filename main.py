from src.agent_v1 import Agent

from fastapi import FastAPI, Request, Response, Body, status, Depends
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


@asynccontextmanager
async def lifespan(app: FastAPI):
	logger.info("Setting up System")
	app.agent = Agent()

	yield
	logger.info("Turning down system")
	app.agent = None

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


@app.post("/chat", response_class=JSONResponse)
async def chat_router(query: Annotated[str, Body()] ,request: Request):
    
    try:
        return JSONResponse(status_code= 200, content=request.app.agent(query))
    except Exception as err:
	    return JSONResponse(status_code= 500, content='server error')


async def main_run():
    config = uvicorn.Config("main:app", 
    	port=5000, 
    	log_level="info", 
    	reload=True,
		reload_dirs= ["src/front_end/static", "src/front_end/templates"]
    	)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main_run())