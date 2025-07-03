#!/usr/bin/env python3
"""
Firebase Configuration Test Script
This script helps debug Firebase configuration issues.
"""

import os
import firebase_admin
from firebase_admin import credentials, auth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_firebase_config():
    """Test Firebase configuration and authentication setup."""
    
    print("🔍 Testing Firebase Configuration...")
    print("=" * 50)
    
    # Check environment variables
    print("1. Checking environment variables:")
    credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
    print(f"   FIREBASE_CREDENTIALS_PATH: {credentials_path}")
    
    if not credentials_path:
        print("   ❌ FIREBASE_CREDENTIALS_PATH not set!")
        return False
    
    if not os.path.exists(credentials_path):
        print(f"   ❌ Credentials file not found at: {credentials_path}")
        return False
    
    print("   ✅ Credentials file found")
    
    # Test Firebase initialization
    print("\n2. Testing Firebase initialization:")
    try:
        # Check if already initialized
        if firebase_admin._apps:
            print("   ⚠️  Firebase already initialized")
            return True
        
        # Initialize Firebase
        cred = credentials.Certificate(credentials_path)
        app = firebase_admin.initialize_app(cred)
        print("   ✅ Firebase initialized successfully")
        
        # Test authentication
        print("\n3. Testing Firebase Authentication:")
        
        # Try to list users (this will test if auth is working)
        try:
            # This will fail if auth is not configured, but it's a good test
            page = auth.list_users()
            print("   ✅ Firebase Authentication is working")
        except Exception as e:
            print(f"   ⚠️  Auth test result: {e}")
            print("   This might be normal if no users exist yet")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Firebase initialization failed: {e}")
        return False

def test_user_creation():
    """Test user creation functionality."""
    
    print("\n4. Testing user creation:")
    
    if not firebase_admin._apps:
        print("   ❌ Firebase not initialized")
        return False
    
    test_email = "test@example.com"
    
    try:
        # Check if test user exists
        try:
            user = auth.get_user_by_email(test_email)
            print(f"   ⚠️  Test user already exists: {user.uid}")
            
            # Try to delete the test user
            try:
                auth.delete_user(user.uid)
                print("   ✅ Test user deleted successfully")
            except Exception as e:
                print(f"   ⚠️  Could not delete test user: {e}")
                
        except auth.UserNotFoundError:
            print("   ✅ Test user does not exist (good)")
        
        # Try to create a test user
        user_properties = {
            'email': test_email,
            'password': 'testpassword123',
            'display_name': 'Test User'
        }
        
        user_record = auth.create_user(**user_properties)
        print(f"   ✅ Test user created successfully: {user_record.uid}")
        
        # Clean up - delete the test user
        auth.delete_user(user_record.uid)
        print("   ✅ Test user cleaned up")
        
        return True
        
    except Exception as e:
        print(f"   ❌ User creation test failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    print("🚀 Firebase Configuration Test")
    print("=" * 50)
    
    # Test basic configuration
    if test_firebase_config():
        print("\n✅ Basic Firebase configuration is working")
        
        # Test user creation
        if test_user_creation():
            print("\n✅ User creation is working")
            print("\n🎉 All tests passed! Your Firebase setup is correct.")
        else:
            print("\n❌ User creation test failed")
            print("\n🔧 Troubleshooting steps:")
            print("1. Go to Firebase Console: https://console.firebase.google.com/")
            print("2. Select your project: all-in-one-ai-464811")
            print("3. Go to Authentication > Sign-in method")
            print("4. Enable 'Email/Password' provider")
            print("5. Save the changes")
    else:
        print("\n❌ Firebase configuration test failed")
        print("\n🔧 Check your setup:")
        print("1. Verify FIREBASE_CREDENTIALS_PATH in .env file")
        print("2. Ensure the credentials file exists and is valid")
        print("3. Check Firebase project configuration") 