from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
from pathlib import Path
from dotenv import load_dotenv
from markdown import markdown as md_convertir

from database import SupabaseAdaptador, Repository_documento

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "static" / "templates"))

PATH_AL_ENV = BASE_DIR / ".env"
load_dotenv(dotenv_path=PATH_AL_ENV)
DATABASE_URL = os.environ.get("DATABASE_URL")
adaptador_supabase = SupabaseAdaptador(DATABASE_URL)


def obtener_db() -> Repository_documento:
    return adaptador_supabase


@router.get("/", response_class=HTMLResponse)
async def principal_route(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@router.get("/api/obtener-documentos", response_class=HTMLResponse)
async def obtener_documentos(
    request: Request, db: Repository_documento = Depends(obtener_db)
):
    # traer el dato de la db
    documentos = await db.obtener_todos_documentos()  # Traer los datos de la db
    if not documentos: 
        print(f"Documentos obtenidos: {documentos}")
    return templates.TemplateResponse(
        request=request,
        name="documentos_fragmento.html",
        context={"documentos": documentos},
    )


@router.get("/api/contenido-md/{documento_id}", response_class=HTMLResponse)
async def contenido_md(
    request: Request,
    documento_id: int,
    db: Repository_documento = Depends(obtener_db),
):
    doc = await db.obtener_documento_por_id(documento_id)
    if not doc or not doc.get("content_md"):
        return "<p class='text-slate-400 text-center py-8 font-mono'>— Sin contenido disponible —</p>"

    html = md_convertir(
        doc["content_md"],
        extensions=["fenced_code", "codehilite"],
    )
    titulo = doc["titulo"]
    return f"""
<h2 class="text-xl font-bold text-slate-100 font-mono mb-4 tracking-tight">{titulo}</h2>
<div class="markdown-body text-sm leading-relaxed">
    {html}
</div>
"""
