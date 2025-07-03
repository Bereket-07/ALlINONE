# Authentication System Documentation

This document describes the comprehensive authentication and authorization system built with Firebase Authentication and FastAPI.

## 🏗️ Architecture Overview

The authentication system follows Clean Architecture principles with the following layers:

-   **Domain Layer**: Data models and business entities
-   **Use Cases Layer**: Business logic for authentication operations
-   **Infrastructure Layer**: Firebase integration and external services
-   **Controllers Layer**: HTTP endpoints and request handling

## 🔧 Setup Requirements

### Environment Variables

Make sure your `.env` file contains:

```bash
FIREBASE_CREDENTIALS_PATH=all-in-one-ai-464811-firebase-adminsdk-fbsvc-75931db9e6.json
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
ANTHROPIC_API_KEY=your_anthropic_key
```

### Dependencies

The system requires these additional packages:

```bash
pip install firebase-admin email-validator
```

## 📋 API Endpoints

### Authentication Endpoints

#### 1. User Registration

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

#### 2. User Login

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

#### 3. Get User Profile

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

#### 4. Update User Profile

```http
PUT /api/v1/auth/profile
Authorization: Bearer <firebase_id_token>
Content-Type: application/json

{
  "display_name": "John Smith"
}
```

**Response:**

```json
{
	"uid": "firebase_user_uid",
	"email": "user@example.com",
	"display_name": "John Smith",
	"email_verified": false,
	"created_at": "2024-01-01T00:00:00",
	"last_sign_in": "2024-01-01T12:00:00"
}
```

#### 5. Delete User Account

```http
DELETE /api/v1/auth/account
Authorization: Bearer <firebase_id_token>
```

**Response:** `204 No Content`

#### 6. Verify Token

```http
POST /api/v1/auth/verify-token
Authorization: Bearer <firebase_id_token>
```

**Response:**

```json
{
	"valid": true,
	"user_id": "firebase_user_uid",
	"email": "user@example.com"
}
```

#### 7. Send Email Verification

```http
POST /api/v1/auth/send-email-verification
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Response:**

```json
{
	"message": "Email verification sent successfully"
}
```

#### 8. Send Password Reset

```http
POST /api/v1/auth/send-password-reset
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Response:**

```json
{
	"message": "Password reset email sent successfully"
}
```

## 🔐 Authentication Flow

### 1. Registration Flow

1. User submits registration data
2. System checks if user already exists
3. Creates new Firebase user account
4. Returns user profile (no tokens - user must login)

### 2. Login Flow

1. User submits login credentials
2. System verifies user exists
3. Returns user profile with authentication tokens
4. Client stores tokens for subsequent requests

### 3. Protected Route Access

1. Client includes `Authorization: Bearer <token>` header
2. System verifies Firebase ID token
3. Extracts user information from token
4. Allows access to protected resources

## 🛡️ Security Features

### Token-Based Authentication

-   Uses Firebase ID tokens for authentication
-   Tokens are verified on every protected request
-   Automatic token expiration handling

### Input Validation

-   Email format validation using `email-validator`
-   Password strength requirements (min 6 characters)
-   Display name length limits

### Error Handling

-   Comprehensive error responses with appropriate HTTP status codes
-   Detailed logging for debugging
-   Graceful handling of Firebase errors

## 📁 File Structure

```
src/
├── domain/models/
│   ├── auth_models.py          # Authentication data models
│   └── llm_selection.py        # Existing LLM models
├── use_cases/
│   ├── auth_use_cases.py       # Authentication business logic
│   └── route_query.py          # Existing LLM routing
├── controllers/
│   ├── auth_controller.py      # Authentication endpoints
│   └── query_controller.py     # Existing query endpoints
├── infrastructure/
│   ├── firebase/
│   │   ├── firebase_config.py  # Firebase configuration
│   │   ├── auth_service.py     # Firebase Auth service
│   │   └── __init__.py
│   └── middleware/
│       ├── auth_middleware.py  # Authentication middleware
│       └── __init__.py
└── app.py                      # Main application
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

#### Access protected endpoint:

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

# Access protected endpoint
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:8000/api/v1/auth/profile", headers=headers)
print(response.json())
```

## 🔧 Configuration

### Firebase Setup

1. Create a Firebase project
2. Enable Authentication with Email/Password provider
3. Download service account key
4. Set `FIREBASE_CREDENTIALS_PATH` environment variable

### Email Templates

Configure email templates in Firebase Console:

-   Email verification template
-   Password reset template

## 🐛 Troubleshooting

### Common Issues

1. **Firebase initialization failed**

    - Check if credentials file exists and path is correct
    - Verify Firebase project configuration

2. **Token verification failed**

    - Ensure token is not expired
    - Check if token format is correct (Bearer <token>)

3. **User not found**
    - Verify user exists in Firebase Authentication
    - Check email spelling

### Logging

The system provides detailed logging. Check logs for:

-   Firebase initialization status
-   Authentication attempts
-   Token verification results
-   Error details

## 🔄 Integration with Existing System

The authentication system integrates seamlessly with the existing LLM routing system:

1. **Protected Queries**: Add authentication to query endpoints
2. **User-Specific Responses**: Use user context for personalized responses
3. **Usage Tracking**: Track user query history and preferences

## 📈 Future Enhancements

-   [ ] Role-based access control (RBAC)
-   [ ] Social authentication (Google, Facebook, etc.)
-   [ ] Multi-factor authentication (MFA)
-   [ ] Session management
-   [ ] Rate limiting
-   [ ] Audit logging
-   [ ] User preferences storage in Firestore
