# AI Web Scraper & Parser
MAIN.PY enhanced.
A powerful, modular web scraping and parsing tool built with Python, Streamlit, Selenium, and LangChain. This application allows you to scrape websites (handling dynamic content and pagination via Bright Data) and parse the extracted data using local LLMs (via Ollama).

## Features

-   **Intelligent Scraping**: Uses Selenium with Bright Data's scraping browser to handle CAPTCHAs, dynamic content, and pagination automatically.
-   **Clean Extraction**: Automatically extracts and cleans product data from HTML, removing clutter like scripts and styles.
-   **AI Parsing**: leverages Ollama (e.g., Gemma 2) to parse unstructured HTML into structured data based on natural language descriptions.
-   **Interactive UI**: Built with Streamlit for a user-friendly experience.

## Project Structure

```
├── main.py              # Streamlit application entry point
├── requirements.txt     # Python dependencies
├── .env.example         # Example configuration file
├── src/                 # Source code
│   ├── scraper.py       # Selenium & Bright Data scraping logic
│   ├── parser.py        # LangChain & Ollama parsing logic
│   └── processing.py    # HTML extraction and cleaning utilities
└── ...
```

## Prerequisites

-   **Python 3.8+**
-   **Ollama**: Installed and running locally.
    -   Pull the model used (default `gemma2:2b`): `ollama pull gemma2:2b`
-   **Bright Data Account**: You need a Scraping Browser instance.

## Installation

1.  **Clone the repository** (if applicable) or navigate to the project folder.

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration**:
    -   Create a `.env` file in the root directory.
    -   Add your Bright Data WebDriver URL (see `.env.example`):
        ```env
        SBR_WEBDRIVER=https://your-username:your-password@brd.superproxy.io:9515
        ```
    -   *Note: If you don't set this, the code currently defaults to a hardcoded placeholder which may not work.*

## Usage

1.  **Start the Streamlit App**:
    ```bash
    streamlit run main.py
    ```

2.  **Scrape**:
    -   Enter a URL in the text box.
    -   Click **Scrape Site**.
    -   Review the cleaned "DOM Content".

3.  **Parse**:
    -   Enter a description of what you want to extract (e.g., "Extract all product titles and prices").
    -   Click **Parse Content**.
    -   View the AI-extracted results.

## Customization

-   **Parsing Model**: Change the model in `src/parser.py` (variable `model = OllamaLLM(model="...")`).
-   **Cleaning Logic**: Modify `src/processing.py` to adjust how HTML is cleaned or to support different website structures.

## License

[MIT](LICENSE)
