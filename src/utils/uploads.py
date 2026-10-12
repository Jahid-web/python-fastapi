import uuid
from io import BytesIO
from fastapi import UploadFile, File, status, HTTPException
from fastapi.responses import FileResponse, Response
from pathlib import Path
from pypdf import PdfReader
from PIL import Image, UnidentifiedImageError

from src.core.exceptions import BadRequestException

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_SIZE = 2 * 1024 * 1024

ALLOWED_FORMATS = {
    "JPEG": ".jpg",
    "PNG": ".png"
}

async def uploads(file: UploadFile):
    file_bytes = bytearray()

    try:
        while chunk:= await file.read(64 * 1024):
            file_bytes.extend(chunk)

            if len(file_bytes) > MAX_SIZE:
                raise HTTPException (
                    status_code= status.HTTP_413_CONTENT_TOO_LARGE,
                    detail="File size must be 2 MB or smaller."
                )

        if not file_bytes:
            raise BadRequestException(
                message="Uploaded file is empty.",
            )

        file_data = bytes(file_bytes)

        if file_data.startswith(b"%PDF-"):
            file_format = validate_pdf(file_data)
            extension = ".pdf"
        else:
            file_format = validate_image(file_data)
            extension = ALLOWED_FORMATS[file_format]

        filename = f"{uuid.uuid4().hex}{extension}"
        file_path = UPLOAD_DIR/filename

        file_path.write_bytes(file_data)

        return {
            "message": "Image uploaded successfully.",
            "filename": filename,
            "path": str(file_path),
            "size": len(file_bytes),
            "format": file_format
        }
    
    finally:
        await file.close()



def validate_image(file_data: bytes) -> str:
    try:
        with Image.open(BytesIO(file_data)) as img:
            img_format = img.format

            if img_format not in ALLOWED_FORMATS:
                raise BadRequestException(
                        message="Only JPEG and PNG images are allowed."
                    )

            img.verify()

        with Image.open(BytesIO(file_data)) as img:
            img.load()

        
        return img_format
    
    except HTTPException:
        raise

    except BadRequestException:
        raise

    except (UnidentifiedImageError, Image.DecompressionBombError, OSError, ValueError) as exc:
                raise BadRequestException(
                    message="Invalid or corrupted image file."
                ) from exc

def validate_pdf(file_data: bytes) -> str:
    if not file_data.startswith(b"%PDF-"):
        raise BadRequestException(
            message="Invalid PDF file."
        )

    try:
        reader = PdfReader(BytesIO(file_data), strict=True)

        if len(reader.pages) < 1:
            raise BadRequestException(
                message="PDF must contain at least one page."
            )

        return "PDF"

    except BadRequestException:
        raise

    except Exception as exc:
        raise BadRequestException(
            message="Invalid or corrupted PDF file."
        ) from exc
        
