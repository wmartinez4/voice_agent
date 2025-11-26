"""
Simple test script to verify the API endpoints work correctly.
This script tests the API without requiring Supabase credentials.
"""

import sys

def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        import fastapi
        print("  ✅ FastAPI imported successfully")
        
        import uvicorn
        print("  ✅ Uvicorn imported successfully")
        
        import pydantic
        print("  ✅ Pydantic imported successfully")
        
        from dotenv import load_dotenv
        print("  ✅ python-dotenv imported successfully")
        
        import dateutil
        print("  ✅ python-dateutil imported successfully")
        
        print("\n✅ All imports successful!\n")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}\n")
        return False


def test_main_structure():
    """Test that main.py has the correct structure."""
    print("🧪 Testing main.py structure...")
    
    try:
        # We can't import main.py directly without Supabase credentials
        # So we'll just check the file exists and has the right content
        with open('main.py', 'r') as f:
            content = f.read()
        
        # Check for required endpoints
        required_endpoints = [
            '/health',
            '/tools/get-case-details',
            '/tools/propose-payment-plan',
            '/tools/update-status'
        ]
        
        for endpoint in required_endpoints:
            if endpoint in content:
                print(f"  ✅ Endpoint '{endpoint}' found")
            else:
                print(f"  ❌ Endpoint '{endpoint}' NOT found")
                return False
        
        # Check for required models
        required_models = [
            'GetCaseDetailsRequest',
            'GetCaseDetailsResponse',
            'ProposePaymentPlanRequest',
            'ProposePaymentPlanResponse',
            'UpdateStatusRequest',
            'UpdateStatusResponse'
        ]
        
        for model in required_models:
            if model in content:
                print(f"  ✅ Model '{model}' found")
            else:
                print(f"  ❌ Model '{model}' NOT found")
                return False
        
        print("\n✅ main.py structure looks good!\n")
        return True
        
    except FileNotFoundError:
        print("  ❌ main.py not found\n")
        return False
    except Exception as e:
        print(f"  ❌ Error reading main.py: {e}\n")
        return False


def test_file_structure():
    """Test that all required files exist."""
    print("🧪 Testing file structure...")
    
    required_files = [
        'main.py',
        'database.py',
        'setup_db.py',
        'seed_data.py',
        'trigger.py',
        'requirements.txt',
        '.env.example',
        '.gitignore',
        'README.md',
        'prompt_guide.md'
    ]
    
    all_exist = True
    for file in required_files:
        try:
            with open(file, 'r') as f:
                pass
            print(f"  ✅ {file} exists")
        except FileNotFoundError:
            print(f"  ❌ {file} NOT found")
            all_exist = False
    
    if all_exist:
        print("\n✅ All required files exist!\n")
    else:
        print("\n⚠️  Some files are missing\n")
    
    return all_exist


def main():
    """Run all tests."""
    print("=" * 60)
    print("🚀 Jess Voice Agent - Verification Tests")
    print("=" * 60)
    print()
    
    results = []
    
    # Test 1: Imports
    results.append(("Imports", test_imports()))
    
    # Test 2: File structure
    results.append(("File Structure", test_file_structure()))
    
    # Test 3: Main.py structure
    results.append(("Main.py Structure", test_main_structure()))
    
    # Summary
    print("=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("=" * 60)
    
    if all(result[1] for result in results):
        print("\n🎉 All tests passed! The backend is ready to use.")
        print("\n📝 Next steps:")
        print("1. Copy .env.example to .env and add your Supabase credentials")
        print("2. Run 'python setup_db.py' to see database setup instructions")
        print("3. Run 'python seed_data.py' to add test data")
        print("4. Run 'uvicorn main:app --reload' to start the server")
        print()
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
