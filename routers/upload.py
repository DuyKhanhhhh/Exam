from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.db import get_db
from schemas.upload import UploadCreate, UploadUpdate, UploadOut
from crud import upload as crud_upload
from typing import List


router = APIRouter(prefix="/uploads", tags=["Uploads"])

@router.get("/", response_model=List[UploadOut])
def get_uploads(db: Session = Depends(get_db)):
    """Lấy danh sách các bài thi đã upload"""
    return crud_upload.get_all(db)

@router.get("/{upload_id}", response_model=UploadOut)
def get_upload(upload_id: int, db: Session = Depends(get_db)):
    """Lấy chi tiết một bài thi"""
    upload = crud_upload.get_by_id(db, upload_id)
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    return upload

@router.post("/", response_model=UploadOut)
def create_upload(upload: UploadCreate, db: Session = Depends(get_db)):
    """Tạo mới bản ghi upload (thêm bài thi mới)"""
    return crud_upload.create(db, upload)

@router.put("/{upload_id}", response_model=UploadOut)
def update_upload(upload_id: int, upload: UploadUpdate, db: Session = Depends(get_db)):
    """Cập nhật bài thi"""
    updated = crud_upload.update(db, upload_id, upload)
    if not updated:
        raise HTTPException(status_code=404, detail="Upload not found")
    return updated

@router.delete("/{upload_id}")
def delete_upload(upload_id: int, db: Session = Depends(get_db)):
    """Xóa bài thi"""
    deleted = crud_upload.delete(db, upload_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Upload not found")
    return {"message": "Upload deleted successfully"}
