# LLM-Routed Query System (with LangChain & JWT Authentication)

A backend system that routes incoming user queries to the most appropriate LLM (like Claude, ChatGPT, or Gemini) — automatically chosen by a powerful router LLM
like GPT-4o. This project is built using **LangChain** for standardized and clean LLM interactions, with **custom JWT authentication** for secure user
management.

## Features

-   **Dynamic Routing**: Uses GPT-4o via LangChain for intelligent, context-aware routing.
-   **LangChain Core**: Leverages LangChain for all LLM calls, providing a unified and extensible interface.
-   **JWT Authentication**: Custom authentication system with secure password hashing and token management.
-   **Asynchronous**: Built with FastAPI and `async` for high performance.
-   **Layered Architecture**: Clean, maintainable, and testable code structure.
-   **REST API-Ready**: Exposes simple and robust endpoints for queries and authentication.
-   **Protected Routes**: Secure endpoints with JWT token validation.
-   **Dockerized**: Includes a production-ready Dockerfile.

## Authentication System

The application includes a complete JWT-based authentication system:

### Endpoints

-   `POST /api/v1/auth/register` - Register a new user
-   `POST /api/v1/auth/login` - Login with email and password
-   `GET /api/v1/auth/profile` - Get current user profile (protected)
-   `POST /api/v1/auth/refresh-token` - Refresh access token

### Security Features

-   Password hashing with bcrypt
-   JWT tokens with configurable expiration
-   Separate access and refresh tokens
-   Protected routes with middleware
-   Token validation and verification

## Getting Started

### Prerequisites

-   Python 3.10+
-   API keys for OpenAI, Anthropic, and Google AI

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

4.  **Configure Environment Variables:** Create a `.env` file with the following variables:

    ```env
    # JWT Configuration
    JWT_SECRET=your-super-secret-jwt-key-change-in-production

    # LLM API Keys
    OPENAI_API_KEY=your-openai-api-key
    GOOGLE_API_KEY=your-google-api-key
    ANTHROPIC_API_KEY=your-anthropic-api-key
    ```

5.  **Run the application:**
    ```bash
    uvicorn src.app:app --reload
    ```
    The server will start on `http://127.0.0.1:8000`.

### API Usage

Access the auto-generated documentation at **http://127.0.0.1:8000/docs**.

#### Authentication Flow

1. **Register a new user:**

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "display_name": "John Doe"
  }'
```

2. **Login:**

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

3. **Use protected query endpoint:**

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/query" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Give me a three-point summary of the key differences between quantum computing and classical computing."
  }'
```

#### Example Query Request (Protected)

Send a `POST` request to `http://127.0.0.1:8000/api/v1/query` with your JWT token in the Authorization header.

Using `curl`:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/query' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "Give me a three-point summary of the key differences between quantum computing and classical computing."
}'
```

## Documentation

-   **JWT Authentication Setup**: See `JWT_AUTH_SETUP_GUIDE.md` for detailed authentication setup and usage instructions.
-   **API Documentation**: Available at `http://127.0.0.1:8000/docs` when the server is running.

## Security Notes

-   **JWT Secret**: Change the default JWT secret in production
-   **Token Expiration**: Access tokens expire in 30 minutes, refresh tokens in 30 days
-   **Password Security**: Passwords are automatically hashed with bcrypt
-   **HTTPS**: Use HTTPS in production environments
-   **Database**: Current implementation uses in-memory storage; implement database storage for production
