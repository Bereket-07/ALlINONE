import asyncio
import aiohttp
import json
import base64
from typing import Optional, Dict, Any, List
from src.config import PELTARION_API_KEY, PELTARION_BASE_URL

class PeltarionService:
    """Service for Peltarion Platform API machine learning models"""
    
    def __init__(self):
        self.api_key = PELTARION_API_KEY
        self.base_url = PELTARION_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def predict(self, model_id: str, 
                     input_data: Dict[str, Any],
                     deployment_id: Optional[str] = None) -> Dict[str, Any]:
        """Make prediction using Peltarion model"""
        try:
            if not self.api_key:
                return {"error": "Peltarion API key not configured"}
            
            # Use deployment_id if provided, otherwise use model_id
            endpoint_id = deployment_id or model_id
            url = f"{self.base_url}/deployments/{endpoint_id}/predict"
            
            payload = {
                "instances": [input_data]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "predictions": result.get("predictions", []),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Prediction failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Prediction error: {str(e)}"}
    
    async def batch_predict(self, model_id: str,
                          input_data_list: List[Dict[str, Any]],
                          deployment_id: Optional[str] = None) -> Dict[str, Any]:
        """Make batch predictions using Peltarion model"""
        try:
            if not self.api_key:
                return {"error": "Peltarion API key not configured"}
            
            # Use deployment_id if provided, otherwise use model_id
            endpoint_id = deployment_id or model_id
            url = f"{self.base_url}/deployments/{endpoint_id}/predict"
            
            payload = {
                "instances": input_data_list
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "predictions": result.get("predictions", []),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Batch prediction failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Batch prediction error: {str(e)}"}
    
    async def get_deployments(self) -> Dict[str, Any]:
        """Get available model deployments"""
        try:
            if not self.api_key:
                return {"error": "Peltarion API key not configured"}
            
            url = f"{self.base_url}/deployments"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "deployments": result.get("deployments", []),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Failed to get deployments: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Get deployments error: {str(e)}"}
    
    async def get_deployment_info(self, deployment_id: str) -> Dict[str, Any]:
        """Get information about a specific deployment"""
        try:
            if not self.api_key:
                return {"error": "Peltarion API key not configured"}
            
            url = f"{self.base_url}/deployments/{deployment_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "deployment": result,
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Failed to get deployment info: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Get deployment info error: {str(e)}"}
    
    async def get_models(self) -> Dict[str, Any]:
        """Get available models"""
        try:
            if not self.api_key:
                return {"error": "Peltarion API key not configured"}
            
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
    
    async def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        try:
            if not self.api_key:
                return {"error": "Peltarion API key not configured"}
            
            url = f"{self.base_url}/models/{model_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "model": result,
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Failed to get model info: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Get model info error: {str(e)}"}
    
    async def get_deployment_metrics(self, deployment_id: str) -> Dict[str, Any]:
        """Get metrics for a deployment"""
        try:
            if not self.api_key:
                return {"error": "Peltarion API key not configured"}
            
            url = f"{self.base_url}/deployments/{deployment_id}/metrics"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "metrics": result,
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Failed to get deployment metrics: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Get deployment metrics error: {str(e)}"}
    
    async def create_deployment(self, model_id: str, 
                              deployment_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new deployment for a model"""
        try:
            if not self.api_key:
                return {"error": "Peltarion API key not configured"}
            
            url = f"{self.base_url}/deployments"
            
            payload = {
                "model_id": model_id,
                **deployment_config
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "deployment_id": result.get("id"),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Failed to create deployment: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Create deployment error: {str(e)}"}
    
    async def delete_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """Delete a deployment"""
        try:
            if not self.api_key:
                return {"error": "Peltarion API key not configured"}
            
            url = f"{self.base_url}/deployments/{deployment_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.delete(url, headers=self.headers) as response:
                    if response.status == 200:
                        return {"status": "success", "message": "Deployment deleted"}
                    else:
                        error_text = await response.text()
                        return {"error": f"Failed to delete deployment: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Delete deployment error: {str(e)}"} 