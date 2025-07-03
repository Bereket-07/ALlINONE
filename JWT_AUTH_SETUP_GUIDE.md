# JWT Authentication Setup Guide

This guide will help you set up the custom JWT-based authentication system for the LLM Router application.

## Overview

The application now uses a custom JWT authentication system instead of Firebase. This provides:

-   Full control over authentication logic
-   Custom token generation and validation
-   Secure password hashing with bcrypt
-   Access and refresh token support
-   In-memory user storage (easily replaceable with database)

## Features

### Authentication Endpoints

-   `POST /api/v1/auth/register` - Register a new user
-   `POST /api/v1/auth/login` - Login with email and password
-   `GET /api/v1/auth/profile` - Get current user profile (protected)
-   `POST /api/v1/auth/refresh-token` - Refresh access token

### Security Features

-   Password hashing with bcrypt
-   JWT tokens with configurable expiration
-   Separate access and refresh tokens
-   Token validation and verification
-   Protected routes with middleware

## Setup Instructions

### 1. Environment Variables

Create a `.env` file in your project root with the following variables:

```env
# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-change-in-production

# LLM API Keys (existing)
OPENAI_API_KEY=your-openai-api-key
GOOGLE_API_KEY=your-google-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

**Important**: Change the `JWT_SECRET` to a strong, unique secret key in production!

### 2. Install Dependencies

Install the required packages:

```bash
pip install -r requirements.txt
```

The new dependencies are:

-   `PyJWT` - For JWT token generation and validation
-   `bcrypt` - For secure password hashing

### 3. Run the Application

Start the FastAPI server:

```bash
python -m uvicorn src.app:app --reload
```

## API Usage

### Register a New User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "display_name": "John Doe"
  }'
```

Response:

```json
{
	"user": {
		"uid": "uuid-string",
		"email": "user@example.com",
		"display_name": "John Doe",
		"email_verified": false,
		"created_at": "2024-01-01T12:00:00",
		"last_sign_in": "2024-01-01T12:00:00"
	},
	"token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
	"refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### Get Profile (Protected Route)

```bash
curl -X GET "http://localhost:8000/api/v1/auth/profile" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Refresh Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh-token" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

### Use Protected LLM Query Endpoint

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the capital of France?"
  }'
```

## Token Configuration

### Default Settings

-   **Access Token Expiration**: 30 minutes
-   **Refresh Token Expiration**: 30 days
-   **Algorithm**: HS256
-   **Token Type**: Bearer

### Customizing Token Settings

You can modify the token settings in `src/use_cases/auth_use_cases.py`:

```python
# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Change this value
REFRESH_TOKEN_EXPIRE_DAYS = 30    # Change this value
```

## Security Best Practices

### 1. JWT Secret

-   Use a strong, random secret key
-   Store it securely in environment variables
-   Never commit secrets to version control

### 2. Token Management

-   Access tokens should have short expiration times
-   Refresh tokens should be stored securely on the client
-   Implement token revocation if needed

### 3. Password Security

-   Passwords are automatically hashed with bcrypt
-   Use strong password policies
-   Consider implementing password complexity requirements

### 4. Production Considerations

-   Replace in-memory storage with a database
-   Implement rate limiting
-   Add logging and monitoring
-   Use HTTPS in production
-   Consider implementing refresh token rotation

## Database Integration

Currently, users are stored in memory. For production, replace the `_users` dictionary in `AuthUseCases` with database operations:

```python
# Example with SQLAlchemy
from sqlalchemy.orm import Session

class AuthUseCases:
    @staticmethod
    async def register_user(request: UserRegisterRequest, db: Session) -> Optional[AuthResponse]:
        # Check if user exists in database
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            return None

        # Create new user in database
        hashed_password = AuthUseCases._hash_password(request.password)
        user = User(
            email=request.email,
            password_hash=hashed_password,
            display_name=request.display_name
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Generate tokens and return response
        # ...
```

## Testing

### Test Registration

1. Register a new user
2. Verify the response contains user data and tokens
3. Check that the password is not returned in the response

### Test Login

1. Login with correct credentials
2. Verify tokens are returned
3. Test with incorrect password (should fail)

### Test Protected Routes

1. Try accessing `/api/v1/auth/profile` without token (should fail)
2. Use valid token to access protected route (should succeed)
3. Use expired token (should fail)

### Test Token Refresh

1. Use refresh token to get new access token
2. Verify new tokens work correctly
3. Test with invalid refresh token (should fail)

## Troubleshooting

### Common Issues

1. **"JWT_SECRET not set"**

    - Ensure JWT_SECRET is set in your .env file

2. **"Invalid token" errors**

    - Check that you're using the correct token format: `Bearer <token>`
    - Verify the token hasn't expired
    - Ensure the JWT_SECRET matches between token generation and verification

3. **"User not found" errors**

    - Users are stored in memory, so they're lost on server restart
    - In production, implement persistent storage

4. **Import errors**
    - Ensure all dependencies are installed: `pip install -r requirements.txt`

### Debug Mode

Enable debug logging by setting the log level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Migration from Firebase

If you're migrating from the previous Firebase implementation:

1. **Remove Firebase dependencies**:

    - Delete `firebase-admin` from requirements.txt
    - Remove Firebase configuration from config.py
    - Delete Firebase service files

2. **Update environment variables**:

    - Remove `FIREBASE_CREDENTIALS_PATH` and `FIREBASE_API_KEY`
    - Add `JWT_SECRET`

3. **Update client code**:
    - The API endpoints remain the same
    - Token format is still `Bearer <token>`
    - Response structure is identical

The migration should be seamless for client applications!
