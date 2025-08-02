# backend/verify_setup.py

"""
Quick verification script to check if your setup is correct
"""

import os
import sys
import traceback

def check_file_structure():
    """Check if all required files exist"""
    print("📁 Checking file structure...")
    
    required_files = [
        "app/__init__.py",
        "app/main.py", 
        "app/api/__init__.py",
        "app/api/api_v1.py",
        "app/api/v1/__init__.py",
        "app/api/v1/auth.py",
        "app/db/__init__.py",
        "app/db/database.py",
        "app/db/models/__init__.py",
        "app/db/models/user.py",
        "app/core/__init__.py",
        "app/core/security.py",
        "app/utils/__init__.py",
        "app/utils/jwt_token.py",
        ".env"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    else:
        print("✅ All required files present")
        return True

def check_imports():
    """Check if all imports work"""
    print("\n🔍 Checking imports...")
    
    try:
        # Test core imports
        from app.core.config import settings
        print("✅ Settings imported")
        
        from app.core.security import get_password_hash
        print("✅ Security imported")
        
        from app.db.database import get_db
        print("✅ Database imported")
        
        from app.db.models import User
        print("✅ User model imported")
        
        from app.api.api_v1 import api_router
        print("✅ API router imported")
        
        from app.main import app
        print("✅ Main app imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False

def check_database():
    """Check database connection and tables"""
    print("\n🗄️ Checking database...")
    
    try:
        from app.db.database import engine
        from sqlalchemy import text
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
        
        # Check if tables exist
        from app.db.models import User
        from sqlalchemy.orm import sessionmaker
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            user_count = db.query(User).count()
            print(f"✅ User table exists with {user_count} users")
            return True
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

def check_test_user():
    """Check if test user exists and can login"""
    print("\n👤 Checking test user...")
    
    try:
        from app.db.database import engine
        from app.db.models import User
        from app.core.security import verify_password
        from sqlalchemy.orm import sessionmaker
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            user = db.query(User).filter(User.email == "test@example.com").first()
            if not user:
                print("❌ Test user not found")
                return False
            
            print(f"✅ Test user found: {user.email}")
            
            # Test password
            if verify_password("testpassword", user.hashed_password):
                print("✅ Test user password is correct")
                return True
            else:
                print("❌ Test user password is incorrect")
                return False
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Test user check failed: {e}")
        return False

def main():
    """Run all verification checks"""
    print("🔧 Contact Page Submitter - Setup Verification")
    print("=" * 50)
    
    checks = [
        ("File Structure", check_file_structure),
        ("Imports", check_imports),
        ("Database", check_database),
        ("Test User", check_test_user),
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name} check crashed: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 All checks passed! Your setup is correct.")
        print("\n🚀 Ready to start:")
        print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        print("\n🧪 Test login:")
        print("   curl -X POST http://localhost:8000/api/v1/auth/login \\")
        print("     -H 'Content-Type: application/x-www-form-urlencoded' \\")
        print("     -d 'username=test@example.com&password=testpassword'")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\n📋 Common fixes:")
        print("1. Create missing __init__.py files")
        print("2. Run: python create_user_and_tables.py")
        print("3. Check your .env file")

if __name__ == "__main__":
    main()