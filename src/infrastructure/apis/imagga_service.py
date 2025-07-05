import asyncio
import aiohttp
import json
import base64
from typing import Optional, Dict, Any, List
from src.config import IMAGGA_API_KEY, IMAGGA_BASE_URL

class ImaggaService:
    """Service for Imagga image analysis and tagging"""
    
    def __init__(self):
        self.api_key = IMAGGA_API_KEY
        self.base_url = IMAGGA_BASE_URL
        self.headers = {
            "Authorization": f"Basic {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def tag_image(self, image_data: bytes, 
                       language: str = "en",
                       limit: int = 10,
                       threshold: float = 30.0) -> Dict[str, Any]:
        """Tag image with descriptive labels"""
        try:
            if not self.api_key:
                return {"error": "Imagga API key not configured"}
            
            url = f"{self.base_url}/tags"
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            params = {
                "image_base64": image_base64,
                "language": language,
                "limit": limit,
                "threshold": threshold
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "tags": result.get("result", {}).get("tags", []),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Image tagging failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Image tagging error: {str(e)}"}
    
    async def categorize_image(self, image_data: bytes,
                             model: str = "general_v3",
                             language: str = "en") -> Dict[str, Any]:
        """Categorize image into predefined categories"""
        try:
            if not self.api_key:
                return {"error": "Imagga API key not configured"}
            
            url = f"{self.base_url}/categories/{model}"
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            params = {
                "image_base64": image_base64,
                "language": language
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "categories": result.get("result", {}).get("categories", []),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Image categorization failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Image categorization error: {str(e)}"}
    
    async def detect_colors(self, image_data: bytes,
                          palette_colors: int = 5,
                          extract_overall_colors: bool = True,
                          extract_object_colors: bool = False) -> Dict[str, Any]:
        """Detect colors in image"""
        try:
            if not self.api_key:
                return {"error": "Imagga API key not configured"}
            
            url = f"{self.base_url}/colors"
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            params = {
                "image_base64": image_base64,
                "palette_colors": palette_colors,
                "extract_overall_colors": extract_overall_colors,
                "extract_object_colors": extract_object_colors
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "colors": result.get("result", {}).get("colors", {}),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Color detection failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Color detection error: {str(e)}"}
    
    async def detect_faces(self, image_data: bytes) -> Dict[str, Any]:
        """Detect faces in image"""
        try:
            if not self.api_key:
                return {"error": "Imagga API key not configured"}
            
            url = f"{self.base_url}/faces/detections"
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            params = {
                "image_base64": image_base64
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "faces": result.get("result", {}).get("faces", []),
                            "count": len(result.get("result", {}).get("faces", [])),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Face detection failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Face detection error: {str(e)}"}
    
    async def extract_text(self, image_data: bytes,
                          language: str = "en") -> Dict[str, Any]:
        """Extract text from image (OCR)"""
        try:
            if not self.api_key:
                return {"error": "Imagga API key not configured"}
            
            url = f"{self.base_url}/text"
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            params = {
                "image_base64": image_base64,
                "language": language
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "text": result.get("result", {}).get("text", []),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Text extraction failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Text extraction error: {str(e)}"}
    
    async def detect_objects(self, image_data: bytes,
                           model: str = "general",
                           language: str = "en") -> Dict[str, Any]:
        """Detect objects in image"""
        try:
            if not self.api_key:
                return {"error": "Imagga API key not configured"}
            
            url = f"{self.base_url}/objects/detections"
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            params = {
                "image_base64": image_base64,
                "model": model,
                "language": language
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "objects": result.get("result", {}).get("objects", []),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Object detection failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Object detection error: {str(e)}"}
    
    async def analyze_image_complete(self, image_data: bytes) -> Dict[str, Any]:
        """Complete image analysis with all features"""
        try:
            if not self.api_key:
                return {"error": "Imagga API key not configured"}
            
            # Run all analyses in parallel
            tasks = [
                self.tag_image(image_data),
                self.categorize_image(image_data),
                self.detect_colors(image_data),
                self.detect_faces(image_data),
                self.detect_objects(image_data)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results
            analysis = {
                "tags": results[0].get("tags", []) if not isinstance(results[0], Exception) else [],
                "categories": results[1].get("categories", []) if not isinstance(results[1], Exception) else [],
                "colors": results[2].get("colors", {}) if not isinstance(results[2], Exception) else {},
                "faces": results[3].get("faces", []) if not isinstance(results[3], Exception) else [],
                "objects": results[4].get("objects", []) if not isinstance(results[4], Exception) else [],
                "status": "success"
            }
            
            return analysis
            
        except Exception as e:
            return {"error": f"Complete analysis error: {str(e)}"}
    
    async def get_usage_statistics(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        try:
            if not self.api_key:
                return {"error": "Imagga API key not configured"}
            
            url = f"{self.base_url}/usage"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "usage": result.get("result", {}),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Failed to get usage statistics: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Get usage statistics error: {str(e)}"} 