from uuid import UUID

from customer_service_agent.core.exceptions import NotFoundError
from customer_service_agent.db.models import Message
from customer_service_agent.repositories.conversation_repository import (
    ConversationRepository,
)
from customer_service_agent.repositories.message_repository import MessageRepository


class MessageService:
    def __init__(
        self,
        message_repository: MessageRepository,
        conversation_repository: ConversationRepository,
    ) -> None:
        self.message_repository = message_repository
        self.conversation_repository = conversation_repository

    async def create_message(
        self,
        conversation_id: UUID,
        role: str,
        content: str,
    ) -> Message:
        await self._ensure_conversation_exists(conversation_id)

        message = await self.message_repository.create(conversation_id, role, content)
        await self.message_repository.session.commit()
        return message

    async def list_messages(self, conversation_id: UUID) -> list[Message]:
        await self._ensure_conversation_exists(conversation_id)
        return await self.message_repository.list_by_conversation(conversation_id)

    async def _ensure_conversation_exists(self, conversation_id: UUID) -> None:
        conversation = await self.conversation_repository.get_by_id(conversation_id)

        if conversation is None:
            raise NotFoundError("Conversation not found")
