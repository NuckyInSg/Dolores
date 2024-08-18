import os
import shutil
from fastapi import UploadFile, HTTPException
from app.core.config import settings
from app.tools.document_parser import parse_resume

class ResumeService:
    @staticmethod
    async def upload_resume(file: UploadFile) -> dict:
        if not os.path.exists(settings.UPLOAD_DIR):
            os.makedirs(settings.UPLOAD_DIR)
        
        file_location = f"{settings.UPLOAD_DIR}/resume_{file.filename}"
        try:
            with open(file_location, "wb+") as file_object:
                shutil.copyfileobj(file.file, file_object)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Could not upload the file: {str(e)}")
        finally:
            file.file.close()
        
        parsed_content = parse_resume(file_location)
        
        return {
            "file_path": file_location,
            "parsed_content": parsed_content
        }