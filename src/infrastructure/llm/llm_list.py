from src.infrastructure.llm.chatgpt_llm import ChatGPTLLM
from src.infrastructure.llm.claude_llm import ClaudeLLM
from src.infrastructure.llm.gemini_llm import GeminiLLM
from src.infrastructure.llm.grok_ai import GrokAi
from src.infrastructure.apis.eleven_labs import ElevenLabsLLM
from src.infrastructure.apis.stability import StabilityAIClient
from src.infrastructure.apis.runway import RunwayClient

# The LLM Registry holds instances of all available worker LLMs.
# New models can be added here.
LLM_REGISTRY = {
    "chatgpt": ChatGPTLLM(),
    "claude": ClaudeLLM(),
    "gemini": GeminiLLM(),
    "elevenlabs": ElevenLabsLLM(),
    "stability": StabilityAIClient(),
    "runway": RunwayClient(),
    "grok": GrokAi(),
}

# This list is exposed to the Router LLM so it knows its options.
AVAILABLE_LLM_NAMES = list(LLM_REGISTRY.keys())

MODEL_DESCRIPTIONS = {
    "chatgpt": "General-purpose conversational AI for natural language understanding, writing, Q&A, and summaries.",
    # "claude": "Conversational AI known for thoughtful, safe, and ethical long-form dialogue and reasoning.",
    "gemini": "Multimodal LLM by Google for advanced text and image understanding, contextual and creative tasks.",
    # "copyai": "AI copywriting assistant for marketing content like product descriptions, ads, and emails.",
    "elevenlabs": "Text-to-speech tool that generates high-quality, realistic voice audio from text.",
    # "hootsuite": "Social media automation assistant for creating, scheduling, and optimizing posts.",
    # "powerbi": "BI assistant to help generate reports, dashboards, and queries from natural language for Power BI.",
    "runway": "Creative visual generation tool to create images and short videos from descriptive text prompts.",
    # "similarweb": "Analytics tool for retrieving web traffic and performance insights of domains and competitors.",
    # "slidespeak": "Presentation assistant to convert slides to summaries or generate presentation scripts.",
    "stability": "Image generator using Stable Diffusion to create visuals from descriptive text prompts.",
    "grok": "Conversational AI optimized for real-time data such as trending tweets, news, and live internet chatter—ideal for timely, context-aware responses.",
}
