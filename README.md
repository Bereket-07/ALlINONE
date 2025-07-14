# LLM Router with AI Services Integration

A comprehensive AI platform that automatically routes user queries to the most suitable Language Model (LLM) and provides access to a wide range of AI services through LangChain tools integration.

## Features

### 🤖 LLM Routing
- **Intelligent Query Routing**: Automatically selects the best LLM (OpenAI GPT, Claude, Gemini) based on query content
- **LangChain Integration**: Built on LangChain for robust LLM orchestration
- **Real-time Analysis**: Analyzes query intent and complexity for optimal routing
- **Document Analysis**: Upload PDF files for intelligent content extraction, analysis, and question-answering

### 🎯 AI Services Integration
The platform integrates with 12+ leading AI services:

#### Audio Processing
- **Assembly AI**: Speech-to-text transcription, real-time audio processing, sentiment analysis
- **Eleven Labs**: High-quality text-to-speech, voice cloning, voice management

#### Image Generation & Analysis
- **Stability AI**: AI image generation, upscaling, image-to-image transformation
- **Google Vision**: Comprehensive image analysis, OCR, object detection, face detection
- **Clarifai**: Image recognition, concept detection, custom model predictions
- **Imagga**: Image tagging, categorization, color detection, complete image analysis

#### Video Services
- **Tavus**: AI-powered video personalization, template-based video generation

#### Machine Learning
- **Peltarion Platform**: Custom ML model deployment, predictions, model management
- **Synthesis AI**: Synthetic data generation, custom model training

#### Business Intelligence & Analytics
- **Lumen**: AI-powered data analytics, insights generation, trend prediction
- **Kentosh**: Business intelligence, customer segmentation, competitive analysis
- **Zeni**: Financial analysis, risk assessment, investment portfolio optimization

### 🔧 LangChain Tools Integration
All AI services are available as LangChain tools, enabling:
- **Seamless Integration**: Use AI services directly within LLM conversations
- **Tool Selection**: Automatic tool selection based on query content
- **Multi-tool Operations**: Combine multiple AI services in a single workflow
- **Agent-based Execution**: LLMs can use tools to enhance their capabilities

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Query    │───▶│  Query Router    │───▶│  Best LLM       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  Tool Selector   │    │  LangChain      │
                       └──────────────────┘    │  Agent          │
                                │              └─────────────────┘
                                ▼                        │
                       ┌──────────────────┐              │
                       │  AI Services     │◀─────────────┘
                       │  (12+ APIs)      │
                       └──────────────────┘
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ALlINONE
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file with your API keys:
   ```env
   # Core LLM APIs
   OPENAI_API_KEY=your_openai_key
   GOOGLE_API_KEY=your_google_key
   ANTHROPIC_API_KEY=your_anthropic_key
   
   # AI Services APIs
   ASSEMBLY_AI_API_KEY=your_assembly_ai_key
   STABILITY_AI_API_KEY=your_stability_ai_key
   ELEVEN_LABS_API_KEY=your_eleven_labs_key
   GOOGLE_VISION_API_KEY=your_google_vision_key
   GOOGLE_TRANSLATE_API_KEY=your_google_translate_key
   TAVUS_API_KEY=your_tavus_key
   CLARIFAI_API_KEY=your_clarifai_key
   PELTARION_API_KEY=your_peltarion_key
   SYNTHESIS_AI_API_KEY=your_synthesis_ai_key
   LUMEN_API_KEY=your_lumen_key
   IMAGGA_API_KEY=your_imagga_key
   KENTOSH_API_KEY=your_kentosh_key
   ZENI_API_KEY=your_zeni_key
   
   # Additional Third-party APIs
   COPY_AI_API_KEY=your_copy_ai_api_key
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   HOOTSUITE_ACCESS_TOKEN=your_hootsuite_access_token
   POWERBI_ACCESS_TOKEN=your_powerbi_access_token
   SLIDESPEAK_API_KEY=your_slidespeak_api_key
   SIMILARWEB_API_KEY=your_similarweb_api_key
   RUNWAY_API_KEY=your_runway_api_key
   
   # JWT and Firebase
   JWT_SECRET=your_jwt_secret
   FIREBASE_CREDENTIALS_PATH=path/to/firebase_credentials.json
   ```

4. **Run the application**
   ```bash
   uvicorn src.app:app --reload
   ```

## API Endpoints

### Core LLM Routing
- `POST /api/v1/query` - Unified endpoint that accepts text queries and/or file uploads (PDF)
  - **Text only**: Regular query processing
  - **Files only**: Automatic comprehensive document insights
  - **Text + Files**: Query-specific document analysis

### AI Services Health & Status
- `GET /ai/health` - Check health of all AI services
- `GET /ai/services` - Get information about available services
- `GET /ai/tools` - Get available LangChain tools
- `POST /ai/tools/test` - Test tool integration

### Audio Services
- `POST /ai/audio/transcribe` - Transcribe audio using Assembly AI
- `POST /ai/audio/tts` - Convert text to speech using Eleven Labs
- `GET /ai/audio/voices` - Get available voices

### Image Services
- `POST /ai/image/generate` - Generate images using Stability AI
- `POST /ai/image/analyze` - Analyze images using multiple services
- `POST /ai/image/upscale` - Upscale images using Stability AI

### Video Services
- `POST /ai/video/create` - Create personalized videos using Tavus

### Machine Learning
- `POST /ai/ml/predict` - Make predictions using Peltarion models
- `POST /ai/ml/generate-data` - Generate synthetic data using Synthesis AI

### Analytics Services
- `POST /ai/analytics/analyze` - Analyze data using Lumen, Kentosh, or Zeni

