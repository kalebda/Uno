from datetime import datetime
from typing import List, Optional

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_message import ChatMessage


class ChatMessageCRUD:
    """CRUD operations for ChatMessage model"""
    
    async def create(
        self, 
        db: AsyncSession, 
        user_id: str, 
        session_id: str, 
        role: str, 
        content: str
    ) -> ChatMessage:
        """Create new chat message"""
        db_obj = ChatMessage(
            user_id=user_id,
            session_id=session_id,
            role=role,
            content=content
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_session_messages(
        self, 
        db: AsyncSession, 
        user_id: str, 
        session_id: str, 
        limit: int = 10
    ) -> List[ChatMessage]:
        """Get recent messages for a session"""
        result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id, ChatMessage.session_id == session_id)
            .order_by(desc(ChatMessage.timestamp))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_user_messages(
        self, 
        db: AsyncSession, 
        user_id: str, 
        limit: int = 20
    ) -> List[ChatMessage]:
        """Get recent messages for a user across all sessions"""
        result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id)
            .order_by(desc(ChatMessage.timestamp))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def delete_session_messages(
        self, 
        db: AsyncSession, 
        user_id: str, 
        session_id: str
    ) -> int:
        """Delete all messages for a session"""
        result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id, ChatMessage.session_id == session_id)
        )
        messages = result.scalars().all()
        
        for message in messages:
            await db.delete(message)
        
        await db.commit()
        return len(messages)


chat_message_crud = ChatMessageCRUD()
