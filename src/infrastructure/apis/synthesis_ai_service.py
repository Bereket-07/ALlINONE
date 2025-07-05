import asyncio
import aiohttp
import json
import base64
from typing import Optional, Dict, Any, List
from src.config import SYNTHESIS_AI_API_KEY, SYNTHESIS_AI_BASE_URL

class SynthesisAIService:
    """Service for Synthesis AI synthetic data generation"""
    
    def __init__(self):
        self.api_key = SYNTHESIS_AI_API_KEY
        self.base_url = SYNTHESIS_AI_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_synthetic_data(self, 
                                    data_type: str,
                                    schema: Dict[str, Any],
                                    count: int = 100,
                                    seed: Optional[int] = None) -> Dict[str, Any]:
        """Generate synthetic data using Synthesis AI"""
        try:
            if not self.api_key:
                return {"error": "Synthesis AI API key not configured"}
            
            url = f"{self.base_url}/generate"
            
            payload = {
                "data_type": data_type,
                "schema": schema,
                "count": count
            }
            
            if seed is not None:
                payload["seed"] = seed
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "data": result.get("data", []),
                            "metadata": result.get("metadata", {}),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Data generation failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Data generation error: {str(e)}"}
    
    async def generate_synthetic_images(self,
                                      prompt: str,
                                      count: int = 1,
                                      width: int = 512,
                                      height: int = 512,
                                      style: Optional[str] = None) -> Dict[str, Any]:
        """Generate synthetic images"""
        try:
            if not self.api_key:
                return {"error": "Synthesis AI API key not configured"}
            
            url = f"{self.base_url}/images/generate"
            
            payload = {
                "prompt": prompt,
                "count": count,
                "width": width,
                "height": height
            }
            
            if style:
                payload["style"] = style
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "images": result.get("images", []),
                            "metadata": result.get("metadata", {}),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Image generation failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Image generation error: {str(e)}"}
    
    async def generate_synthetic_text(self,
                                    prompt: str,
                                    max_length: int = 1000,
                                    temperature: float = 0.7,
                                    count: int = 1) -> Dict[str, Any]:
        """Generate synthetic text"""
        try:
            if not self.api_key:
                return {"error": "Synthesis AI API key not configured"}
            
            url = f"{self.base_url}/text/generate"
            
            payload = {
                "prompt": prompt,
                "max_length": max_length,
                "temperature": temperature,
                "count": count
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "texts": result.get("texts", []),
                            "metadata": result.get("metadata", {}),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Text generation failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Text generation error: {str(e)}"}
    
    async def get_available_models(self) -> Dict[str, Any]:
        """Get available synthesis models"""
        try:
            if not self.api_key:
                return {"error": "Synthesis AI API key not configured"}
            
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
    
    async def validate_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a data schema"""
        try:
            if not self.api_key:
                return {"error": "Synthesis AI API key not configured"}
            
            url = f"{self.base_url}/validate/schema"
            
            payload = {
                "schema": schema
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "valid": result.get("valid", False),
                            "errors": result.get("errors", []),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Schema validation failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Schema validation error: {str(e)}"}
    
    async def get_generation_history(self, limit: int = 50) -> Dict[str, Any]:
        """Get generation history"""
        try:
            if not self.api_key:
                return {"error": "Synthesis AI API key not configured"}
            
            url = f"{self.base_url}/history?limit={limit}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "history": result.get("history", []),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Failed to get history: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Get history error: {str(e)}"}
    
    async def create_custom_model(self, 
                                name: str,
                                description: str,
                                training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a custom synthesis model"""
        try:
            if not self.api_key:
                return {"error": "Synthesis AI API key not configured"}
            
            url = f"{self.base_url}/models/custom"
            
            payload = {
                "name": name,
                "description": description,
                "training_data": training_data
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "model_id": result.get("model_id"),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Failed to create custom model: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Create custom model error: {str(e)}"}
    
    async def get_model_status(self, model_id: str) -> Dict[str, Any]:
        """Get status of a custom model"""
        try:
            if not self.api_key:
                return {"error": "Synthesis AI API key not configured"}
            
            url = f"{self.base_url}/models/{model_id}/status"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "status": result.get("status"),
                            "progress": result.get("progress", 0),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Failed to get model status: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Get model status error: {str(e)}"} 