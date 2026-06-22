from contextlib import asynccontextmanager

from fastapi import FastAPI
from routes import router as landing_web
from routes import adaptador_supabase as db


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Estableciendo conexion con la db")
    await db.conectar()
    yield
    print("Ya terminamos de usar la db, desconectando")
    await db.desconectar()


app = FastAPI(lifespan=lifespan)
app.include_router(landing_web, prefix="/web")
