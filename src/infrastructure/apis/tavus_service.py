import asyncio
import aiohttp
import json
import base64
from typing import Optional, Dict, Any, List
from src.config import TAVUS_API_KEY, TAVUS_BASE_URL

class TavusService:
    """Service for Tavus video personalization and AI video generation"""
    
    def __init__(self):
        self.api_key = TAVUS_API_KEY
        self.base_url = TAVUS_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def create_video(self, 
                          template_id: str,
                          personalizations: List[Dict],
                          output_format: str = "mp4") -> Dict[str, Any]:
        """Create personalized video using Tavus"""
        try:
            if not self.api_key:
                return {"error": "Tavus API key not configured"}
            
            url = f"{self.base_url}/videos"
            
            payload = {
                "template_id": template_id,
                "personalizations": personalizations,
                "output_format": output_format
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "video_id": result.get("id"),
                            "status": result.get("status"),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Video creation failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Video creation error: {str(e)}"}
    
    async def get_video_status(self, video_id: str) -> Dict[str, Any]:
        """Get video generation status"""
        try:
            if not self.api_key:
                return {"error": "Tavus API key not configured"}
            
            url = f"{self.base_url}/videos/{video_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "video": result,
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Failed to get video status: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Get video status error: {str(e)}"}
    
    async def get_templates(self) -> Dict[str, Any]:
        """Get available video templates"""
        try:
            if not self.api_key:
                return {"error": "Tavus API key not configured"}
            
            url = f"{self.base_url}/templates"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "templates": result.get("templates", []),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Failed to get templates: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Get templates error: {str(e)}"}
    
    async def upload_template(self, video_file: bytes, name: str, description: str = "") -> Dict[str, Any]:
        """Upload a new video template"""
        try:
            if not self.api_key:
                return {"error": "Tavus API key not configured"}
            
            url = f"{self.base_url}/templates"
            
            # Prepare form data
            data = aiohttp.FormData()
            data.add_field('video', video_file, 
                         filename='template.mp4',
                         content_type='video/mp4')
            data.add_field('name', name)
            data.add_field('description', description)
            
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "template_id": result.get("id"),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Template upload failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Template upload error: {str(e)}"}
    
    async def delete_video(self, video_id: str) -> Dict[str, Any]:
        """Delete a video"""
        try:
            if not self.api_key:
                return {"error": "Tavus API key not configured"}
            
            url = f"{self.base_url}/videos/{video_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.delete(url, headers=self.headers) as response:
                    if response.status == 200:
                        return {"status": "success", "message": "Video deleted"}
                    else:
                        error_text = await response.text()
                        return {"error": f"Failed to delete video: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Delete video error: {str(e)}"}
    
    async def get_video_download_url(self, video_id: str) -> Dict[str, Any]:
        """Get download URL for generated video"""
        try:
            if not self.api_key:
                return {"error": "Tavus API key not configured"}
            
            url = f"{self.base_url}/videos/{video_id}/download"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "download_url": result.get("download_url"),
                            "expires_at": result.get("expires_at"),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Failed to get download URL: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Get download URL error: {str(e)}"} 