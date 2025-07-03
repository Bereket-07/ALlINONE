# Simple JWT + Firestore Setup Guide

## What This System Does

✅ **JWT Authentication** - Custom tokens for login/register  
✅ **Firestore Storage** - Users stored in `users` collection  
✅ **Simple & Clean** - No complex features

## Quick Setup

### 1. Environment Variables

Create `.env` file:

```env
# JWT Secret
JWT_SECRET=your-super-secret-jwt-key-change-in-production

# Firebase Credentials (required)
FIREBASE_CREDENTIALS_PATH=path/to/your/firebase-credentials.json

# LLM API Keys
OPENAI_API_KEY=your-openai-api-key
GOOGLE_API_KEY=your-google-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### 2. Get Firebase Credentials

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create/select project
3. Project Settings → Service Accounts
4. Generate new private key
5. Download JSON file
6. Put it in your project folder
7. Update `FIREBASE_CREDENTIALS_PATH` in `.env`

### 3. Enable Firestore

1. In Firebase Console → Firestore Database
2. Create database
3. Start in test mode
4. Choose location

### 4. Install & Run

```bash
pip install -r requirements.txt
python -m uvicorn src.app:app --reload
```

## API Endpoints

### Register User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "display_name": "John Doe"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### Get Profile (Protected)

```bash
curl -X GET "http://localhost:8000/api/v1/auth/profile" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Use LLM Query (Protected)

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the capital of France?"
  }'
```

## Firestore Data Structure

### `users` Collection

```json
{
	"uid": "uuid-string",
	"email": "user@example.com",
	"display_name": "John Doe",
	"email_verified": false,
	"created_at": "2024-01-01T12:00:00Z",
	"last_sign_in": "2024-01-01T12:00:00Z",
	"password_hash": "bcrypt-hashed-password"
}
```

## That's It!

-   Users are stored in Firestore `users` collection
-   JWT tokens for authentication
-   Simple and clean implementation
-   No complex features or fallbacks

Your authentication system is ready! 🚀
