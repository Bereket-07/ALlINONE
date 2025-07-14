import json
import httpx
from runwayml import RunwayML, TaskFailedError
from pydantic import BaseModel
from src.config import RUNWAY_API_KEY
from typing import Optional
from src.infrastructure.llm.llm_interface import LLMInterface

class RunwayInput(BaseModel):
    prompt: str
    model: str = "gen4_image"
    duration: int = 4
    width: int = 1280
    height: int = 720

class RunwayClient(LLMInterface):
    """
    Async-compatible Runway video/image generation client.
    Inherits from LLMInterface for compatibility with LLM workflows.
    """

    async def generate_response(self, prompt: str , history: str) -> str:
        """
        LLMInterface-compliant method: generate a video/image from a prompt string.
        Uses default model and parameters.
        """
        client = RunwayML(api_key=RUNWAY_API_KEY)

        try:
            task =await client.text_to_image.create(
                model="gen4_image",
                prompt_text=prompt,
                ratio="1024:1024",
            ).wait_for_task_output()
            
            response = {
                "output": task.output,
                "status": getattr(task, "status", None),
                "error": getattr(task, "error", None)
            }
            return json.dumps(response)

        except TaskFailedError as e:
            return json.dumps({"error": str(e)})

# def main():
#     client = RunwayClient()
#     prompt = "A futuristic city"
#     # Since generate_response is async, we need to run it in an event loop
#     import asyncio
#     result = asyncio.run(client.generate_response(prompt))
#     print("Result:", result)

# if __name__ == "__main__":
#     main()


