from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from docx import Document
import tempfile
import os

client = OpenAI()

app = FastAPI()

# CORS so the HTML from http://localhost:5500 can call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev; narrow later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    # Save uploaded audio to a temp file
    suffix = os.path.splitext(file.filename)[-1] or ".tmp"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    # Call Whisper (or your chosen STT) to get text
    with open(tmp_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text",
        )

    # Build DOCX file
    doc = Document()
    doc.add_paragraph(transcription)
    docx_path = tmp_path + ".docx"
    doc.save(docx_path)

    # Let the browser download it
    return FileResponse(
        docx_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename="transcription.docx",
    )
