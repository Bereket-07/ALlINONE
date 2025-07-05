import asyncio
import aiohttp
import json
import base64
from typing import Optional, Dict, Any, List
from src.config import LUMEN_API_KEY, LUMEN_BASE_URL

class LumenService:
    """Service for Lumen AI-powered analytics and insights"""
    
    def __init__(self):
        self.api_key = LUMEN_API_KEY
        self.base_url = LUMEN_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def analyze_data(self, 
                          data: List[Dict[str, Any]],
                          analysis_type: str = "general",
                          insights_count: int = 5) -> Dict[str, Any]:
        """Analyze data and generate insights using Lumen"""
        try:
            if not self.api_key:
                return {"error": "Lumen API key not configured"}
            
            url = f"{self.base_url}/analyze"
            
            payload = {
                "data": data,
                "analysis_type": analysis_type,
                "insights_count": insights_count
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "insights": result.get("insights", []),
                            "patterns": result.get("patterns", []),
                            "recommendations": result.get("recommendations", []),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Data analysis failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Data analysis error: {str(e)}"}
    
    async def generate_report(self,
                            data: List[Dict[str, Any]],
                            report_type: str = "comprehensive",
                            format: str = "json") -> Dict[str, Any]:
        """Generate comprehensive report from data"""
        try:
            if not self.api_key:
                return {"error": "Lumen API key not configured"}
            
            url = f"{self.base_url}/reports/generate"
            
            payload = {
                "data": data,
                "report_type": report_type,
                "format": format
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "report": result.get("report", {}),
                            "summary": result.get("summary", {}),
                            "visualizations": result.get("visualizations", []),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Report generation failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Report generation error: {str(e)}"}
    
    async def detect_anomalies(self,
                             data: List[Dict[str, Any]],
                             threshold: float = 0.95) -> Dict[str, Any]:
        """Detect anomalies in data"""
        try:
            if not self.api_key:
                return {"error": "Lumen API key not configured"}
            
            url = f"{self.base_url}/anomalies/detect"
            
            payload = {
                "data": data,
                "threshold": threshold
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "anomalies": result.get("anomalies", []),
                            "anomaly_score": result.get("anomaly_score", 0),
                            "confidence": result.get("confidence", 0),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Anomaly detection failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Anomaly detection error: {str(e)}"}
    
    async def predict_trends(self,
                           historical_data: List[Dict[str, Any]],
                           forecast_periods: int = 12,
                           confidence_level: float = 0.95) -> Dict[str, Any]:
        """Predict future trends based on historical data"""
        try:
            if not self.api_key:
                return {"error": "Lumen API key not configured"}
            
            url = f"{self.base_url}/predict/trends"
            
            payload = {
                "historical_data": historical_data,
                "forecast_periods": forecast_periods,
                "confidence_level": confidence_level
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "forecast": result.get("forecast", []),
                            "confidence_intervals": result.get("confidence_intervals", []),
                            "trend_direction": result.get("trend_direction", ""),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Trend prediction failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Trend prediction error: {str(e)}"}
    
    async def segment_data(self,
                          data: List[Dict[str, Any]],
                          segment_count: int = 5,
                          algorithm: str = "kmeans") -> Dict[str, Any]:
        """Segment data into clusters"""
        try:
            if not self.api_key:
                return {"error": "Lumen API key not configured"}
            
            url = f"{self.base_url}/segment"
            
            payload = {
                "data": data,
                "segment_count": segment_count,
                "algorithm": algorithm
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "segments": result.get("segments", []),
                            "segment_characteristics": result.get("segment_characteristics", {}),
                            "segment_sizes": result.get("segment_sizes", {}),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Data segmentation failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Data segmentation error: {str(e)}"}
    
    async def get_insights(self,
                          data: List[Dict[str, Any]],
                          insight_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get specific types of insights from data"""
        try:
            if not self.api_key:
                return {"error": "Lumen API key not configured"}
            
            url = f"{self.base_url}/insights"
            
            payload = {
                "data": data
            }
            
            if insight_types:
                payload["insight_types"] = insight_types
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "insights": result.get("insights", []),
                            "insight_categories": result.get("insight_categories", {}),
                            "confidence_scores": result.get("confidence_scores", {}),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Insight generation failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Insight generation error: {str(e)}"}
    
    async def create_dashboard(self,
                             data: List[Dict[str, Any]],
                             dashboard_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a custom dashboard"""
        try:
            if not self.api_key:
                return {"error": "Lumen API key not configured"}
            
            url = f"{self.base_url}/dashboards/create"
            
            payload = {
                "data": data,
                "config": dashboard_config
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "dashboard_id": result.get("dashboard_id"),
                            "dashboard_url": result.get("dashboard_url"),
                            "widgets": result.get("widgets", []),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Dashboard creation failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Dashboard creation error: {str(e)}"}
    
    async def get_available_models(self) -> Dict[str, Any]:
        """Get available analysis models"""
        try:
            if not self.api_key:
                return {"error": "Lumen API key not configured"}
            
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