from sqlalchemy.orm import Session
from models.exam import Upload
from schemas.upload import UploadCreate, UploadUpdate
import time

def get_all(db: Session):
    return db.query(Upload).order_by(Upload.uploaded_at.desc()).all()

def get_by_id(db: Session, upload_id: int):
    return db.query(Upload).filter(Upload.id == upload_id).first()

def create(db: Session, upload: UploadCreate):
    new_upload = Upload(
        subject=upload.subject,
        filename=upload.filename,
        csv_text=upload.csv_text,
        uploaded_at=int(time.time())
    )
    db.add(new_upload)
    db.commit()
    db.refresh(new_upload)
    return new_upload

def update(db: Session, upload_id: int, upload: UploadUpdate):
    db_upload = db.query(Upload).filter(Upload.id == upload_id).first()
    if not db_upload:
        return None
    for key, value in upload.dict(exclude_unset=True).items():
        setattr(db_upload, key, value)
    db.commit()
    db.refresh(db_upload)
    return db_upload

def delete(db: Session, upload_id: int):
    db_upload = db.query(Upload).filter(Upload.id == upload_id).first()
    if not db_upload:
        return None
    db.delete(db_upload)
    db.commit()
    return True
