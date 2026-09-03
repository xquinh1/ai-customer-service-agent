import re

from customer_service_agent.knowledge.parser import ParsedBlock


def clean_text(text: str) -> str:
    """
    Clean the text by removing extra whitespace and newlines.
    """
    return re.sub(r"\s+", " ", text).strip()


BOILERPLATE_PHRASES = (
    "Was this page helpful?",
    "Last updated: ",
    "Shopify Support",
    "Sign up for Shopify",
)


def is_boilerplate(text: str) -> bool:
    """
    Check if the text is a boilerplate phrase.
    """
    lowered = text.lower()
    return any(phrase.lower() in lowered for phrase in BOILERPLATE_PHRASES)


def clean_blocks(blocks: list[ParsedBlock]) -> list[ParsedBlock]:
    """
    Clean the blocks by removing boilerplate phrases.
    """
    cleaned: list[ParsedBlock] = []
    for block in blocks:
        text = clean_text(block.text)
        if not text or is_boilerplate(text):
            continue
        cleaned.append(ParsedBlock(kind=block.kind, level=block.level, text=text))
    return cleaned
