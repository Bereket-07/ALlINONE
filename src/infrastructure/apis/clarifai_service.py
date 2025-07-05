import asyncio
import aiohttp
import json
import base64
from typing import Optional, Dict, Any, List
from src.config import CLARIFAI_API_KEY, CLARIFAI_BASE_URL

class ClarifaiService:
    """Service for Clarifai image recognition and AI models"""
    
    def __init__(self):
        self.api_key = CLARIFAI_API_KEY
        self.base_url = CLARIFAI_BASE_URL
        self.headers = {
            "Authorization": f"Key {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def analyze_image(self, image_data: bytes, 
                          model_id: str = "general-image-recognition",
                          user_id: str = "clarifai",
                          app_id: str = "main") -> Dict[str, Any]:
        """Analyze image using Clarifai models"""
        try:
            if not self.api_key:
                return {"error": "Clarifai API key not configured"}
            
            url = f"{self.base_url}/users/{user_id}/apps/{app_id}/models/{model_id}/outputs"
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            payload = {
                "inputs": [
                    {
                        "data": {
                            "image": {
                                "base64": image_base64
                            }
                        }
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "predictions": result.get("outputs", [{}])[0].get("data", {}),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Image analysis failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Image analysis error: {str(e)}"}
    
    async def detect_concepts(self, image_data: bytes, 
                            concepts: Optional[List[str]] = None) -> Dict[str, Any]:
        """Detect specific concepts in image"""
        try:
            if not self.api_key:
                return {"error": "Clarifai API key not configured"}
            
            url = f"{self.base_url}/users/clarifai/apps/main/models/general-image-recognition/outputs"
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            payload = {
                "inputs": [
                    {
                        "data": {
                            "image": {
                                "base64": image_base64
                            }
                        }
                    }
                ]
            }
            
            if concepts:
                payload["model"] = {
                    "output_info": {
                        "output_config": {
                            "select_concepts": [{"name": concept} for concept in concepts]
                        }
                    }
                }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        concepts_data = result.get("outputs", [{}])[0].get("data", {}).get("concepts", [])
                        return {
                            "concepts": concepts_data,
                            "count": len(concepts_data),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Concept detection failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Concept detection error: {str(e)}"}
    
    async def detect_faces(self, image_data: bytes) -> Dict[str, Any]:
        """Detect faces in image"""
        try:
            if not self.api_key:
                return {"error": "Clarifai API key not configured"}
            
            url = f"{self.base_url}/users/clarifai/apps/main/models/face-detection/outputs"
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            payload = {
                "inputs": [
                    {
                        "data": {
                            "image": {
                                "base64": image_base64
                            }
                        }
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        regions = result.get("outputs", [{}])[0].get("data", {}).get("regions", [])
                        return {
                            "faces": regions,
                            "count": len(regions),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Face detection failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Face detection error: {str(e)}"}
    
    async def detect_text(self, image_data: bytes) -> Dict[str, Any]:
        """Extract text from image (OCR)"""
        try:
            if not self.api_key:
                return {"error": "Clarifai API key not configured"}
            
            url = f"{self.base_url}/users/clarifai/apps/main/models/ocr-scene/outputs"
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            payload = {
                "inputs": [
                    {
                        "data": {
                            "image": {
                                "base64": image_base64
                            }
                        }
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        regions = result.get("outputs", [{}])[0].get("data", {}).get("regions", [])
                        
                        # Extract text from regions
                        text_data = []
                        for region in regions:
                            for line in region.get("data", {}).get("lines", []):
                                for word in line.get("data", {}).get("words", []):
                                    text_data.append({
                                        "text": word.get("data", {}).get("text", ""),
                                        "confidence": word.get("value", 0),
                                        "bbox": word.get("data", {}).get("bbox", {})
                                    })
                        
                        return {
                            "text": " ".join([item["text"] for item in text_data]),
                            "words": text_data,
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Text detection failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Text detection error: {str(e)}"}
    
    async def get_models(self, user_id: str = "clarifai") -> Dict[str, Any]:
        """Get available models"""
        try:
            if not self.api_key:
                return {"error": "Clarifai API key not configured"}
            
            url = f"{self.base_url}/users/{user_id}/models"
            
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
    
    async def predict_with_custom_model(self, image_data: bytes,
                                      model_id: str,
                                      user_id: str,
                                      app_id: str) -> Dict[str, Any]:
        """Use a custom trained model for prediction"""
        try:
            if not self.api_key:
                return {"error": "Clarifai API key not configured"}
            
            url = f"{self.base_url}/users/{user_id}/apps/{app_id}/models/{model_id}/outputs"
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            payload = {
                "inputs": [
                    {
                        "data": {
                            "image": {
                                "base64": image_base64
                            }
                        }
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "predictions": result.get("outputs", [{}])[0].get("data", {}),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Custom model prediction failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Custom model prediction error: {str(e)}"} 