from customer_service_agent.knowledge.parser import parse_html


def test_parse_extracts_title_and_blocks_in_order() -> None:
    html = """
    <html><head><title>Creating discount codes - Shopify Help Center</title></head>
        <body>
          <nav>Home > Discounts</nav>
          <article>
            <h1>Creating discount codes</h1>
            <p>To create a discount code, go to Discounts in your Shopify admin.</p>
            <h2>Steps</h2>
            <ul><li>Open the Discounts page.</li><li>Click Create discount.</li></ul>
          </article>
          <footer>(c) 2026 Shopify</footer>
        </body></html>
    """

    doc = parse_html(html)

    assert doc.title == "Creating discount codes - Shopify Help Center"
    assert [block.kind for block in doc.blocks] == [
        "heading",
        "paragraph",
        "heading",
        "list_item",
        "list_item",
    ]
    assert doc.blocks[0].level == 1
    assert doc.blocks[2].level == 2


def test_skips_empty_elements_and_scripts() -> None:
    html = """
    <article>
        <h2>Steps</h2>
        <p></p>
        <p>First step.</p>
        <script>alert('x')</script>
        <li>Item</li>
    </article>
    """

    doc = parse_html(html)

    assert [block.text for block in doc.blocks] == [
        "Steps",
        "First step.",
        "Item",
    ]
