from __future__ import annotations

import shutil
import fitz
import tempfile
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from graph import run_pipeline
from llm import answer_question
from pydantic import BaseModel
from typing import Optional, List
import json as json_lib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # <-- 1. Import the tool

app = FastAPI(title="Hack2Heal Report Analysis Service")

# 2. Define who is allowed to talk to your FastAPI server
origins = [
    "http://localhost:8080", 
    "http://127.0.0.1:8080",
]

# 3. Inject the CORS logic into your FastAPI app pipeline
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Allows port 8080 to send requests
    allow_credentials=True,
    allow_methods=["*"],              # Allows GET, POST, etc.
    allow_headers=["*"],              # Allows all network headers
)

class Metric(BaseModel):
    name: str
    value: float
    unit: str
    reference_range: Optional[str] = None
    flag: str  # "normal" | "high" | "low" | "unknown"

class AnalysisResult(BaseModel):
    metrics: List[Metric]
    summary: str
    risk_score: float
    raw_text: str

@app.get("/health")
def health():
    """Simple check Spring Boot (or you) can hit to confirm the service is up."""
    return {"status": "ok"}

@app.post("/page-count")
async def page_count(file: UploadFile = File(...)):
    await file.seek(0) 
    
    contents = await file.read()
    doc = fitz.open(stream=contents, filetype="pdf")
    count = len(doc)
    doc.close()
    return {"page_count": count}


@app.post("/analyze", response_model=AnalysisResult)
async def analyze(file: UploadFile = File(...), page_numbers: Optional[str] = Form(None)):
    """
    Accepts a PDF report, runs it through the LangGraph pipeline
    (OCR -> page filter -> Groq extraction), and returns structured JSON.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Save the uploaded file to a temp path - the pipeline works off disk paths
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        pages = None
        if page_numbers:
            cleaned = page_numbers.strip().strip("[]")
            pages = [int(p.strip()) for p in cleaned.split(",") if p.strip()]
        output = run_pipeline(tmp_path, page_numbers=pages)
        
    finally:
        Path(tmp_path).unlink(missing_ok=True)  # clean up temp file either way

    if "error" in output:
        raise HTTPException(status_code=500, detail=output["error"])

    return output["result"]

@app.post("/ask")
async def ask(report_text: str = Form(...), question: str = Form(...)):
    answer = answer_question(report_text, question)
    return {"answer": answer}