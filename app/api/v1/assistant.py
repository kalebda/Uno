from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.db import get_db
from app.schemas.assistant import (ChatRequest, ChatResponse,
                                   ScholarshipAnalysisRequest,
                                   ScholarshipAnalysisResponse)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """Chat with the AI assistant about study opportunities for a specific country"""
    from app.crud.chat_message import chat_message_crud
    from app.crud.user import user_crud
    from app.services.rag_service import RAGService

    try:
        # Get or create default user
        user = await user_crud.get_or_create_default_user(db)

        # Save user message
        await chat_message_crud.create(
            db=db,
            user_id=user.id,
            session_id=request.session_id,
            role="user",
            content=request.message
        )

        # Get chat history for context
        chat_history = await chat_message_crud.get_session_messages(
            db=db,
            user_id=user.id,
            session_id=request.session_id,
            limit=5
        )

        rag_service = RAGService()
        
        # Generate response using RAG with country context and chat history
        result = rag_service.generate_response(
            request.message,
            request.user_background,
            chat_history
        )

        # Save assistant response
        await chat_message_crud.create(
            db=db,
            user_id=user.id,
            session_id=request.session_id,
            role="assistant",
            content=result.get("response", "Sorry, I couldn't process your request.")
        )

        return ChatResponse(
            response=result.get("response", "Sorry, I couldn't process your request."),
            query=result.get("query", request.message),
            country=request.country,
            user_background=result.get("user_background", request.user_background),
            session_id=request.session_id,
            sources=result.get("sources", []),
            confidence=result.get("confidence", 0.0)
        )
    except Exception as e:
        return ChatResponse(
            response=f"Error: {str(e)}",
            query=request.message,
            country=request.country,
            user_background=request.user_background,
            session_id=request.session_id,
            error=True
        )


@router.post("/analyze-scholarship", response_model=ScholarshipAnalysisResponse)
async def analyze_scholarship_fit(
    request: ScholarshipAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """Analyze if a user fits specific scholarship programs"""
    from app.services.rag_service import RAGService

    try:
        rag_service = RAGService()

        # Analyze scholarship fit
        result = rag_service.analyze_scholarship_fit(request.user_background, request.scholarship_query)

        return ScholarshipAnalysisResponse(
            analysis=result.get("analysis", "Sorry, I couldn't analyze your eligibility."),
            user_background=result.get("user_background", request.user_background),
            scholarship_query=result.get("scholarship_query", request.scholarship_query),
            sources=result.get("sources", []),
            confidence=result.get("confidence", 0.0)
        )
    except Exception as e:
        return ScholarshipAnalysisResponse(
            analysis=f"Error: {str(e)}",
            user_background=request.user_background,
            scholarship_query=request.scholarship_query,
            error=True
        )
