# Simple Authentication System

A streamlined authentication system with Firebase Authentication that provides user registration, login, and profile retrieval functionality.

## 🎯 Features

-   ✅ **User Registration** - Create new user accounts
-   ✅ **User Login** - Authenticate users and get tokens
-   ✅ **Get Profile** - Retrieve user profile information
-   ✅ **Token Verification** - Secure authentication with Firebase ID tokens

## 🏗️ Architecture

The system follows a simplified Clean Architecture:

```
src/
├── domain/models/
│   └── auth_models.py          # Authentication data models
├── use_cases/
│   └── auth_use_cases.py       # Authentication business logic (merged with Firebase service)
├── controllers/
│   └── auth_controller.py      # Authentication endpoints
├── infrastructure/
│   └── firebase/
│       ├── firebase_config.py  # Firebase configuration
│       └── __init__.py
└── app.py                      # Main application
```

## 📋 API Endpoints

### 1. Register User

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "display_name": "John Doe"
}
```

**Response:**

```json
{
	"user": {
		"uid": "firebase_user_uid",
		"email": "user@example.com",
		"display_name": "John Doe",
		"email_verified": false,
		"created_at": "2024-01-01T00:00:00",
		"last_sign_in": null
	},
	"token": "",
	"refresh_token": null
}
```

### 2. Login User

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**

```json
{
	"user": {
		"uid": "firebase_user_uid",
		"email": "user@example.com",
		"display_name": "John Doe",
		"email_verified": false,
		"created_at": "2024-01-01T00:00:00",
		"last_sign_in": "2024-01-01T12:00:00"
	},
	"token": "firebase_id_token",
	"refresh_token": "firebase_refresh_token"
}
```

### 3. Get User Profile

```http
GET /api/v1/auth/profile
Authorization: Bearer <firebase_id_token>
```

**Response:**

```json
{
	"uid": "firebase_user_uid",
	"email": "user@example.com",
	"display_name": "John Doe",
	"email_verified": false,
	"created_at": "2024-01-01T00:00:00",
	"last_sign_in": "2024-01-01T12:00:00"
}
```

## 🔧 Setup

### Environment Variables

```bash
FIREBASE_CREDENTIALS_PATH=all-in-one-ai-464811-firebase-adminsdk-fbsvc-75931db9e6.json
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
ANTHROPIC_API_KEY=your_anthropic_key
```

### Dependencies

```bash
pip install firebase-admin email-validator
```

## 🚀 Usage Examples

### Using cURL

#### Register a new user:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "display_name": "Test User"
  }'
```

#### Login:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

#### Get profile (requires token):

```bash
curl -X GET "http://localhost:8000/api/v1/auth/profile" \
  -H "Authorization: Bearer <your_firebase_id_token>"
```

### Using Python Requests

```python
import requests

# Register
response = requests.post("http://localhost:8000/api/v1/auth/register", json={
    "email": "test@example.com",
    "password": "password123",
    "display_name": "Test User"
})
print(response.json())

# Login
response = requests.post("http://localhost:8000/api/v1/auth/login", json={
    "email": "test@example.com",
    "password": "password123"
})
data = response.json()
token = data["token"]

# Get profile
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:8000/api/v1/auth/profile", headers=headers)
print(response.json())
```

## 🔐 Authentication Flow

1. **Registration**: User creates account → Returns user data (no tokens)
2. **Login**: User authenticates → Returns user data + tokens
3. **Profile Access**: Use token in Authorization header → Returns user profile

## 🛡️ Security

-   Firebase ID token verification
-   Bearer token authentication
-   Input validation with Pydantic
-   Email format validation
-   Password strength requirements (min 6 characters)

## 🏃‍♂️ Running the Application

```bash
# Start the server
uvicorn src.app:app --reload

# Access API documentation
# http://localhost:8000/docs
```

## 📝 Notes

-   **Login Implementation**: The current login implementation is simplified. In production, you would need to implement proper password verification using
    Firebase Auth REST API.
-   **Token Management**: Tokens are returned as placeholders. Implement proper token generation and management for production use.
-   **Error Handling**: Comprehensive error handling with appropriate HTTP status codes.
-   **Logging**: Detailed logging for debugging and monitoring.

## 🔄 Integration

This authentication system integrates seamlessly with your existing LLM routing system. You can:

1. Add authentication to query endpoints
2. Track user query history
3. Personalize responses based on user context
4. Implement usage limits per user
