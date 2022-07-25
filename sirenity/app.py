import pathlib

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

ROOT = pathlib.Path(__file__).parent

app = FastAPI()

app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
templates = Jinja2Templates(directory=ROOT / "templates")


@app.get("/")
def index(request: Request):
    """The main site page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/create")
def game(request: Request):
    """The game creation form"""
    return templates.TemplateResponse("create.html", {"request": request})
