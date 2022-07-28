import contextvars
import json
import pathlib

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .game_manager import GameManager
from .message import Message

ROOT = pathlib.Path(__file__).parent

app = FastAPI()

game_manager_context: contextvars.ContextVar = contextvars.ContextVar("game_manager")
game_manager_context.set(GameManager())

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


@app.websocket("/update-code")
async def update_Code(websocket: WebSocket):
    """Handles changes between clients"""
    game_manager = game_manager_context.get()
    if game_manager is None:
        raise Exception("No GameManager instance")
    await websocket.accept()
    client_id, token = game_manager.add_client(websocket)
    await websocket.send_text(
        json.dumps(
            {
                "action": "assign_id",
                "user_id": client_id,
                "token": token,
                "problems": game_manager.get_problems(),
            }
        )
    )
    try:
        while True:
            data = Message(await websocket.receive_text())
            await game_manager.broadcast(client_id, data)
    except WebSocketDisconnect:
        game_manager.remove_client(client_id)


@app.get("/web-ide")
def web_ide(request: Request):
    """Returns HTML file containing the web IDE"""
    return templates.TemplateResponse("send-code.html", {"request": request})
