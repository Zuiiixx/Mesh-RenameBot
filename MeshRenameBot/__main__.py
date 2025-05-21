from .core.get_config import get_var
from .core.handlers import add_handlers
from .mesh_bot import MeshRenameBot
from .maneuvers.ExecutorManager import ExecutorManager
import logging

import threading
from fastapi import FastAPI
import uvicorn

def start_health_server():
    app = FastAPI()

    @app.get("/")
    def health():
        return {"status": "ok"}

    uvicorn.run(app, host="0.0.0.0", port=8080)

# Start health check server in background
threading.Thread(target=start_health_server, daemon=True).start()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s"
)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

# MAIN ENTRY POINT
if __name__ == "__main__":

    rbot = MeshRenameBot(
        session_string=get_var("SESSION_STRING"),
        api_id=get_var("API_ID"),
        api_hash=get_var("API_HASH"),
        workers=200
    )
    
    excm = ExecutorManager()
    add_handlers(rbot)
    rbot.run()