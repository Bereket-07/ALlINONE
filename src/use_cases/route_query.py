import re
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.config import OPENAI_API_KEY
from src.config import GOOGLE_API_KEY
from src.infrastructure.llm.llm_list import LLM_REGISTRY, AVAILABLE_LLM_NAMES

# Define the Router LLM using LangChain
router_llm = ChatOpenAI(
            model="gpt-4o", 
            api_key=OPENAI_API_KEY, 
            temperature=0.7, 
            max_tokens=1500
        )

# Define the prompt template for the router
ROUTING_PROMPT_TEMPLATE = """
You are an intelligent routing system. Your task is to select the best language model
to answer a given user query. You must choose from the following available models: [{available_models}].

Consider the query's nature (e.g., creative writing, coding, factual recall, conversation)
to make your selection.

User Query:
"{user_query}"

Based on the query, which model is the most appropriate?
Return only the name of the model (e.g., 'claude', 'chatgpt', 'gemini') and nothing else.
Do not provide any explanation, preamble, or punctuation.
"""

prompt_template = ChatPromptTemplate.from_template(ROUTING_PROMPT_TEMPLATE)
output_parser = StrOutputParser()

# Create the routing chain using LangChain Expression Language (LCEL)
routing_chain = prompt_template | router_llm | output_parser

async def route_query_to_best_llm(user_query: str) -> dict:
    """
    Orchestrates routing a query to the best LLM using a LangChain-based router.
    """
    available_models_str = ", ".join(AVAILABLE_LLM_NAMES)
    print("here is bereket ")
    try:
        
        # Invoke the chain asynchronously
        llm_choice = await routing_chain.ainvoke({
            "available_models": available_models_str,
            "user_query": user_query
        })
        
        # Clean the output just in case the LLM adds extra text
        match = re.search(r'\b(' + '|'.join(AVAILABLE_LLM_NAMES) + r')\b', llm_choice.lower())
        print(f"match in using the gemini router: {match}")
        if not match:
            print(f"Router LLM returned an invalid choice: '{llm_choice}'. Defaulting to chatgpt.")
            llm_choice = "chatgpt" # Fallback to a default
        else:
            llm_choice = match.group(0)

    except Exception as e:
        print(f"Error during LangChain routing: {e}. Defaulting to chatgpt.")
        llm_choice = "chatgpt" # Fallback on API error

    if llm_choice not in LLM_REGISTRY:
        return {"error": f"Internal Error: Chosen LLM '{llm_choice}' is not available in the registry."}

    # Delegate the query to the selected LLM
    selected_llm = LLM_REGISTRY[llm_choice]
    final_response = await selected_llm.generate_response(user_query)

    return {
        "llm_used": llm_choice,
        "response": final_response
    }