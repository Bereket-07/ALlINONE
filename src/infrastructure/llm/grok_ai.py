from langchain_xai import ChatXAI
from langchain_core.messages import HumanMessage
from src.config import XAI_API_KEY
from src.infrastructure.llm.llm_interface import LLMInterface

class GrokAi(LLMInterface):
    """LangChain implementation for grok's ."""
    def __init__(self, model: str = "grok-beta"):
        self.model = ChatXAI(
            model=model, 
            api_key=XAI_API_KEY, 
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
            return "Error: Could not get a response from grok."