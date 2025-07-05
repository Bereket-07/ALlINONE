import asyncio
import aiohttp
import json
import base64
from typing import Optional, Dict, Any, List
from src.config import KENTOSH_API_KEY, KENTOSH_BASE_URL

class KentoshService:
    """Service for Kentosh AI-powered business intelligence"""
    
    def __init__(self):
        self.api_key = KENTOSH_API_KEY
        self.base_url = KENTOSH_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def analyze_business_data(self, 
                                  data: List[Dict[str, Any]],
                                  analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Analyze business data and generate insights"""
        try:
            if not self.api_key:
                return {"error": "Kentosh API key not configured"}
            
            url = f"{self.base_url}/analyze/business"
            
            payload = {
                "data": data,
                "analysis_type": analysis_type
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "insights": result.get("insights", []),
                            "metrics": result.get("metrics", {}),
                            "recommendations": result.get("recommendations", []),
                            "trends": result.get("trends", []),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Business analysis failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Business analysis error: {str(e)}"}
    
    async def generate_business_report(self,
                                     data: List[Dict[str, Any]],
                                     report_type: str = "executive",
                                     format: str = "pdf") -> Dict[str, Any]:
        """Generate business intelligence report"""
        try:
            if not self.api_key:
                return {"error": "Kentosh API key not configured"}
            
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
                            "report_url": result.get("report_url"),
                            "report_id": result.get("report_id"),
                            "summary": result.get("summary", {}),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Report generation failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Report generation error: {str(e)}"}
    
    async def predict_business_metrics(self,
                                     historical_data: List[Dict[str, Any]],
                                     target_metric: str,
                                     forecast_periods: int = 12) -> Dict[str, Any]:
        """Predict business metrics"""
        try:
            if not self.api_key:
                return {"error": "Kentosh API key not configured"}
            
            url = f"{self.base_url}/predict/metrics"
            
            payload = {
                "historical_data": historical_data,
                "target_metric": target_metric,
                "forecast_periods": forecast_periods
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "predictions": result.get("predictions", []),
                            "confidence_intervals": result.get("confidence_intervals", []),
                            "accuracy_score": result.get("accuracy_score", 0),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Metric prediction failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Metric prediction error: {str(e)}"}
    
    async def detect_business_anomalies(self,
                                      data: List[Dict[str, Any]],
                                      sensitivity: float = 0.8) -> Dict[str, Any]:
        """Detect business anomalies and outliers"""
        try:
            if not self.api_key:
                return {"error": "Kentosh API key not configured"}
            
            url = f"{self.base_url}/anomalies/detect"
            
            payload = {
                "data": data,
                "sensitivity": sensitivity
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "anomalies": result.get("anomalies", []),
                            "anomaly_score": result.get("anomaly_score", 0),
                            "severity_levels": result.get("severity_levels", {}),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Anomaly detection failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Anomaly detection error: {str(e)}"}
    
    async def segment_customers(self,
                              customer_data: List[Dict[str, Any]],
                              segment_count: int = 5) -> Dict[str, Any]:
        """Segment customers based on behavior and characteristics"""
        try:
            if not self.api_key:
                return {"error": "Kentosh API key not configured"}
            
            url = f"{self.base_url}/customers/segment"
            
            payload = {
                "customer_data": customer_data,
                "segment_count": segment_count
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "segments": result.get("segments", []),
                            "segment_profiles": result.get("segment_profiles", {}),
                            "segment_sizes": result.get("segment_sizes", {}),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Customer segmentation failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Customer segmentation error: {str(e)}"}
    
    async def analyze_competition(self,
                                market_data: List[Dict[str, Any]],
                                competitors: List[str]) -> Dict[str, Any]:
        """Analyze competitive landscape"""
        try:
            if not self.api_key:
                return {"error": "Kentosh API key not configured"}
            
            url = f"{self.base_url}/competition/analyze"
            
            payload = {
                "market_data": market_data,
                "competitors": competitors
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "competitive_analysis": result.get("competitive_analysis", {}),
                            "market_position": result.get("market_position", {}),
                            "opportunities": result.get("opportunities", []),
                            "threats": result.get("threats", []),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Competitive analysis failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Competitive analysis error: {str(e)}"}
    
    async def optimize_business_processes(self,
                                        process_data: List[Dict[str, Any]],
                                        optimization_goal: str) -> Dict[str, Any]:
        """Optimize business processes"""
        try:
            if not self.api_key:
                return {"error": "Kentosh API key not configured"}
            
            url = f"{self.base_url}/processes/optimize"
            
            payload = {
                "process_data": process_data,
                "optimization_goal": optimization_goal
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "optimization_recommendations": result.get("recommendations", []),
                            "efficiency_gains": result.get("efficiency_gains", {}),
                            "cost_savings": result.get("cost_savings", {}),
                            "implementation_plan": result.get("implementation_plan", {}),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Process optimization failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Process optimization error: {str(e)}"}
    
    async def create_business_dashboard(self,
                                      data: List[Dict[str, Any]],
                                      dashboard_type: str = "executive") -> Dict[str, Any]:
        """Create interactive business dashboard"""
        try:
            if not self.api_key:
                return {"error": "Kentosh API key not configured"}
            
            url = f"{self.base_url}/dashboards/create"
            
            payload = {
                "data": data,
                "dashboard_type": dashboard_type
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
    
    async def get_business_insights(self,
                                  data: List[Dict[str, Any]],
                                  insight_categories: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get specific business insights"""
        try:
            if not self.api_key:
                return {"error": "Kentosh API key not configured"}
            
            url = f"{self.base_url}/insights/business"
            
            payload = {
                "data": data
            }
            
            if insight_categories:
                payload["insight_categories"] = insight_categories
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "insights": result.get("insights", []),
                            "action_items": result.get("action_items", []),
                            "priority_scores": result.get("priority_scores", {}),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Business insights failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Business insights error: {str(e)}"} 