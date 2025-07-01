# LLM-Routed Query System (with LangChain)

A backend system that routes incoming user queries to the most appropriate LLM (like Claude, ChatGPT, or Gemini) — automatically chosen by a powerful router LLM like GPT-4o. This project is built using **LangChain** for standardized and clean LLM interactions.

## Features
- **Dynamic Routing**: Uses GPT-4o via LangChain for intelligent, context-aware routing.
- **LangChain Core**: Leverages LangChain for all LLM calls, providing a unified and extensible interface.
- **Asynchronous**: Built with FastAPI and `async` for high performance.
- **Layered Architecture**: Clean, maintainable, and testable code structure.
- **REST API-Ready**: Exposes a simple and robust `/query` endpoint.
- **Dockerized**: Includes a production-ready Dockerfile.

## Getting Started

### Prerequisites
- Python 3.10+
- API keys for OpenAI, Anthropic, and Google AI

### Running Locally

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd ALLinONE
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure API Keys:**
    - Create a `.env` file from the sample:
      ```bash
      cp .env.sample .env
      ```
    - Open the `.env` file and add your actual API keys.

5.  **Run the application:**
    ```bash
    uvicorn src.app:app --reload
    ```
    The server will start on `http://127.0.0.1:8000`.

### API Usage

Access the auto-generated documentation at **http://127.0.0.1:8000/docs**.

#### Example Request
Send a `POST` request to `http://127.0.0.1:8000/api/v1/query`.

Using `curl`:
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/query' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "Give me a three-point summary of the key differences between quantum computing and classical computing."
}'