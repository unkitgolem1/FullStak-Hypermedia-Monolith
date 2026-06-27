"""Entry point para desarrollo local sin DB.

Uso:  fastapi dev tests/run_dev.py
      python tests/run_dev.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import uvicorn
from fastapi import FastAPI
from routes import router

app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("run_dev:app", host="127.0.0.1", port=8000, reload=True)
