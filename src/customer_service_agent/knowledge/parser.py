from dataclasses import dataclass

from bs4 import BeautifulSoup, Tag


@dataclass
class ParsedBlock:
    """get heading, paragraph, list item theo block"""

    kind: str
    level: int
    text: str


@dataclass
class ParsedDocument:
    """Result of parse: title and blocks"""

    title: str
    blocks: list[ParsedBlock]


def _find_main_content(soup: BeautifulSoup) -> Tag:
    """Return main content: article, main, body"""
    main = soup.find("article") or soup.find("main") or soup.body
    assert main is not None
    return main


def parse_html(html: str) -> ParsedDocument:
    """Parse html to title and blockes"""

    soup = BeautifulSoup(html, "html.parser")
    main = _find_main_content(soup)

    title_tag = soup.title
    title = title_tag.get_text(strip=True) if title_tag else ""

    blocks: list[ParsedBlock] = []
    for element in main.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"]):
        text = element.get_text(strip=True)
        if not text:
            continue
        if element.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            blocks.append(ParsedBlock(kind="heading", level=int(element.name[1]), text=text))
        elif element.name == "p":
            blocks.append(ParsedBlock(kind="paragraph", level=0, text=text))
        else:
            blocks.append(ParsedBlock(kind="list_item", level=0, text=text))

    return ParsedDocument(title=title, blocks=blocks)
