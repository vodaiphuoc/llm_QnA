from src.llms import Gemini_Inference

from src.data_models import Example, UserResponse, SingleUserAnswer

from fastapi import FastAPI, Request, Response,Form, File, UploadFile, Body, status, Depends
from fastapi.encoders import jsonable_encoder

from pydantic import BaseModel, Field
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
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
	app.data_loader = ReadingQuestionLoader()
	app.llm_model = Gemini_Inference()

	yield
	logger.info("Turning down system")
	app.data_loader = None
	app.llm_model = None


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