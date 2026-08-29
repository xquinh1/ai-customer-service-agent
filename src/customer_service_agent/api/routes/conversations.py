from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from customer_service_agent.db.connection import get_db_session
from customer_service_agent.repositories.conversation_repository import (
    ConversationRepository,
)
from customer_service_agent.schemas.conversation import (
    ConversationRequest,
    ConversationResponse,
)
from customer_service_agent.services.conversation_service import (
    ConversationService,
)

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


def get_conversation_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ConversationService:
    repository = ConversationRepository(session)
    return ConversationService(repository)


@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_conversation(
    payload: ConversationRequest,
    service: Annotated[
        ConversationService,
        Depends(get_conversation_service),
    ],
) -> ConversationResponse:
    conversation = await service.create_conversation(payload.title)
    return ConversationResponse.model_validate(conversation)


@router.get("", response_model=list[ConversationResponse])
async def list_conversations(
    service: Annotated[
        ConversationService,
        Depends(get_conversation_service),
    ],
) -> list[ConversationResponse]:
    conversations = await service.list_conversations()
    return [ConversationResponse.model_validate(conversation) for conversation in conversations]


@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
)
async def get_conversation(
    conversation_id: UUID,
    service: Annotated[ConversationService, Depends(get_conversation_service)],
) -> ConversationResponse:
    conversation = await service.get_conversation(conversation_id)
    return ConversationResponse.model_validate(conversation)


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_conversation(
    conversation_id: UUID,
    service: Annotated[
        ConversationService,
        Depends(get_conversation_service),
    ],
) -> None:
    await service.delete_conversation(conversation_id)
