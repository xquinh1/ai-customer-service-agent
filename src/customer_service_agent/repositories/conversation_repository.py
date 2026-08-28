from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from customer_service_agent.db.models import Conversation


class ConversationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, title: str) -> Conversation:
        conversation = Conversation(title=title)

        self.session.add(conversation)
        await self.session.flush()
        await self.session.refresh(conversation)

        return conversation

    async def list_all(self) -> list[Conversation]:
        result = await self.session.execute(
            select(Conversation).order_by(Conversation.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, conversation_id: UUID) -> Conversation | None:
        result = await self.session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def delete(self, conversation: Conversation) -> None:
        await self.session.delete(conversation)
