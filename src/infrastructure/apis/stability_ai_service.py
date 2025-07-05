import asyncio
import aiohttp
import json
import base64
from typing import Optional, Dict, Any, List
from src.config import STABILITY_AI_API_KEY, STABILITY_AI_BASE_URL

class StabilityAIService:
    """Service for Stability AI image generation"""
    
    def __init__(self):
        self.api_key = STABILITY_AI_API_KEY
        self.base_url = STABILITY_AI_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def generate_image(self, prompt: str, 
                           negative_prompt: str = "",
                           width: int = 1024,
                           height: int = 1024,
                           steps: int = 30,
                           cfg_scale: float = 7.0,
                           samples: int = 1,
                           seed: Optional[int] = None) -> Dict[str, Any]:
        """Generate image using Stability AI"""
        try:
            if not self.api_key:
                return {"error": "Stability AI API key not configured"}
            
            url = f"{self.base_url}/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
            
            payload = {
                "text_prompts": [
                    {
                        "text": prompt,
                        "weight": 1.0
                    }
                ],
                "cfg_scale": cfg_scale,
                "height": height,
                "width": width,
                "samples": samples,
                "steps": steps
            }
            
            if negative_prompt:
                payload["text_prompts"].append({
                    "text": negative_prompt,
                    "weight": -1.0
                })
            
            if seed is not None:
                payload["seed"] = seed
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "images": result.get("artifacts", []),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"API request failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Image generation error: {str(e)}"}
    
    async def upscale_image(self, image_data: bytes, 
                          width: int = 2048,
                          height: int = 2048) -> Dict[str, Any]:
        """Upscale image using Stability AI"""
        try:
            if not self.api_key:
                return {"error": "Stability AI API key not configured"}
            
            url = f"{self.base_url}/generation/esrgan-v1-x2plus/image-to-image/upscale"
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            payload = {
                "image": image_base64,
                "width": width,
                "height": height
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "images": result.get("artifacts", []),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Upscale failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Image upscale error: {str(e)}"}
    
    async def image_to_image(self, image_data: bytes,
                           prompt: str,
                           negative_prompt: str = "",
                           strength: float = 0.35,
                           steps: int = 30) -> Dict[str, Any]:
        """Image-to-image generation"""
        try:
            if not self.api_key:
                return {"error": "Stability AI API key not configured"}
            
            url = f"{self.base_url}/generation/stable-diffusion-xl-1024-v1-0/image-to-image"
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            payload = {
                "init_image": image_base64,
                "text_prompts": [
                    {
                        "text": prompt,
                        "weight": 1.0
                    }
                ],
                "image_strength": strength,
                "steps": steps
            }
            
            if negative_prompt:
                payload["text_prompts"].append({
                    "text": negative_prompt,
                    "weight": -1.0
                })
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "images": result.get("artifacts", []),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Image-to-image failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Image-to-image error: {str(e)}"}
    
    async def get_models(self) -> Dict[str, Any]:
        """Get available models"""
        try:
            if not self.api_key:
                return {"error": "Stability AI API key not configured"}
            
            url = f"{self.base_url}/models"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "models": result.get("models", []),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Failed to get models: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Get models error: {str(e)}"} 