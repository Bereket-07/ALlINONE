from langchain.chat_models import ChatPerplexity
from langchain_core.messages import HumanMessage
from src.config import GOOGLE_API_KEY
from src.infrastructure.llm.llm_interface import LLMInterface

class PerplexityAi(LLMInterface):
    """LangChain implementation for PerplexityAi."""
    def __init__(self, model: str = "sonar"):
        self.model = ChatPerplexity(
            model=model,
            google_api_key=PPLX_API_KEY,
            temperature=0.7,
            max_output_tokens=1500
        )

    async def generate_response(self, prompt: str) -> str:
        try:
            messages = [HumanMessage(content=prompt)]
            response = await self.model.ainvoke(messages)
            return response.content
        except Exception as e:
            print(f"Error calling PerplexityAi via LangChain: {e}")
            return "Error: Could not get a response from PerplexityAi."