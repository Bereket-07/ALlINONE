from src.infrastructure.llm.chatgpt_llm import ChatGPTLLM
from src.infrastructure.llm.claude_llm import ClaudeLLM
from src.infrastructure.llm.gemini_llm import GeminiLLM

# The LLM Registry holds instances of all available worker LLMs.
# New models can be added here.
LLM_REGISTRY = {
    "chatgpt": ChatGPTLLM(),
    "claude": ClaudeLLM(),
    "gemini": GeminiLLM(),
}

# This list is exposed to the Router LLM so it knows its options.
AVAILABLE_LLM_NAMES = list(LLM_REGISTRY.keys())