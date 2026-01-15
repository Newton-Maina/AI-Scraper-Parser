from bs4 import BeautifulSoup

def extract_body_content(html_content):
    """
    Extract <body> content from raw HTML.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        body = soup.body
        if body:
            return str(body)
        return ''
    except Exception as e:
        print(f"Error extracting body content: {e}")
        return ''

def clean_body_content(body_content):
    """
    Extract only product text (titles, prices, stock, etc.) with no HTML tags.
    This function is tailored for the specific product site structure.
    """
    try:
        soup = BeautifulSoup(body_content, 'html.parser')

        # Remove irrelevant elements
        for elem in soup(['script', 'style', 'header', 'footer', 'nav']):
            elem.extract()

        # Target product grid and best sellers section
        product_sections = soup.select(
            '.sm\:grid-cols-2.lg\:grid-cols-3.xl\:grid-cols-4, [data-nc-id="BestSellersSection"]'
        )

        if not product_sections:
            print("No product sections found in body content")
            return ''

        # Extract text only from ProductCards
        products = []
        for section in product_sections:
            cards = section.select('[data-nc-id="ProductCard"]')
            for card in cards:
                text = card.get_text(separator=" ", strip=True)
                if text:
                    products.append(text)

        return "\n\n--- PRODUCT ---\n\n".join(products) if products else ''

    except Exception as e:
        print(f"Error cleaning body content: {e}")
        return ''

def split_dom_content(dom_content, max_length=5000):
    """
    Split DOM content into chunks, preserving page boundaries.
    """
    if isinstance(dom_content, list):
        return dom_content  # Already split by page
    elif isinstance(dom_content, str):
        return [dom_content[i:i + max_length] for i in range(0, len(dom_content), max_length)]
    else:
        raise TypeError("dom_content must be a string or list of strings")
