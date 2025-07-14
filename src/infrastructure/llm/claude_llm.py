from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from src.config import ANTHROPIC_API_KEY
from src.infrastructure.llm.llm_interface import LLMInterface

class ClaudeLLM(LLMInterface):
    """LangChain implementation for Anthropic's Claude."""
    def __init__(self, model: str = "claude-3-haiku-20240307"):
        self.model = ChatAnthropic(
            model=model,
            api_key=ANTHROPIC_API_KEY,
            temperature=0.7,
            max_tokens_to_sample=1500
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
            print(f"Error calling Claude via LangChain: {e}")
            return "Error: Could not get a response from Claude."