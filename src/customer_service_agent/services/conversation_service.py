from uuid import UUID

from customer_service_agent.db.models import Conversation
from customer_service_agent.repositories.conversation_repository import (
    ConversationRepository,
)


class ConversationService:
    def __init__(self, repository: ConversationRepository) -> None:
        self.repository = repository

    async def create_conversation(self, title: str) -> Conversation:
        conversation = await self.repository.create(title)
        await self.repository.session.commit()
        return conversation

    async def list_conversations(self) -> list[Conversation]:
        return await self.repository.list_all()

    async def get_conversation(self, conversation_id: UUID) -> Conversation:
        conversation = await self.repository.get_by_id(conversation_id)

        if conversation is None:
            raise ValueError("Conversation not found")

        return conversation

    async def delete_conversation(self, conversation_id: UUID) -> None:
        conversation = await self.repository.get_by_id(conversation_id)

        if conversation is None:
            raise ValueError("Conversation not found")

        await self.repository.delete(conversation)
