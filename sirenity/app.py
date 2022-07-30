import pathlib

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .game_manager import GameManager
from .message import JoinMessage, Message

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


@app.websocket("/update-code")
async def update_Code(websocket: WebSocket):
    """Handles changes between clients"""
    game_manager = app.game_manager  # type: ignore
    if game_manager is None:
        raise Exception("No GameManager instance")
    await websocket.accept()
    client_id, token = game_manager.add_client(websocket)
    await websocket.send_text(
        str(
            JoinMessage(
                action="assign_id",
                user_id=client_id,
                token=token,
                data={"problems": game_manager.get_problems()},
            )
        )
    )

    game_manager.start()

    try:
        while True:
            data = Message(await websocket.receive_text())
            if data.action == "submitCode":
                code = game_manager.get_code(data)
                code  # run and check code
                continue
            elif data.action == "requestCode" and game_manager.started:

                await game_manager.request_code(websocket)
            if game_manager.waiting_for_code_request:
                if (
                    game_manager.clients[data.user_id].websocket
                    == game_manager.first_client
                ):
                    await game_manager.send_requested_code(data)

            await game_manager.broadcast(client_id, data)
    except WebSocketDisconnect:
        game_manager.remove_client(client_id)


@app.get("/web-ide")
def web_ide(request: Request):
    """Returns HTML file containing the web IDE"""
    return templates.TemplateResponse("send-code.html", {"request": request})


@app.on_event("startup")
def startup():
    """Sets GameManager"""
    app.game_manager = GameManager()  # type: ignore


@app.on_event("shutdown")
def shutdown():
    """Closes resources"""
    del app.game_manager
