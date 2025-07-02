from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from src.config import GOOGLE_API_KEY
from src.infrastructure.llm.llm_interface import LLMInterface

class GeminiLLM(LLMInterface):
    """LangChain implementation for Google's Gemini."""
    def __init__(self, model: str = "gemini-2.5-flash"):
        self.model = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=GOOGLE_API_KEY,
            temperature=0.7,
            max_output_tokens=1500
        )

    async def generate_response(self, prompt: str) -> str:
        try:
            messages = [HumanMessage(content=prompt)]
            response = await self.model.ainvoke(messages)
            return response.content
        except Exception as e:
            print(f"Error calling Gemini via LangChain: {e}")
            return "Error: Could not get a response from Gemini."