import asyncio
import aiohttp
import json
import base64
from typing import Optional, Dict, Any, List
from src.config import GOOGLE_VISION_API_KEY, GOOGLE_VISION_BASE_URL

class GoogleVisionService:
    """Service for Google Vision API image analysis"""
    
    def __init__(self):
        self.api_key = GOOGLE_VISION_API_KEY
        self.base_url = GOOGLE_VISION_BASE_URL
    
    async def analyze_image(self, image_data: bytes, 
                          features: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analyze image using Google Vision API"""
        try:
            if not self.api_key:
                return {"error": "Google Vision API key not configured"}
            
            url = f"{self.base_url}/images:annotate?key={self.api_key}"
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Default features if none specified
            if not features:
                features = [
                    "LABEL_DETECTION",
                    "TEXT_DETECTION", 
                    "FACE_DETECTION",
                    "LANDMARK_DETECTION",
                    "LOGO_DETECTION",
                    "OBJECT_LOCALIZATION",
                    "SAFE_SEARCH_DETECTION"
                ]
            
            # Convert feature names to proper format
            feature_requests = []
            for feature in features:
                feature_requests.append({
                    "type": feature,
                    "maxResults": 10
                })
            
            payload = {
                "requests": [
                    {
                        "image": {
                            "content": image_base64
                        },
                        "features": feature_requests
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "analysis": result.get("responses", [{}])[0],
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Image analysis failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Image analysis error: {str(e)}"}
    
    async def detect_text(self, image_data: bytes) -> Dict[str, Any]:
        """Extract text from image (OCR)"""
        try:
            if not self.api_key:
                return {"error": "Google Vision API key not configured"}
            
            url = f"{self.base_url}/images:annotate?key={self.api_key}"
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            payload = {
                "requests": [
                    {
                        "image": {
                            "content": image_base64
                        },
                        "features": [
                            {
                                "type": "TEXT_DETECTION",
                                "maxResults": 1
                            }
                        ]
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        text_annotations = result.get("responses", [{}])[0].get("textAnnotations", [])
                        
                        if text_annotations:
                            full_text = text_annotations[0].get("description", "")
                            return {
                                "text": full_text,
                                "words": text_annotations[1:] if len(text_annotations) > 1 else [],
                                "status": "success"
                            }
                        else:
                            return {
                                "text": "",
                                "words": [],
                                "status": "success",
                                "message": "No text detected"
                            }
                    else:
                        error_text = await response.text()
                        return {"error": f"Text detection failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Text detection error: {str(e)}"}
    
    async def detect_faces(self, image_data: bytes) -> Dict[str, Any]:
        """Detect faces in image"""
        try:
            if not self.api_key:
                return {"error": "Google Vision API key not configured"}
            
            url = f"{self.base_url}/images:annotate?key={self.api_key}"
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            payload = {
                "requests": [
                    {
                        "image": {
                            "content": image_base64
                        },
                        "features": [
                            {
                                "type": "FACE_DETECTION",
                                "maxResults": 10
                            }
                        ]
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        faces = result.get("responses", [{}])[0].get("faceAnnotations", [])
                        
                        return {
                            "faces": faces,
                            "count": len(faces),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Face detection failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Face detection error: {str(e)}"}
    
    async def detect_objects(self, image_data: bytes) -> Dict[str, Any]:
        """Detect objects in image"""
        try:
            if not self.api_key:
                return {"error": "Google Vision API key not configured"}
            
            url = f"{self.base_url}/images:annotate?key={self.api_key}"
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            payload = {
                "requests": [
                    {
                        "image": {
                            "content": image_base64
                        },
                        "features": [
                            {
                                "type": "OBJECT_LOCALIZATION",
                                "maxResults": 10
                            }
                        ]
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        objects = result.get("responses", [{}])[0].get("localizedObjectAnnotations", [])
                        
                        return {
                            "objects": objects,
                            "count": len(objects),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Object detection failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Object detection error: {str(e)}"}
    
    async def detect_labels(self, image_data: bytes) -> Dict[str, Any]:
        """Detect labels/categories in image"""
        try:
            if not self.api_key:
                return {"error": "Google Vision API key not configured"}
            
            url = f"{self.base_url}/images:annotate?key={self.api_key}"
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            payload = {
                "requests": [
                    {
                        "image": {
                            "content": image_base64
                        },
                        "features": [
                            {
                                "type": "LABEL_DETECTION",
                                "maxResults": 10
                            }
                        ]
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        labels = result.get("responses", [{}])[0].get("labelAnnotations", [])
                        
                        return {
                            "labels": labels,
                            "count": len(labels),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Label detection failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Label detection error: {str(e)}"}
    
    async def safe_search_detection(self, image_data: bytes) -> Dict[str, Any]:
        """Detect safe search categories in image"""
        try:
            if not self.api_key:
                return {"error": "Google Vision API key not configured"}
            
            url = f"{self.base_url}/images:annotate?key={self.api_key}"
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            payload = {
                "requests": [
                    {
                        "image": {
                            "content": image_base64
                        },
                        "features": [
                            {
                                "type": "SAFE_SEARCH_DETECTION",
                                "maxResults": 1
                            }
                        ]
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        safe_search = result.get("responses", [{}])[0].get("safeSearchAnnotation", {})
                        
                        return {
                            "safe_search": safe_search,
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Safe search detection failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Safe search detection error: {str(e)}"} 