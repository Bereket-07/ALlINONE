import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from src.config import GOOGLE_API_KEY
from src.domain.models.task_tree import TaskTree

logger = logging.getLogger(__name__)

# The Planner Agent LLM. Using a powerful model is key for good JSON output.
planner_llm = ChatGoogleGenerativeAI(
    model='gemini-1.5-flash', # A model good at following JSON instructions
    google_api_key=GOOGLE_API_KEY,
    temperature=0.1, # Low temperature for predictable, structured output
)

# This prompt is the "brain" of the Planner Agent. It instructs the LLM on its role,
# the available tools, and the required JSON output format.
PLANNER_PROMPT_TEMPLATE = """
You are a highly intelligent Planner Agent for an AI assistant called Allin1.
Your primary function is to receive a user query and decompose it into a structured JSON task tree.
You must strictly adhere to the provided JSON schema. Do not add any extra text or explanations.

Based on the user's query, identify ONE of the following main tasks:
"Flight Booking", "Send Email", "Schedule Meeting", "Trip Planning", "Order Food", "Post to X".

Then, break that task down into the necessary subtasks.

For the 'payload' of each subtask:
1. Extract any parameters you can directly from the user's query (e.g., "NYC" for destination).
2. If a parameter is MISSING and required for the function, use the placeholder format: "USER_INPUT:<parameter_name>"
   (e.g., "USER_INPUT:departure_city", "USER_INPUT:recipient_email").

Here is an example:
User Query: "Book a flight to NYC for next Friday"
Your JSON Output:
{{
    "user_query": "Book a flight to NYC for next Friday",
    "task": "Flight Booking",
    "subtasks": [
        {{
            "subtask_name": "Search for Flights",
            "function": "search_flights",
            "api": "Skyscanner API",
            "payload": {{
                "destination": "NYC",
                "date": "next Friday",
                "departure_city": "USER_INPUT:departure_city"
            }}
        }},
        {{
            "subtask_name": "Book the selected flight",
            "function": "book_flight",
            "api": "Skyscanner/Stripe API",
            "payload": {{
                "flight_id": "RESULT:search_flights:flight_id",
                "payment_details": "USER_INPUT:payment_method"
            }}
        }},
        {{
            "subtask_name": "Confirm booking via email",
            "function": "send_email",
            "api": "SendGrid API",
            "payload": {{
                "recipient": "USER_INPUT:user_email",
                "subject": "Your Flight to NYC is Booked!",
                "body": "Confirmation details for your flight."
            }}
        }}
    ]
}}

Now, process the following user query.

USER QUERY:
"{user_query}"

YOUR JSON OUTPUT:
"""

async def generate_task_tree(user_query: str) -> TaskTree:
    """
    Uses the Planner Agent LLM to parse a user query and build a structured TaskTree.
    This fulfills requirements FR1.2 and FR1.3.
    """
    parser = JsonOutputParser(pydantic_object=TaskTree)
    
    prompt = ChatPromptTemplate.from_template(
        template=PLANNER_PROMPT_TEMPLATE,
        partial_variables={"format_instructions": parser.get_format_instructions()} # This helps the LLM
    )
    
    # Create the chain: Prompt -> LLM -> JSON Parser
    chain = prompt | planner_llm | parser
    
    logger.info(f"Generating task tree for query: '{user_query}'")
    try:
        # Invoke the chain to get the structured TaskTree object
        task_tree_dict = await chain.ainvoke({"user_query": user_query})
        
        # We get a dict from the parser, so we create a TaskTree instance from it
        task_tree = TaskTree(**task_tree_dict)
        
        logger.info(f"Successfully generated task tree for task: {task_tree.task}")
        print(task_tree) 
        return task_tree
        
    except Exception as e:
        logger.error(f"Failed to generate or parse task tree: {e}")
        # In a real app, you might try a fallback or re-prompting logic here.
        raise ValueError(f"Could not generate a valid task plan for the query. Error: {e}")