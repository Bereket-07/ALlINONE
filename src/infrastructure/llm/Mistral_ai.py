from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage
from src.config import MISTRAL_API_KEY
from src.infrastructure.llm.llm_interface import LLMInterface

class MistralAi(LLMInterface):
    """LangChain implementation for MistralAi."""
    def __init__(self, model: str = "mistral-large-latest"):
        self.model = ChatMistralAI(
            model=model,
            mistral_api_key=MISTRAL_API_KEY,
            temperature=0.7,
            max_output_tokens=1500
        )

    async def generate_response(self, prompt: str , history: str) -> str:
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
            print(f"Error calling MistralAi via LangChain: {e}")
            return "Error: Could not get a response from MistralAi."