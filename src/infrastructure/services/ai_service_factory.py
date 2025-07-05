from typing import Dict, Any, Optional
from src.infrastructure.apis.assembly_ai_service import AssemblyAIService
from src.infrastructure.apis.stability_ai_service import StabilityAIService
from src.infrastructure.apis.eleven_labs_service import ElevenLabsService
from src.infrastructure.apis.google_vision_service import GoogleVisionService
from src.infrastructure.apis.tavus_service import TavusService
from src.infrastructure.apis.clarifai_service import ClarifaiService
from src.infrastructure.apis.peltarion_service import PeltarionService
from src.infrastructure.apis.synthesis_ai_service import SynthesisAIService
from src.infrastructure.apis.lumen_service import LumenService
from src.infrastructure.apis.imagga_service import ImaggaService
from src.infrastructure.apis.kentosh_service import KentoshService
from src.infrastructure.apis.zeni_service import ZeniService

class AIServiceFactory:
    """Factory for managing all AI API services"""
    
    def __init__(self):
        self._services = {}
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize all AI services"""
        self._services = {
            "assembly_ai": AssemblyAIService(),
            "stability_ai": StabilityAIService(),
            "eleven_labs": ElevenLabsService(),
            "google_vision": GoogleVisionService(),
            "tavus": TavusService(),
            "clarifai": ClarifaiService(),
            "peltarion": PeltarionService(),
            "synthesis_ai": SynthesisAIService(),
            "lumen": LumenService(),
            "imagga": ImaggaService(),
            "kentosh": KentoshService(),
            "zeni": ZeniService()
        }
    
    def get_service(self, service_name: str) -> Optional[Any]:
        """Get a specific AI service by name"""
        return self._services.get(service_name.lower())
    
    def get_all_services(self) -> Dict[str, Any]:
        """Get all available AI services"""
        return self._services.copy()
    
    def get_available_services(self) -> Dict[str, bool]:
        """Get status of all services (whether they have API keys configured)"""
        available = {}
        for name, service in self._services.items():
            # Check if service has API key configured
            has_key = hasattr(service, 'api_key') and service.api_key is not None
            available[name] = has_key
        return available
    
    def get_service_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all services"""
        info = {}
        for name, service in self._services.items():
            info[name] = {
                "class_name": service.__class__.__name__,
                "description": service.__class__.__doc__ or "AI Service",
                "has_api_key": hasattr(service, 'api_key') and service.api_key is not None
            }
        return info
    
    # Convenience methods for specific service types
    def get_audio_services(self) -> Dict[str, Any]:
        """Get audio-related services"""
        return {
            "assembly_ai": self._services["assembly_ai"],
            "eleven_labs": self._services["eleven_labs"]
        }
    
    def get_image_services(self) -> Dict[str, Any]:
        """Get image-related services"""
        return {
            "stability_ai": self._services["stability_ai"],
            "google_vision": self._services["google_vision"],
            "clarifai": self._services["clarifai"],
            "imagga": self._services["imagga"]
        }
    
    def get_video_services(self) -> Dict[str, Any]:
        """Get video-related services"""
        return {
            "tavus": self._services["tavus"]
        }
    
    def get_ml_services(self) -> Dict[str, Any]:
        """Get machine learning services"""
        return {
            "peltarion": self._services["peltarion"],
            "synthesis_ai": self._services["synthesis_ai"]
        }
    
    def get_analytics_services(self) -> Dict[str, Any]:
        """Get analytics and business intelligence services"""
        return {
            "lumen": self._services["lumen"],
            "kentosh": self._services["kentosh"],
            "zeni": self._services["zeni"]
        }
    
    async def health_check(self) -> Dict[str, Dict[str, Any]]:
        """Perform health check on all services"""
        health_status = {}
        
        for name, service in self._services.items():
            try:
                # Try to get models or basic info to test connectivity
                if hasattr(service, 'get_models'):
                    result = await service.get_models()
                    health_status[name] = {
                        "status": "healthy" if "error" not in result else "error",
                        "error": result.get("error") if "error" in result else None
                    }
                elif hasattr(service, 'get_available_models'):
                    result = await service.get_available_models()
                    health_status[name] = {
                        "status": "healthy" if "error" not in result else "error",
                        "error": result.get("error") if "error" in result else None
                    }
                else:
                    # For services without get_models method, just check if API key is configured
                    has_key = hasattr(service, 'api_key') and service.api_key is not None
                    health_status[name] = {
                        "status": "configured" if has_key else "no_api_key",
                        "error": None if has_key else "API key not configured"
                    }
            except Exception as e:
                health_status[name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return health_status

# Global instance
ai_service_factory = AIServiceFactory() 