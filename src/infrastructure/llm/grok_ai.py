from langchain_openai import OpenAI
from langchain_core.messages import HumanMessage
from src.config import OPENAI_API_KEY
from src.infrastructure.llm.llm_interface import LLMInterface

class GrokAi(LLMInterface):
    """LangChain implementation for OpenAI's ChatGPT."""
    def __init__(self, model: str = "grok-beta"):
        self.model = ChatOpenAI(
            model=model, 
            api_key=OPENAI_API_KEY, 
            temperature=0.7, 
            max_tokens=1500
        )

    async def generate_response(self, prompt: str,history: str) -> str:
        try:
            full_context = f"""Here is the conversation history:
                    {history}

                    Given this history, continue the conversation by responding to the following user input.

                    User: {prompt}
                    AI:"""
            messages = [HumanMessage(content=full_context)]
            response = await self.model.ainvoke(messages)
            return response.content
        except Exception as e:
            print(f"Error calling ChatGPT via LangChain: {e}")
            return "Error: Could not get a response from ChatGPT."