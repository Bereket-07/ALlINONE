import re
import logging
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.config import OPENAI_API_KEY
from src.config import GOOGLE_API_KEY
from src.infrastructure.llm.llm_list import LLM_REGISTRY, AVAILABLE_LLM_NAMES
from src.infrastructure.services.service_factory import ServiceFactory

# Define the Router LLM using LangChain
router_llm = ChatGoogleGenerativeAI(
            model='gemini-2.5-flash',
            google_api_key=GOOGLE_API_KEY,
            temperature=0.7,
            max_output_tokens=1500
        )

# Define the prompt template for the router
ROUTING_PROMPT_TEMPLATE = """
You are an intelligent routing system. Your task is to select the best language model
to answer a given user query. You must choose from the following available models: [{available_models}].

Consider the query's nature AND the preceding conversation history to make your selection.
For example, if the history is about coding, a follow-up question is likely also about coding.

CONVERSATION HISTORY:
{conversation_history}

LATEST USER QUERY:
"{user_query}"

Based on the history and the latest query, which model is the most appropriate?
Return only the name of the model (e.g., 'claude', 'chatgpt', 'gemini') and nothing else.
"""

prompt_template = ChatPromptTemplate.from_template(ROUTING_PROMPT_TEMPLATE)
output_parser = StrOutputParser()

# Create the routing chain using LangChain Expression Language (LCEL)
routing_chain = prompt_template | router_llm | output_parser


def _format_history_for_prompt(history: List[Dict[str, Any]]) -> str:
    """Formats a list of conversation turns into a single string."""
    if not history:
        return "No history yet. This is the first message."
    
    formatted_history = []
    for turn in history:
        formatted_history.append(f"Human: {turn.get('query', '')}")
        formatted_history.append(f"AI: {turn.get('response', '')}")
        
    return "\n".join(formatted_history)

async def route_query_to_best_llm(user_query: str , user_id: str) -> dict:
    """
    Orchestrates routing a query to the best LLM using a LangChain-based router.
    """

        # --- FETCH AND FORMAT HISTORY ---
    firestore_service = ServiceFactory.get_firestore_service()
    if not firestore_service:
        logger.error("Firestore service not available for fetching history.")
        # We can continue without history, but it's a degraded experience
        history = []
    else:
        history = await firestore_service.get_last_n_conversations(user_id, limit=10)
    
    formatted_history = _format_history_for_prompt(history)
    # --- END HISTORY FETCH ---
    
    available_models_str = ", ".join(AVAILABLE_LLM_NAMES)
    try:
        # Invoke the chain asynchronously
        llm_choice = await routing_chain.ainvoke({
            "available_models": available_models_str,
            "conversation_history": formatted_history,
            "user_query": user_query
        })
        
        # Clean the output just in case the LLM adds extra text
        match = re.search(r'\b(' + '|'.join(AVAILABLE_LLM_NAMES) + r')\b', llm_choice.lower())
        print(f"match in using the gemini router: {match}")
        if not match:
            print(f"Router LLM returned an invalid choice: '{llm_choice}'. Defaulting to chatgpt.")
            llm_choice = "gemini" # Fallback to a default
        else:
            llm_choice = match.group(0)

    except Exception as e:
        print(f"Error during LangChain routing: {e}. Defaulting to chatgpt.")
        llm_choice = "gemini" # Fallback on API error

    if llm_choice not in LLM_REGISTRY:
        return {"error": f"Internal Error: Chosen LLM '{llm_choice}' is not available in the registry."}

    # Delegate the query to the selected LLM
    selected_llm = LLM_REGISTRY[llm_choice]
    final_response = await selected_llm.generate_response(user_query , history=formatted_history)

    try:
        firestore_service = ServiceFactory.get_firestore_service()
        if firestore_service:
            conversation_data = {
                "user_id": user_id,
                "query": user_query,
                "response": final_response,
                "llm_used": llm_choice
            }
            await firestore_service.add_conversation_turn(conversation_data)
        else:
            logger.error("Could not get Firestore service to save conversation.")
    except Exception as e:
        # We log the error but don't fail the request. The user should still get their answer.
        logger.error(f"Failed to save conversation for user {user_id}: {e}")

    return {
        "llm_used": llm_choice,
        "response": final_response
    }