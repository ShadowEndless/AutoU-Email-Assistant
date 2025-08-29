import os
import io
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pypdf import PdfReader

from .classifier import classify_email
from .db import init_db, salvar_classificacao, listar_classificacoes

ROOT = os.path.dirname(os.path.dirname(__file__))
FRONTEND_DIR = os.path.join(ROOT, "frontend")
INDEX_HTML = os.path.join(FRONTEND_DIR, "index.html")

app = FastAPI(title="AutoU Email Assistant", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir frontend
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# Inicializa banco
init_db()

@app.get("/", response_class=HTMLResponse)
def root():
    return FileResponse(INDEX_HTML)

@app.post("/api/classify")
async def api_classify(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    remetente: Optional[str] = Form(None),
    assunto: Optional[str] = Form(None),
    use_llm: Optional[bool] = Form(False),
):
    content = (text or "").strip()

    if file and file.filename:
        fname = file.filename.lower()
        data = await file.read()
        if fname.endswith(".pdf"):
            try:
                reader = PdfReader(io.BytesIO(data))
                pages = [p.extract_text() or "" for p in reader.pages]
                content = "\n".join(pages).strip()
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Falha ao ler PDF: {e}")
        elif fname.endswith(".txt"):
            try:
                content = data.decode("utf-8", errors="ignore")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Falha ao ler TXT: {e}")
        else:
            raise HTTPException(status_code=400, detail="Formato não suportado. Envie .txt ou .pdf")

    if not content:
        raise HTTPException(status_code=400, detail="Nenhum conteúdo enviado.")

    result = classify_email(content, use_llm=bool(use_llm))

    # Salvar no banco
    salvar_classificacao(
        conteudo=content,
        tipo=result["category"],
        subtipo=result["subtype"],
        confianca=result["confidence"],
        remetente=remetente,
        assunto=assunto
    )

    return JSONResponse(result)

@app.get("/api/logs")
async def logs():
    return listar_classificacoes()

