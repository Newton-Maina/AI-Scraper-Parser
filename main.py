# app.py
import streamlit as st
from scrape import scrape_website, split_dom_content, clean_body_content, extract_body_content
from parse import parse_with_ollama

st.title("🌐 AI Web Scraper")
st.markdown("Welcome to the AI Web Scraper!")
st.markdown("Enter a website URL to scrape its content and extract specific information.")

url = st.text_input("🔗 Enter the Website URL", "")
if st.button("Scrape Site"):
    if url:
        st.write("🕵️‍♂️ Scraping Your Site...")
        try:
            result = scrape_website(url)
            body_content = extract_body_content(result)
            cleaned_content = clean_body_content(body_content)
            st.session_state.dom_content = cleaned_content

            with st.expander("📄 View DOM Content"):
                st.text_area("DOM Content", cleaned_content, height=300)
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
                    dom_chunks = split_dom_content(st.session_state.dom_content)
                    parsed_results = parse_with_ollama(dom_chunks, parse_description)

                    st.subheader("📊 Parsed Results")
                    st.write("Results", parsed_results)
                except Exception as e:
                    st.error(f"An error occurred during parsing: {e}")
        else:
            st.warning("Please enter a description of what you want to parse.")
