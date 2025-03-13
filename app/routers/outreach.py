import os
import asyncio
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from loguru import logger

from app.services.process_files import process_outreach

router = APIRouter(prefix="/outreach", tags=["Outreach"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/process")
async def process_outreach_file(file: UploadFile = File(...)):
    """
    Uploads a file and processes outreach (email or call) asynchronously in the background.
    Returns a download link for the processed results.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Invalid file. Filename cannot be None.")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    # Save uploaded file
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    logger.info(f"File {file.filename} uploaded successfully.")

    # Determine output file name
    output_filename = f"processed_{file.filename}"
    output_path = os.path.join(UPLOAD_DIR, output_filename)

    # 🔥 Run process_outreach properly and catch errors
    async def run_processing():
        try:
            logger.info(f"Starting background task for {file_path}")
            await process_outreach(file_path, output_path)
            logger.info(f"Processing completed for {file_path}")
        except Exception as e:
            logger.error(f"Error in process_outreach: {e}")

    asyncio.create_task(run_processing())

    return {
        "message": "Processing started in the background. Check back for results.",
        "download_url": f"/outreach/download/{output_filename}"
    }


@router.get("/download/{filename}")
async def download_processed_file(filename: str):
    """
    Allows users to download the processed outreach results file.
    """
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, filename=filename, media_type="text/csv")
