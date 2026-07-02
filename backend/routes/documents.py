from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database.models import Document
from database.config import get_db
from backend.services.auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix='/documents')

class DocumentResponse(BaseModel):
    id: UUID
    user_id: UUID
    filename: str
    status: str
    chunk_count: int
    created_at: str

    class Config:
        orm_mode = True

@router.post("/upload", operation_id="upload_document", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Save document metadata to the database
        new_document = Document(
            user_id=current_user["id"],
            filename=file.filename,
            status="processing",
            chunk_count=0,
            created_at=datetime.utcnow()
        )
        db.add(new_document)
        db.commit()
        db.refresh(new_document)

        # Process the file (e.g., extract text, chunk, embed, etc.)
        # This logic should be implemented in the document service layer
        # For now, we assume the processing is handled asynchronously
        # document_service.process_document(file, new_document.id)

        return {"message": "Document uploaded successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", operation_id="list_documents", response_model=List[DocumentResponse])
async def list_documents(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        documents = db.query(Document).filter(Document.user_id == current_user["id"]).all()
        return documents
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{id}", operation_id="delete_document", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        document = db.query(Document).filter(Document.id == id, Document.user_id == current_user["id"]).first()
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

        db.delete(document)
        db.commit()
        return {"message": "Document deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))