### Service Management
- `GET /ai/services/{service_name}/models` - Get models for specific service
- `POST /ai/batch/process` - Process multiple operations in batch

## Usage Examples

### Text-Only Query
```python
import requests

# Regular text query (form data)
response = requests.post("http://localhost:8000/api/v1/query", 
    data={"query": "Generate an image of a beautiful sunset"},
    headers={"Authorization": "Bearer your_jwt_token"}
)

print(response.json())
# Output: {"llm_used": "chatgpt", "response": "...", "file_processed": null}
```

### File-Only Analysis (Auto Insights)
```python
import requests

# Upload PDF without query - generates comprehensive insights automatically
with open("document.pdf", "rb") as f:
    response = requests.post("http://localhost:8000/api/v1/query",
        files={"files": f},
        headers={"Authorization": "Bearer your_jwt_token"}
    )

print(response.json())
# Output: {"llm_used": "chatgpt", "response": "Comprehensive document analysis...", "file_processed": {"filename": "document.pdf", ...}}
```

### Query with PDF File Analysis
```python
import requests

# Upload PDF with specific question
with open("document.pdf", "rb") as f:
    response = requests.post("http://localhost:8000/api/v1/query",
        files={"files": f},
        data={"query": "What are the main conclusions of this research paper?"},
        headers={"Authorization": "Bearer your_jwt_token"}
    )

print(response.json())
# Output: {"llm_used": "chatgpt", "response": "...", "file_processed": {"filename": "document.pdf", ...}}

# Upload multiple PDFs (only first one processed currently)
with open("report1.pdf", "rb") as f1, open("report2.pdf", "rb") as f2:
    response = requests.post("http://localhost:8000/api/v1/query",
        files=[("files", f1), ("files", f2)],
        data={"query": "Compare these documents"},
        headers={"Authorization": "Bearer your_jwt_token"}
    )
```

### Direct AI Service Usage
```python
# Transcribe audio
with open("audio.mp3", "rb") as f:
    response = requests.post("http://localhost:8000/ai/audio/transcribe",
        files={"file": f},
        data={"language_code": "en"},
        headers={"Authorization": "Bearer your_jwt_token"}
    )

# Generate image
response = requests.post("http://localhost:8000/ai/image/generate",
    data={
        "prompt": "A beautiful sunset over mountains",
        "width": 1024,
        "height": 1024
    },
    headers={"Authorization": "Bearer your_jwt_token"}
)
```

### LangChain Integration
The platform automatically integrates AI services as LangChain tools:

```python
# When a user asks: "Generate an image of a cat and then analyze it"
# The system will:
# 1. Route to appropriate LLM
# 2. Select tools: ["stability_ai_generate_image", "google_vision_analyze"]
# 3. Execute: Generate image → Analyze the generated image
# 4. Return comprehensive response
```

## Service Categories

### Audio Processing
- **Assembly AI**: Real-time transcription, speaker detection, sentiment analysis
- **Eleven Labs**: Natural-sounding TTS, voice cloning, voice management

### Image & Vision
- **Stability AI**: Text-to-image generation, upscaling, style transfer
- **Google Vision**: OCR, object detection, face analysis, safe search
- **Clarifai**: Custom image recognition, concept detection
- **Imagga**: Image tagging, categorization, color analysis

### Video & Media
- **Tavus**: Personalized video generation, template management

### Machine Learning
- **Peltarion**: Custom ML model deployment, batch predictions
- **Synthesis AI**: Synthetic data generation, custom model training

### Business Intelligence
- **Lumen**: Data analytics, trend prediction, anomaly detection
- **Kentosh**: Business analysis, customer segmentation, competitive intelligence
- **Zeni**: Financial analysis, risk assessment, portfolio optimization

## Configuration

### Service Configuration
Each service can be configured independently. Services without API keys will be marked as unavailable but won't break the system.

### Tool Selection
The system automatically selects appropriate tools based on query content:
- **Audio queries**: Assembly AI, Eleven Labs
- **Image queries**: Stability AI, Google Vision, Clarifai, Imagga
- **Video queries**: Tavus
- **Data analysis**: Lumen, Kentosh, Zeni
- **ML operations**: Peltarion, Synthesis AI

## Development

### Adding New Services
1. Create service class in `src/infrastructure/apis/`
2. Add configuration in `src/config.py`
3. Create LangChain tool in `src/infrastructure/llm/ai_tools.py`
4. Add to service factory in `src/infrastructure/services/ai_service_factory.py`
5. Add API endpoints in `src/controllers/ai_controller.py`

### Testing
```bash
# Test tool integration
curl -X POST "http://localhost:8000/ai/tools/test" \
  -H "Authorization: Bearer your_jwt_token"

# Test service health
curl -X GET "http://localhost:8000/ai/health" \
  -H "Authorization: Bearer your_jwt_token"
```

## Security

- **JWT Authentication**: All endpoints require valid JWT tokens
- **API Key Management**: Secure storage of service API keys
- **Input Validation**: Comprehensive validation for all inputs
- **Error Handling**: Graceful error handling without exposing sensitive information

## Performance

- **Async Operations**: All AI service calls are asynchronous
- **Connection Pooling**: Efficient HTTP connection management
- **Caching**: Optional caching for frequently used operations
- **Batch Processing**: Support for batch operations to improve efficiency

## Monitoring

- **Health Checks**: Comprehensive health monitoring for all services
- **Usage Statistics**: Track API usage and performance metrics
- **Error Logging**: Detailed error logging for debugging
- **Service Status**: Real-time status monitoring of all AI services

## License

[Your License Here]

## Support

For support and questions, please open an issue in the repository or contact the development team.