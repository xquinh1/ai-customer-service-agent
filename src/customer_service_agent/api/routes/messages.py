from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from customer_service_agent.db.connection import get_db_session
from customer_service_agent.repositories.conversation_repository import (
    ConversationRepository,
)
from customer_service_agent.repositories.message_repository import MessageRepository
from customer_service_agent.schemas.message import MessageRequest, MessageResponse
from customer_service_agent.services.message_service import MessageService

router = APIRouter(prefix="/api/conversations", tags=["messages"])


def get_message_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> MessageService:
    return MessageService(
        message_repository=MessageRepository(session),
        conversation_repository=ConversationRepository(session),
    )


@router.post(
    "/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_message(
    conversation_id: UUID,
    payload: MessageRequest,
    service: Annotated[MessageService, Depends(get_message_service)],
) -> MessageResponse:
    message = await service.create_message(
        conversation_id,
        payload.role,
        payload.content,
    )
    return MessageResponse.model_validate(message)


@router.get(
    "/{conversation_id}/messages",
    response_model=list[MessageResponse],
)
async def list_messages(
    conversation_id: UUID,
    service: Annotated[MessageService, Depends(get_message_service)],
) -> list[MessageResponse]:
    messages = await service.list_messages(conversation_id)
    return [MessageResponse.model_validate(message) for message in messages]
