from openai import AsyncOpenAI

REWRITE_SYSTEM_PROMPT = """You are a query rewriter for a Shopify support assistant.
Given a conversation history and the user's latest question, rewrite the question
into a standalone, self-contained query that captures the full intent.
If the latest question is already self-contained, return it unchanged.
Return ONLY the rewritten question, no extra text, no formatting."""


async def rewrite_query(
    question: str,
    history: list[dict[str, str]],
    client: AsyncOpenAI,
    model: str,
    max_history: int = 4,
) -> str:
    """Rewrite ambiguous questions into independent, contextualized questions."""

    if not history:
        return question

    recent = history[-max_history:]
    conversation = "\n".join(f"{msg['role'].capitalize()}: {msg['content']}" for msg in recent)
    user_prompt = (
        f"Conversation:\n{conversation}\n\nLatest question: {question}\n\nRewritten question:"
    )
    completion = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": REWRITE_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,  # deterministic
    )

    rewritten = (completion.choices[0].message.content or "").strip()
    return rewritten if rewritten else question
