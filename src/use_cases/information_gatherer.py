import logging
from typing import Dict, Any, Generator

from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

from src.config import GOOGLE_API_KEY
from src.domain.models.task_tree import TaskTree
from src.infrastructure.firebase.firestore_service import FirestoreService

logger = logging.getLogger(__name__)

# --- LLM Setup with Memory for Conversational Question Generation ---
# We use a PromptTemplate that now includes chat history
QUESTION_PROMPT_WITH_MEMORY = PromptTemplate(
    input_variables=["history", "task_context", "parameter_name"],
    template="""
You are a helpful assistant. Your job is to ask a user clear, friendly questions to gather missing information.
Use the conversation history to sound natural and avoid repeating yourself.
The user is trying to accomplish a specific task. Use that context to make the question more relevant.
Do not add any preamble like "Great, the next question is:". Just return the question itself.

Current Conversation:
{history}

Task Context: The user wants to '{task_context}'.
Parameter to ask for: '{parameter_name}'

Your Question:
"""
)

# The LLM remains the same
question_generator_llm = ChatGoogleGenerativeAI(
    model='gemini-1.5-flash',
    google_api_key=GOOGLE_API_KEY,
    temperature=0.4, # Slightly higher temp for more natural phrasing
)

def create_question_generation_chain() -> LLMChain:
    """Creates an LLMChain with its own isolated memory for a single session."""
    # Memory is created here, so each conversation gets a fresh instance.
    memory = ConversationBufferMemory(input_key="parameter_name", memory_key="history")
    return LLMChain(
        llm=question_generator_llm,
        prompt=QUESTION_PROMPT_WITH_MEMORY,
        memory=memory,
        verbose=False # Set to True for debugging the chain's thoughts
    )


async def interactive_information_gathering_loop(user_id: str, task_tree: TaskTree) -> Generator[Dict[str, Any], str, None]:
    """
    An interactive generator that finds missing info, yields questions, and updates the DB.

    This function orchestrates the entire Q&A loop for a single task.
    - It finds all placeholders.
    - For each one, it yields a question and waits for an answer.
    - It updates the database after receiving each answer.

    Args:
        user_id: The ID of the current user.
        task_tree: The initial TaskTree object with placeholders.

    Yields:
        A dictionary like {"parameter_name": "departure_city", "question": "..."}

    Receives:
        The user's string answer via `generator.asend(answer)`.

    Returns:
        None. The generator signals completion by exiting. The task_tree object
        in the calling scope will be fully updated.
    """

    logger.info("--- Inside information_gatherer ---")
    logger.info(f"Task Tree object received: {task_tree.model_dump_json(indent=2)}")
    logger.info("--- End of object ---")

    # 1. Identify all placeholders that need to be filled
    placeholders = []
    for subtask in task_tree.subtasks:
        for key, value in subtask.payload.items():
            if isinstance(value, str) and value.startswith("USER_INPUT:"):
                placeholders.append((subtask, key, value.split(":", 1)[1]))

    if not placeholders:
        logger.info(f"Task {task_tree.task_tree_id} requires no user input. Completing.")
        if task_tree.status != "completed":
            task_tree.status = "completed"
            #
            # --- FIX 1: Correctly call save_task_tree to update the document ---
            #
            FirestoreService.save_task_tree(
                user_id=user_id,
                task_tree_data=task_tree.model_dump(),
                task_tree_id=task_tree.task_tree_id
            )
        # A bare return is valid to exit a generator early.
        return

    # 2. Setup for the conversation
    llm_chain = create_question_generation_chain()
    task_tree.status = "in_progress"
    #
    # --- FIX 2: Correctly call save_task_tree to update the document ---
    #
    FirestoreService.save_task_tree(
        user_id=user_id,
        task_tree_data=task_tree.model_dump(),
        task_tree_id=task_tree.task_tree_id
    )
    logger.info(f"Task {task_tree.task_tree_id} status set to 'in_progress'. Starting Q&A loop.")

    # 3. Loop through placeholders, asking questions and updating
    for subtask, key, param_name in placeholders:
        # Generate the question using the LLM chain (which includes memory)
        response = await llm_chain.ainvoke({
            "task_context": task_tree.task,
            "parameter_name": param_name
        })
        question = response['text'].strip()

        # Yield the question to the caller (e.g., the WebSocket) and wait for an answer
        answer = yield {"parameter_name": param_name, "question": question}

        # 4. Update the task tree in memory and in the database
        subtask.payload[key] = answer
        logger.info(f"Task {task_tree.task_tree_id}: Filled '{key}' with user answer. Updating DB.")
        #
        # --- FIX 3: Correctly call save_task_tree to update the document ---
        #
        FirestoreService.save_task_tree(
            user_id=user_id,
            task_tree_data=task_tree.model_dump(),
            task_tree_id=task_tree.task_tree_id
        )

    # 5. Finalize the process
    task_tree.status = "completed"
    logger.info(f"All information gathered for task {task_tree.task_tree_id}. Status set to 'completed'.")
    #
    # --- FIX 4: Correctly call save_task_tree to update the document ---
    #
    FirestoreService.save_task_tree(
        user_id=user_id,
        task_tree_data=task_tree.model_dump(),
        task_tree_id=task_tree.task_tree_id
    )
    
    # A generator must end with a bare `return` or just by falling off the end.
    return