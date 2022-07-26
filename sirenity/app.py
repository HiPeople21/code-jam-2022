import json

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
def index(request: Request):
    """The main site page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/create")
def game(request: Request):
    """The game creation form"""
    return templates.TemplateResponse("create.html", {"request": request})


# Game manager class can handle the next few lines
clients = set()
next_id = 0


@app.websocket("/update-code")
async def update_Code(websocket: WebSocket):
    """Handles changes between clients"""
    global change, next_id
    await websocket.accept()
    clients.add(websocket)
    await websocket.send_text(json.dumps({"action": "id", "user_id": next_id}))
    next_id += 1
    try:
        while True:
            data = json.loads(await websocket.receive_text())
            for client in clients:
                if client == websocket:
                    continue
                await client.send_text(json.dumps(data))
    except WebSocketDisconnect:
        clients.remove(websocket)


@app.get("/web-ide")
def web_ide(request: Request):
    """Returns HTML file containing the web IDE"""
    return templates.TemplateResponse("send-code.html", {"request": request})
