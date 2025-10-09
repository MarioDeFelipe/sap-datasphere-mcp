#!/usr/bin/env python3
"""
Test the application locally without Docker
Run this to verify everything works before containerizing
"""

import sys
import subprocess
import importlib.util

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    else:
        print("✅ Python version is compatible")
        return True

def check_dependencies():
    """Check if required dependencies are available"""
    required_packages = ['flask', 'requests']
    missing_packages = []
    
    for package in required_packages:
        spec = importlib.util.find_spec(package)
        if spec is None:
            missing_packages.append(package)
            print(f"❌ {package} not found")
        else:
            print(f"✅ {package} is available")
    
    if missing_packages:
        print(f"\n📦 Install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def install_dependencies():
    """Install dependencies from requirements.txt"""
    try:
        print("📦 Installing dependencies...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def test_app():
    """Test the Flask application"""
    try:
        print("🧪 Testing Flask application...")
        
        # Import the app
        from app import app
        
        # Test client
        with app.test_client() as client:
            # Test homepage
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Homepage works")
            else:
                print(f"❌ Homepage failed: {response.status_code}")
                return False
            
            # Test API
            response = client.get('/api/hello')
            if response.status_code == 200:
                print("✅ API endpoint works")
                data = response.get_json()
                print(f"   Message: {data.get('message', 'N/A')}")
            else:
                print(f"❌ API endpoint failed: {response.status_code}")
                return False
            
            # Test health check
            response = client.get('/health')
            if response.status_code == 200:
                print("✅ Health check works")
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import app: {e}")
        return False
    except Exception as e:
        print(f"❌ App test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 SAP Datasphere Control Panel - Local Test")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    print()
    
    # Check dependencies
    if not check_dependencies():
        print("\n📦 Attempting to install dependencies...")
        if not install_dependencies():
            return False
        print()
    
    # Test the application
    if not test_app():
        return False
    
    print("\n🎉 All tests passed!")
    print("\n🚀 Ready to run with Docker or locally:")
    print("   Local:  python app.py")
    print("   Docker: run.bat start")
    print("\n🌐 Then visit: http://localhost:8000")
    
    return True

if __name__ == '__main__':
    success = main()
    if not success:
        sys.exit(1)