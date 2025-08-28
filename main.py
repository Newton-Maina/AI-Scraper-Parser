import streamlit as st
from bs4 import BeautifulSoup
import os
from scrape import scrape_website
from parse import parse_with_ollama

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
    """
    try:
        soup = BeautifulSoup(body_content, 'html.parser')

        # Remove irrelevant elements
        for elem in soup(['script', 'style', 'header', 'footer', 'nav']):
            elem.extract()

        # Target product grid and best sellers section
        product_sections = soup.select(
            '.sm\\:grid-cols-2.lg\\:grid-cols-3.xl\\:grid-cols-4, [data-nc-id="BestSellersSection"]'
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

# Streamlit App
st.title("🌐 AI Multi-Web Scraper")
st.markdown("Welcome to the AI Web Scraper!")
st.markdown("Enter a website URL to scrape its content and extract specific information.")

url = st.text_input("🔗 Enter the Website URL", "")
if st.button("Scrape Site"):
    if url:
        st.write("🕵️‍♂️ Scraping Your Site...")
        try:
            result = scrape_website(url)  # List of HTML pages

            all_cleaned = []
            for page_num, html in enumerate(result, 1):
                body_content = extract_body_content(html)
                if not body_content:
                    st.warning(f"No body content found for page {page_num}")
                    continue
                cleaned_content = clean_body_content(body_content)
                if cleaned_content:
                    all_cleaned.append(f"<!-- Page {page_num} -->\n{cleaned_content}")
                else:
                    st.warning(f"No product data found for page {page_num}")

            # Store as list to preserve page boundaries
            st.session_state.dom_content = all_cleaned

            with st.expander("📄 View DOM Content"):
                st.text_area("DOM Content", "\n\n--- PAGE SPLIT ---\n\n".join(all_cleaned), height=300)

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a valid URL before scraping.")

if "dom_content" in st.session_state:
    st.subheader("🔍 Wish to parse?")
    parse_description = st.text_area("Describe what you want to parse:", "")

    if st.button("Parse Content"):
        if parse_description:
            st.write("🔍 Parsing Description...")
            with st.spinner("Processing..."):
                try:
                    # Pass list of page contents directly to parser
                    parsed_results = parse_with_ollama(st.session_state.dom_content, parse_description)

                    st.subheader("📊 Parsed Results")
                    st.write("Results", parsed_results)
                except Exception as e:
                    st.error(f"An error occurred during parsing: {e}")
        else:
            st.warning("Please enter a description of what you want to parse.")