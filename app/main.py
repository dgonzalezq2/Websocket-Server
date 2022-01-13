# from fastapi import FastAPI, WebSocket

# from fastapi.responses import HTMLResponse

# import logging 
# import websockets

# _logger = logging.getLogger(__name__)

# app = FastAPI()

# html = """

# <!DOCTYPE html>

# <html>

#     <head>

#         <title>Chat</title>

#     </head>

#     <body>

#         <h1>WebSocket Chat</h1>

#         <form action="" onsubmit="sendMessage(event)">

#             <input type="text" id="messageText" autocomplete="off"/>

#             <button>Send</button>

#         </form>

#         <ul id='messages'>

#         </ul>

#         <script>

#             var ws = new WebSocket("ws://127.0.0.1:8080/ws");

#             ws.onmessage = function(event) {

#                 var messages = document.getElementById('messages')

#                 var message = document.createElement('li')

#                 var content = document.createTextNode(event.data)

#                 message.appendChild(content)

#                 messages.appendChild(message)

#             };

#             function sendMessage(event) {

#                 var input = document.getElementById("messageText")

#                 ws.send(input.value)

#                 input.value = ''

#                 event.preventDefault()

#             }

#         </script>

#     </body>

# </html>

# """

# # @app.get("/")

# # async def get():

# #     return HTMLResponse(html)

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     while True:
#         data = await websocket.receive_text()
#         _logger.warning(data)
#         await websocket.send_text(f"Message text was: {data}")

from typing import List
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from starlette.websockets import WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import logging

app = FastAPI()

origins = [
    "https:insitedev.infinit-plus.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

logger=logging.getLogger() 


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")