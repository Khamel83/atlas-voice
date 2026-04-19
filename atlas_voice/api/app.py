"""FastAPI application for Atlas Voice."""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from typing import List, Optional
import tempfile
import shutil

from atlas_voice.storage import Database
from atlas_voice.services import ImportService, AnalyzerService, GeneratorService
from atlas_voice.models import VoicePattern, VoicePrompt


app = FastAPI(
    title="Atlas Voice",
    description="Generate AI voice prompts from your writing patterns",
    version="1.0.0"
)

# Mount static files
web_dir = Path(__file__).parent.parent.parent / "web"
if web_dir.exists():
    app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "atlas-voice"}


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main web interface."""
    html_file = web_dir / "index.html"
    if html_file.exists():
        return html_file.read_text()
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Atlas Voice</title>
    </head>
    <body>
        <h1>Atlas Voice</h1>
        <p>Web interface not found. Please run from CLI: atlas-voice --help</p>
    </body>
    </html>
    """


@app.post("/api/import")
async def import_file(
    file: UploadFile = File(...),
    file_type: str = Form("auto"),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    """Import a file and analyze it."""
    # Save uploaded file to temp location
    temp_dir = Path(tempfile.mkdtemp())
    temp_file = temp_dir / file.filename

    try:
        with temp_file.open("wb") as f:
            shutil.copyfileobj(file.file, f)

        # Import
        importer = ImportService()
        file_type_actual = None if file_type == "auto" else file_type
        texts = importer.import_file(str(temp_file), file_type_actual)

        if not texts:
            raise HTTPException(status_code=400, detail="No text could be extracted from file")

        # Analyze
        analyzer = AnalyzerService()
        profile_name = name or f"Profile from {file.filename}"
        source_desc = description or f"Imported from {file.filename}"

        pattern = analyzer.analyze(texts, name=profile_name, source_description=source_desc)

        # Save
        db = Database()
        db.save_pattern(pattern)
        db.close()

        return {
            "success": True,
            "pattern_id": pattern.id,
            "name": pattern.name,
            "stats": {
                "total_words": pattern.total_words,
                "total_sentences": pattern.total_sentences,
                "avg_sentence_length": pattern.avg_sentence_length,
                "vocab_richness": pattern.vocab_richness,
            }
        }

    finally:
        # Cleanup temp file
        if temp_file.exists():
            temp_file.unlink()
        if temp_dir.exists():
            temp_dir.rmdir()


@app.get("/api/patterns")
async def list_patterns():
    """List all voice patterns."""
    db = Database()
    patterns = db.list_patterns()
    db.close()

    return {
        "patterns": [
            {
                "id": p.id,
                "name": p.name,
                "total_words": p.total_words,
                "total_sentences": p.total_sentences,
                "source_description": p.source_description,
                "created_at": p.created_at.isoformat(),
            }
            for p in patterns
        ]
    }


@app.get("/api/patterns/{pattern_id}")
async def get_pattern(pattern_id: str):
    """Get detailed information about a pattern."""
    db = Database()
    pattern = db.get_pattern(pattern_id)
    db.close()

    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")

    return pattern.to_dict()


@app.post("/api/generate")
async def generate_prompt(
    pattern_id: str = Form(...),
    context: str = Form("professional"),
    name: Optional[str] = Form(None)
):
    """Generate a prompt from a pattern."""
    db = Database()
    pattern = db.get_pattern(pattern_id)

    if not pattern:
        db.close()
        raise HTTPException(status_code=404, detail="Pattern not found")

    # Generate
    generator = GeneratorService()
    prompt = generator.generate(pattern, context=context, name=name)

    # Save
    db.save_prompt(prompt)
    db.close()

    return {
        "success": True,
        "prompt_id": prompt.id,
        "name": prompt.name,
        "context": prompt.context,
        "prompt_text": prompt.prompt_text,
    }


@app.get("/api/prompts")
async def list_prompts(pattern_id: Optional[str] = None):
    """List all prompts."""
    db = Database()
    prompts = db.list_prompts(pattern_id)
    db.close()

    return {
        "prompts": [
            {
                "id": p.id,
                "pattern_id": p.pattern_id,
                "name": p.name,
                "context": p.context,
                "created_at": p.created_at.isoformat(),
            }
            for p in prompts
        ]
    }


@app.get("/api/prompts/{prompt_id}")
async def get_prompt(prompt_id: str):
    """Get a specific prompt."""
    db = Database()
    prompt = db.get_prompt(prompt_id)
    db.close()

    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    return prompt.to_dict()


@app.get("/api/prompts/{prompt_id}/download", response_class=PlainTextResponse)
async def download_prompt(prompt_id: str):
    """Download a prompt as a text file."""
    db = Database()
    prompt = db.get_prompt(prompt_id)
    db.close()

    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    return PlainTextResponse(
        content=prompt.prompt_text,
        headers={"Content-Disposition": f'attachment; filename="{prompt.id}.txt"'}
    )


@app.get("/api/privacy")
async def privacy_info():
    """Get privacy information."""
    db = Database()
    patterns = db.list_patterns()
    db.close()

    total_words = sum(p.total_words for p in patterns)

    db_path = Path("data/atlas_voice.db")
    db_size = db_path.stat().st_size if db_path.exists() else 0

    return {
        "guarantee": "NO original text content is stored. Only linguistic patterns.",
        "stats": {
            "patterns_count": len(patterns),
            "total_words_analyzed": total_words,
            "original_content_stored": 0,
            "database_size_kb": round(db_size / 1024, 1),
        },
        "what_we_store": [
            "Word frequencies (e.g., 'the' appears 3.2% of the time)",
            "Sentence length averages",
            "Common phrases and patterns",
            "Style markers (casual/formal indicators)"
        ],
        "what_we_dont_store": [
            "Original text content",
            "Personal information",
            "Email addresses",
            "Actual messages or documents"
        ]
    }


@app.delete("/api/patterns/{pattern_id}")
async def delete_pattern(pattern_id: str):
    """Delete a pattern and all its prompts."""
    db = Database()
    pattern = db.get_pattern(pattern_id)

    if not pattern:
        db.close()
        raise HTTPException(status_code=404, detail="Pattern not found")

    db.delete_pattern(pattern_id)
    db.close()

    return {"success": True, "message": "Pattern deleted"}
