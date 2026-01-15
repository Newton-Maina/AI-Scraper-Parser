import streamlit as st
from src.scraper import scrape_website
from src.parser import parse_with_ollama
from src.processing import extract_body_content, clean_body_content, split_dom_content

# Streamlit App
st.set_page_config(page_title="AI Multi-Web Scraper", page_icon="🌐")
st.title("🌐 AI Multi-Web Scraper")

# Sidebar for global controls
with st.sidebar:
    st.header("Controls")
    if st.button("🧹 Clear Session", help="Reset all data and start over"):
        st.session_state.clear()
        st.rerun()

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
