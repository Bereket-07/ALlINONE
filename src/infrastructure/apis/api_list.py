from infrastructure.apis.copy_ai import CopyAIClient
from infrastructure.apis.eleven_labs import ElevenLabsClient
from infrastructure.apis.hootsuite import HootsuiteClient
from infrastructure.apis.powerBi import PowerBIClient
from infrastructure.apis.runway import RunwayClient
from infrastructure.apis.similar_webs import SimilarWebClient
from infrastructure.apis.slide_speak import SlideSpeakClient
from infrastructure.apis.stability import StabilityAIClient

API_REGISTRY = {
    'copyai': CopyAIClient(),
    'elevenlabs': ElevenLabsClient(),
    'hootsuite': HootsuiteClient(),
    'powerbi': PowerBIClient(),
    'runway': RunwayClient(),
    'similarweb': SimilarWebClient(),
    'slidespeak': SlideSpeakClient(),
    'stability': StabilityAIClient()
}