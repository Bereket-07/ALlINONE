from datetime import datetime
import re
import logging
from fastapi import logger
from langchain_openai import ChatOpenAI
from pytz import timezone

logger = logging.getLogger(__name__)
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from fastapi import UploadFile
from src.config import OPENAI_API_KEY
from src.config import GOOGLE_API_KEY
from src.infrastructure.llm.llm_list import LLM_REGISTRY, AVAILABLE_LLM_NAMES , MODEL_DESCRIPTIONS   # LLM_NAME_TO_CLASS         
from src.infrastructure.services.service_factory import ServiceFactory
from src.utils.pdf_processor import DocumentProcessor
from src.domain.models.llm_selection import FileQueryRequest, ProcessedFileContent
from typing import List, Dict, Any, Optional

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
and there descriptions {model_descriptions}

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

async def route_query_to_best_llm(user_query: str , user_id: str, conversation_id: str) -> dict:
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
        history = await firestore_service.get_last_n_conversations(user_id, conversation_id, limit=10)
    
    formatted_history = _format_history_for_prompt(history)
    # --- END HISTORY FETCH ---
    
    available_models_str = ", ".join(AVAILABLE_LLM_NAMES)
    model_descriptions = ", ".join([f"{name}: {desc}" for name, desc in MODEL_DESCRIPTIONS.items()])
    try:
        # Invoke the chain asynchronously
        llm_choice = await routing_chain.ainvoke({
            "available_models": available_models_str,
            "conversation_history": formatted_history,
            "user_query": user_query,
            "model_descriptions": model_descriptions
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
    final_response = await selected_llm.generate_response(user_query , formatted_history)

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

async def route_file_query_to_best_llm(file: UploadFile, request: FileQueryRequest, user_id: str, conversation_id) -> dict:
    """
    Orchestrates processing a file with optional query, routes to the best LLM, and returns response.
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Step 1: Extract content from document file
        file_content = await DocumentProcessor.extract_document_content(file)
        logger.info(f"Successfully extracted content from {file_content.filename} for user {user_id}")
        
        # Step 2: Generate appropriate prompt based on file content and query
        file_prompt = DocumentProcessor.generate_file_insights_prompt(file_content, request.query)
        
        # Step 3: Fetch conversation history
        firestore_service = ServiceFactory.get_firestore_service()
        if not firestore_service:
            logger.error("Firestore service not available for fetching history.")
            history = []
        else:
            if not conversation_id:
                # If no conversation ID provided, create a new session
                conversation_id = await firestore_service.create_conversation_session(user_id)
            history = await firestore_service.get_last_n_conversations(user_id, conversation_id, limit=10)
        
        formatted_history = _format_history_for_prompt(history)
        
        # Step 4: Route to best LLM using the file-aware prompt
        available_models_str = ", ".join(AVAILABLE_LLM_NAMES)
        model_descriptions = ", ".join([f"{name}: {desc}" for name, desc in MODEL_DESCRIPTIONS.items()])
        
        try:
            # For file-based queries, we use a modified routing prompt that considers file analysis
            file_routing_prompt = f"""
You are an intelligent routing system for file analysis queries. Your task is to select the best language model
to analyze a file and answer questions about it. You must choose from: [{available_models_str}].

Model descriptions: {model_descriptions}

Consider the conversation history: {formatted_history}

The user has uploaded a file and wants analysis. The content involves detailed document analysis.
Choose the model best suited for comprehensive document analysis and insights.

Query type: {"File analysis with specific question" if request.query else "General file insights"}

Return only the model name (e.g., 'claude', 'chatgpt', 'gemini') and nothing else.
"""
            
            # Invoke the routing chain
            llm_choice = await routing_chain.ainvoke({
                "available_models": available_models_str,
                "conversation_history": formatted_history,
                "user_query": file_routing_prompt,
                "model_descriptions": model_descriptions
            })
            
            # Clean the output
            match = re.search(r'\b(' + '|'.join(AVAILABLE_LLM_NAMES) + r')\b', llm_choice.lower())
            if not match:
                logger.warning(f"Router LLM returned invalid choice: '{llm_choice}'. Defaulting to chatgpt.")
                llm_choice = "chatgpt"
            else:
                llm_choice = match.group(0)
                
        except Exception as e:
            logger.error(f"Error during LangChain routing for file query: {e}. Defaulting to chatgpt.")
            llm_choice = "chatgpt"
        
        if llm_choice not in LLM_REGISTRY:
            return {"error": f"Internal Error: Chosen LLM '{llm_choice}' is not available in the registry."}
        
        # Step 5: Generate response using selected LLM
        selected_llm = LLM_REGISTRY[llm_choice]
        final_response = await selected_llm.generate_response(file_prompt, formatted_history)
        
        # Step 6: Save conversation with file context
        try:
            if firestore_service:
                # Create a summary of the file for history
                file_summary = DocumentProcessor.create_file_summary_for_history(file_content)
                query_for_history = request.query if request.query else "[File analysis request]"
                
                conversation_data = {
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "title": f"File Analysis: {file_content.filename}",
                    "created_at": datetime.now(timezone('UTC')),
                    "query": f"{query_for_history}\n\n{file_summary}",
                    "response": final_response,
                    "llm_used": llm_choice,
                    "file_info": {
                        "filename": file_content.filename,
                        "file_type": file_content.file_type,
                        "page_count": file_content.page_count,
                        "file_size": file_content.file_size
                    }
                }
                await firestore_service.add_conversation_turn(conversation_data)
            else:
                logger.error("Could not get Firestore service to save file conversation.")
        except Exception as e:
            logger.error(f"Failed to save file conversation for user {user_id}: {e}")
        
        # Step 7: Return response with file information
        return {
            "llm_used": llm_choice,
            "response": final_response,
            "conversation_id": conversation_id,
            "file_processed": file_content,
        }
        
    except Exception as e:
        logger.error(f"Error in route_file_query_to_best_llm: {e}")
        return {"error": f"Failed to process file query: {str(e)}"}

async def route_unified_query_to_best_llm(query: Optional[str], files: Optional[List[UploadFile]], user_id: str, conversation_id) -> dict:
    """
    Unified routing function that handles both text-only queries and queries with file attachments.
    
    Args:
        query: User query text (can be empty if only files are provided)
        files: Optional list of uploaded files (currently supports PDF)
        user_id: User identifier
        
    Returns:
        Response dictionary with LLM choice, response, and optional file processing info
    """
    logger = logging.getLogger(__name__)
    
    # Check if files are provided first
    valid_files = []
    if files and len(files) > 0:
        valid_files = [f for f in files if f and f.filename]
    
    # Determine if we have a valid query
    has_query = query and query.strip()
    has_files = len(valid_files) > 0
    
    # Handle file-only scenario (no query but files provided)
    if has_files and not has_query:
        # Generate default insights query for file analysis
        default_query = """Please provide a comprehensive analysis and insights about this document. Include:

1. **Document Summary**: What is this document about and what is its main purpose?
2. **Key Topics & Themes**: What are the main subjects, topics, or themes covered?
3. **Important Information**: Highlight the most significant findings, data, statistics, or facts
4. **Structure & Organization**: How is the document organized and what are its main sections?
5. **Key Takeaways**: What are the most important points or conclusions?
6. **Actionable Items**: Any recommendations, next steps, or action items mentioned
7. **Context & Significance**: What is the broader context and why is this document important?

Provide a detailed, well-structured analysis that would help someone quickly understand the essence and value of this document."""
        
        logger.info(f"No query provided, using default insights query for file analysis (user: {user_id})")
        query = default_query
        has_query = True
    
    # Validate that we have either a query or files
    if not has_query and not has_files:
        return {"error": "Either a query or file must be provided"}
    
    # At this point, we should have a valid query (either original or generated)
    if not has_query:
        return {"error": "Internal error: Query validation failed"}
    
    # Check if files are provided and process accordingly
    if has_files:
        # Process with files
        # logger.info(f"Processing query with {len(valid_files)} file(s) for user {user_id}")
        
        if len(valid_files) > 1:
            # Multiple files - process the first PDF for now
            # TODO: In future, could combine multiple files
            logger.warning(f"Multiple files uploaded, processing only the first one: {valid_files[0].filename}")
        
        # Use the first valid file
        file_to_process = valid_files[0]
        
        # Create file request object
        file_request = FileQueryRequest(query=query)
        
        # Route to file processing logic
        return await route_file_query_to_best_llm(file_to_process, file_request, user_id, conversation_id)
    
    # No valid files, process as regular text query
    if not query or not query.strip():
        return {
            "error": "Either query or files must be provided"
        }
    
    logger.info(f"Processing text-only query for user {user_id}")
    return await route_query_to_best_llm(query, user_id=user_id, conversation_id=conversation_id)