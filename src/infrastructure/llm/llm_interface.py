from abc import ABC, abstractmethod

class LLMInterface(ABC):
    """
    Abstract Base Class for all LLM implementations.
    Ensures that any new LLM integration will have a consistent interface.
    """
    @abstractmethod
    async def generate_response(self, prompt: str ,  history: str) -> str:
        """
        Generates a response from the language model for a given prompt.
        considering the conversation history.

        Args:
            prompt: The user query or prompt to send to the LLM.
            history: A formatted string of the past conversation.

        Returns:
            The text response from the LLM.
        """
        pass