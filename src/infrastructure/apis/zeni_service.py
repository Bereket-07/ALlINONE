import asyncio
import aiohttp
import json
import base64
from typing import Optional, Dict, Any, List
from src.config import ZENI_API_KEY, ZENI_BASE_URL

class ZeniService:
    """Service for Zeni AI-powered financial analysis"""
    
    def __init__(self):
        self.api_key = ZENI_API_KEY
        self.base_url = ZENI_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def analyze_financial_data(self, 
                                   financial_data: List[Dict[str, Any]],
                                   analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Analyze financial data and generate insights"""
        try:
            if not self.api_key:
                return {"error": "Zeni API key not configured"}
            
            url = f"{self.base_url}/analyze/financial"
            
            payload = {
                "financial_data": financial_data,
                "analysis_type": analysis_type
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "financial_insights": result.get("insights", []),
                            "key_metrics": result.get("key_metrics", {}),
                            "risk_assessment": result.get("risk_assessment", {}),
                            "recommendations": result.get("recommendations", []),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Financial analysis failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Financial analysis error: {str(e)}"}
    
    async def generate_financial_report(self,
                                      data: List[Dict[str, Any]],
                                      report_type: str = "quarterly",
                                      format: str = "pdf") -> Dict[str, Any]:
        """Generate comprehensive financial report"""
        try:
            if not self.api_key:
                return {"error": "Zeni API key not configured"}
            
            url = f"{self.base_url}/reports/financial"
            
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
                            "financial_summary": result.get("summary", {}),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Financial report generation failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Financial report generation error: {str(e)}"}
    
    async def predict_financial_metrics(self,
                                      historical_data: List[Dict[str, Any]],
                                      target_metrics: List[str],
                                      forecast_periods: int = 12) -> Dict[str, Any]:
        """Predict financial metrics and trends"""
        try:
            if not self.api_key:
                return {"error": "Zeni API key not configured"}
            
            url = f"{self.base_url}/predict/financial"
            
            payload = {
                "historical_data": historical_data,
                "target_metrics": target_metrics,
                "forecast_periods": forecast_periods
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "predictions": result.get("predictions", {}),
                            "confidence_intervals": result.get("confidence_intervals", {}),
                            "accuracy_metrics": result.get("accuracy_metrics", {}),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Financial prediction failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Financial prediction error: {str(e)}"}
    
    async def assess_financial_risk(self,
                                  financial_data: List[Dict[str, Any]],
                                  risk_factors: Optional[List[str]] = None) -> Dict[str, Any]:
        """Assess financial risk and provide risk scores"""
        try:
            if not self.api_key:
                return {"error": "Zeni API key not configured"}
            
            url = f"{self.base_url}/risk/assess"
            
            payload = {
                "financial_data": financial_data
            }
            
            if risk_factors:
                payload["risk_factors"] = risk_factors
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "risk_scores": result.get("risk_scores", {}),
                            "risk_factors": result.get("risk_factors", []),
                            "mitigation_strategies": result.get("mitigation_strategies", []),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Risk assessment failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Risk assessment error: {str(e)}"}
    
    async def optimize_investment_portfolio(self,
                                          portfolio_data: List[Dict[str, Any]],
                                          optimization_goal: str = "maximize_returns") -> Dict[str, Any]:
        """Optimize investment portfolio"""
        try:
            if not self.api_key:
                return {"error": "Zeni API key not configured"}
            
            url = f"{self.base_url}/portfolio/optimize"
            
            payload = {
                "portfolio_data": portfolio_data,
                "optimization_goal": optimization_goal
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "optimized_allocation": result.get("allocation", {}),
                            "expected_returns": result.get("expected_returns", {}),
                            "risk_adjustments": result.get("risk_adjustments", {}),
                            "rebalancing_recommendations": result.get("rebalancing", []),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Portfolio optimization failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Portfolio optimization error: {str(e)}"}
    
    async def analyze_market_trends(self,
                                  market_data: List[Dict[str, Any]],
                                  sectors: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analyze market trends and sector performance"""
        try:
            if not self.api_key:
                return {"error": "Zeni API key not configured"}
            
            url = f"{self.base_url}/market/trends"
            
            payload = {
                "market_data": market_data
            }
            
            if sectors:
                payload["sectors"] = sectors
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "market_trends": result.get("trends", []),
                            "sector_performance": result.get("sector_performance", {}),
                            "market_indicators": result.get("indicators", {}),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Market trend analysis failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Market trend analysis error: {str(e)}"}
    
    async def detect_financial_anomalies(self,
                                       financial_data: List[Dict[str, Any]],
                                       sensitivity: float = 0.8) -> Dict[str, Any]:
        """Detect financial anomalies and unusual patterns"""
        try:
            if not self.api_key:
                return {"error": "Zeni API key not configured"}
            
            url = f"{self.base_url}/anomalies/financial"
            
            payload = {
                "financial_data": financial_data,
                "sensitivity": sensitivity
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "anomalies": result.get("anomalies", []),
                            "anomaly_scores": result.get("scores", {}),
                            "impact_assessment": result.get("impact", {}),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Financial anomaly detection failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Financial anomaly detection error: {str(e)}"}
    
    async def create_financial_dashboard(self,
                                       data: List[Dict[str, Any]],
                                       dashboard_type: str = "executive") -> Dict[str, Any]:
        """Create interactive financial dashboard"""
        try:
            if not self.api_key:
                return {"error": "Zeni API key not configured"}
            
            url = f"{self.base_url}/dashboards/financial"
            
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
                            "financial_widgets": result.get("widgets", []),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Financial dashboard creation failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Financial dashboard creation error: {str(e)}"}
    
    async def get_financial_insights(self,
                                   data: List[Dict[str, Any]],
                                   insight_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get specific financial insights"""
        try:
            if not self.api_key:
                return {"error": "Zeni API key not configured"}
            
            url = f"{self.base_url}/insights/financial"
            
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
                            "financial_insights": result.get("insights", []),
                            "action_items": result.get("action_items", []),
                            "priority_rankings": result.get("priorities", {}),
                            "status": "success"
                        }
                    else:
                        error_text = await response.text()
                        return {"error": f"Financial insights failed: {response.status} - {error_text}"}
                        
        except Exception as e:
            return {"error": f"Financial insights error: {str(e)}"} 