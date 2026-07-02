from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from pydantic import BaseModel, Field

from database.models import Conversation
from database.config import get_db
from backend.services.auth import get_current_user

router = APIRouter(prefix="/conversations")

# Pydantic schemas
class ConversationResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    created_at: str

    class Config:
        orm_mode = True

# Route handlers
@router.post("/", operation_id="create_conversation", status_code=status.HTTP_201_CREATED)
async def create_conversation(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Create a new conversation for the authenticated user.
    """
    user_id = current_user["id"]
    new_conversation = Conversation(user_id=user_id, title="New Conversation")
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    return {"message": "Conversation created successfully"}

@router.get("/", operation_id="list_conversations", response_model=List[ConversationResponse])
async def list_conversations(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List all conversations for the authenticated user.
    """
    user_id = current_user["id"]
    conversations = db.query(Conversation).filter(Conversation.user_id == user_id).all()
    return conversations