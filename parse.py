from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from colorama import Fore, Style, init

init(autoreset=True)

template = (
    "You are tasked with extracting specific information from the following text content: {dom_content}. "
    "Please follow these instructions carefully: \n\n"
    "1. **Extract Information:** Only extract the information that directly matches the provided description: {parse_description}. "
    "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response. "
    "3. **Empty Response:** If no information matches the description, return an empty string ('')."
    "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
)

model = OllamaLLM(model="gemma2:2b")

def parse_with_ollama(dom_chunks, parse_description):
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model
    print(f"{Fore.GREEN}Parsing Initialized...")

    parsed_results = []

    for i, chunk in enumerate(dom_chunks, start=1):
        response = chain.invoke(
            {"dom_content": chunk, "parse_description": parse_description}
        )
        print(f"{Fore.YELLOW}Parsed batch: {i} of {len(dom_chunks)}")
        parsed_results.append(response)

    print(f"{Fore.GREEN}Parsing complete!")
    return "\n".join(parsed_results)


