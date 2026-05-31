# =============================================================================
# Save uploaded documents for job applications.
# Files are stored under `uploads/` and described in jobs_applied.attachment_metadata as JSON.
# =============================================================================

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from fastapi import HTTPException, UploadFile, status

from app.config import MAX_UPLOAD_SIZE_MB, UPLOAD_DIR

# Allowed document types for a simple learning project
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt", ".png", ".jpg", ".jpeg"}
MAX_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024


def ensure_upload_dir() -> Path:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    return UPLOAD_DIR


def _safe_filename(original: str) -> str:
    # Strip path components and unsafe characters from uploaded file names
    name = Path(original).name
    name = re.sub(r"[^\w.\-]", "_", name)
    return name[:120] or "file"


def parse_attachment_metadata(raw: Optional[str]) -> List[dict]:
    # Turn stored JSON (or legacy plain text) into a list for templates
    if not raw or not raw.strip():
        return []
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass
    return [{"original_name": raw, "stored_name": None, "note": "legacy text entry"}]


async def save_job_attachments(job_id: int, files: List[UploadFile]) -> Optional[str]:

    # Save one or more uploads for a job; Returns JSON string for attachment_metadata

    if not files:
        return None

    ensure_upload_dir()
    entries: List[dict] = []
    uploaded_at = datetime.now(timezone.utc).isoformat()

    for upload in files:
        if not upload.filename:
            continue

        ext = Path(upload.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type '{ext}' not allowed. Use: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
            )

        content = await upload.read()
        if len(content) > MAX_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File '{upload.filename}' exceeds {MAX_UPLOAD_SIZE_MB} MB limit.",
            )

        safe = _safe_filename(upload.filename)
        stored_name = f"job_{job_id}_{safe}"
        dest = UPLOAD_DIR / stored_name
        dest.write_bytes(content)

        entries.append(
            {
                "original_name": upload.filename,
                "stored_name": stored_name,
                "url": f"/uploads/{stored_name}",
                "uploaded_at": uploaded_at,
            }
        )

    if not entries:
        return None

    return json.dumps(entries)
