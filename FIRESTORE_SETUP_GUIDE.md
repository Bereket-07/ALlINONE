# Firestore Integration Setup Guide

This guide explains how to enable Firestore database storage for the JWT authentication system.

## Overview

The application now supports **hybrid storage**:

-   **In-Memory Storage** (default): Fast but users are lost on server restart
-   **Firestore Storage** (optional): Persistent storage in Google Firestore database

## Benefits of Firestore Integration

✅ **Persistent User Data**: Users remain after server restarts  
✅ **Scalable**: Handles thousands of users  
✅ **Real-time**: Automatic synchronization  
✅ **Secure**: Google's enterprise-grade security  
✅ **Backup**: Automatic backups and disaster recovery

## Setup Instructions

### 1. Enable Firestore in Environment Variables

Add these variables to your `.env` file:

```env
# Enable Firestore storage
USE_FIRESTORE=true

# Firebase service account credentials path
FIREBASE_CREDENTIALS_PATH=path/to/your/firebase-credentials.json

# JWT Configuration (still required)
JWT_SECRET=your-super-secret-jwt-key-change-in-production

# LLM API Keys (existing)
OPENAI_API_KEY=your-openai-api-key
GOOGLE_API_KEY=your-google-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### 2. Get Firebase Service Account Credentials

1. **Go to Firebase Console**: https://console.firebase.google.com/
2. **Select your project** (or create a new one)
3. **Go to Project Settings** (gear icon)
4. **Go to Service Accounts tab**
5. **Click "Generate new private key"**
6. **Download the JSON file**
7. **Place it in your project** (e.g., `firebase-credentials.json`)
8. **Update your .env file** with the correct path

### 3. Enable Firestore Database

1. **In Firebase Console**, go to **Firestore Database**
2. **Click "Create database"**
3. **Choose "Start in test mode"** (for development)
4. **Select a location** (choose closest to your users)
5. **Click "Done"**

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Test the Setup

Start the server and register a user:

```bash
python -m uvicorn src.app:app --reload
```

Register a user:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "display_name": "Test User"
  }'
```

**Check Firestore Console**: You should see the user data in the `users` collection!

## Firestore Data Structure

The application creates two collections in Firestore:

### `users` Collection

```json
{
	"uid": "uuid-string",
	"email": "user@example.com",
	"display_name": "John Doe",
	"email_verified": false,
	"created_at": "2024-01-01T12:00:00Z",
	"last_sign_in": "2024-01-01T12:00:00Z"
}
```

### `user_auth` Collection

```json
{
	"uid": "uuid-string",
	"password_hash": "bcrypt-hashed-password",
	"created_at": "2024-01-01T12:00:00Z"
}
```

**Security Note**: Password hashes are stored separately from user data for better security.

## Configuration Options

### Environment Variables

| Variable                    | Default | Description                       |
| --------------------------- | ------- | --------------------------------- |
| `USE_FIRESTORE`             | `false` | Enable/disable Firestore storage  |
| `FIREBASE_CREDENTIALS_PATH` | -       | Path to Firebase credentials JSON |

### Fallback Behavior

If Firestore is enabled but fails to initialize:

-   The system automatically falls back to in-memory storage
-   Users are logged with warnings
-   Application continues to work normally

## Security Best Practices

### 1. Firebase Security Rules

Set up proper Firestore security rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only read their own data
    match /users/{userId} {
      allow read: if request.auth != null && request.auth.uid == userId;
      allow write: if false; // Only server can write
    }

    // Auth data is server-only
    match /user_auth/{userId} {
      allow read, write: if false; // Server only
    }
  }
}
```

### 2. Service Account Security

-   **Never commit** Firebase credentials to version control
-   **Use environment variables** for credential paths
-   **Rotate credentials** regularly in production
-   **Limit permissions** to only what's needed

### 3. Production Considerations

-   **Enable Firestore** in production for data persistence
-   **Set up proper security rules**
-   **Monitor usage** and costs
-   **Backup data** regularly
-   **Use Firebase Auth** for additional security layers

## Troubleshooting

### Common Issues

1. **"Firebase credentials not found"**

    - Check the path in `FIREBASE_CREDENTIALS_PATH`
    - Ensure the JSON file exists and is readable

2. **"Firestore not initialized"**

    - Check Firebase project settings
    - Ensure Firestore database is created
    - Verify service account permissions

3. **"Permission denied"**

    - Check Firestore security rules
    - Verify service account has proper permissions

4. **"User not found" errors**
    - Check if user exists in Firestore console
    - Verify collection names (`users`, `user_auth`)

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Testing Firestore Connection

Test the connection manually:

```python
from src.infrastructure.firebase.firestore_service import FirestoreService

# Initialize
success = FirestoreService.initialize("path/to/credentials.json")
print(f"Firestore initialized: {success}")

# Test operations
if success:
    # Create test user
    user_data = {
        'uid': 'test-123',
        'email': 'test@example.com',
        'display_name': 'Test User',
        'email_verified': False,
        'created_at': datetime.utcnow(),
        'last_sign_in': datetime.utcnow(),
        'password_hash': 'test-hash'
    }

    result = await FirestoreService.create_user(user_data)
    print(f"User created: {result}")
```

## Migration from In-Memory to Firestore

### Existing Users

If you have existing users in memory:

1. **Export current users** (if any)
2. **Enable Firestore** with `USE_FIRESTORE=true`
3. **Restart the server**
4. **Users will need to re-register** (or implement migration script)

### Migration Script (Optional)

For production migrations, create a script to transfer existing users:

```python
# migration_script.py
from src.use_cases.auth_use_cases import AuthUseCases
from src.infrastructure.firebase.firestore_service import FirestoreService

async def migrate_users():
    """Migrate users from memory to Firestore."""
    FirestoreService.initialize("path/to/credentials.json")

    for uid, user_data in AuthUseCases._users.items():
        success = await FirestoreService.create_user(user_data)
        print(f"Migrated user {uid}: {success}")

# Run migration
import asyncio
asyncio.run(migrate_users())
```

## Performance Considerations

### Firestore Queries

-   **Indexed queries**: Email lookups are fast
-   **Document reads**: Efficient for user profile access
-   **Batch operations**: Consider for bulk operations

### Caching

For high-traffic applications, consider:

-   **Redis caching** for frequently accessed user data
-   **Token caching** to reduce database calls
-   **Connection pooling** for better performance

## Cost Optimization

### Firestore Pricing

-   **Document reads**: $0.06 per 100,000 reads
-   **Document writes**: $0.18 per 100,000 writes
-   **Document deletes**: $0.02 per 100,000 deletes

### Optimization Tips

-   **Minimize reads**: Cache user data when possible
-   **Batch operations**: Use batch writes for multiple updates
-   **Monitor usage**: Set up billing alerts
-   **Clean up**: Remove unused documents

## Monitoring and Logging

### Firebase Console

Monitor your Firestore usage in the Firebase Console:

-   **Usage tab**: Track read/write operations
-   **Performance tab**: Monitor query performance
-   **Logs tab**: View detailed operation logs

### Application Logs

The application logs all Firestore operations:

-   User creation/deletion
-   Authentication attempts
-   Error conditions
-   Performance metrics

## Next Steps

1. **Set up Firestore** following this guide
2. **Test user registration** and verify data appears in Firestore
3. **Configure security rules** for production
4. **Monitor usage** and optimize as needed
5. **Set up backups** and disaster recovery procedures

Your JWT authentication system is now fully integrated with Firestore for persistent, scalable user storage! 🚀
