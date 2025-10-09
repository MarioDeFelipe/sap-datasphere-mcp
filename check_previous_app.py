#!/usr/bin/env python3
"""
Check the previous application with AI features
"""

import urllib.request
import urllib.error
import json

def check_previous_app():
    """Check if the previous app is still accessible"""
    
    print("🔍 CHECKING PREVIOUS APPLICATION")
    print("=" * 40)
    
    url = "https://mqfguhf5wj.execute-api.us-east-1.amazonaws.com/prod"
    
    try:
        print(f"📋 Testing URL: {url}")
        
        with urllib.request.urlopen(url, timeout=30) as response:
            if response.status == 200:
                content = response.read().decode('utf-8')
                print("✅ Previous application is accessible!")
                print(f"📋 Response length: {len(content)} characters")
                
                # Check for AI features
                if "AI" in content or "ai" in content:
                    print("✅ AI features detected in content!")
                
                if "Q Business" in content or "Amazon Q" in content:
                    print("✅ Q Business integration detected!")
                
                if "Enhanced" in content or "enhanced" in content:
                    print("✅ Enhanced features detected!")
                
                # Save a sample of the content
                print("\n📋 Content preview (first 500 chars):")
                print("-" * 40)
                print(content[:500])
                print("-" * 40)
                
                return True, content
            else:
                print(f"❌ Application returned status: {response.status}")
                return False, None
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error: {e.code} - {e.reason}")
        return False, None
    except Exception as e:
        print(f"❌ Error accessing application: {e}")
        return False, None

def check_api_endpoints():
    """Check if API endpoints are working"""
    
    print("\n🔍 CHECKING API ENDPOINTS")
    print("=" * 40)
    
    base_url = "https://mqfguhf5wj.execute-api.us-east-1.amazonaws.com/prod"
    endpoints = [
        "/api/status",
        "/api/assets", 
        "/api/analytics",
        "/api/insights",
        "/api/recommendations"
    ]
    
    working_endpoints = []
    
    for endpoint in endpoints:
        try:
            url = base_url + endpoint
            print(f"📋 Testing: {endpoint}")
            
            with urllib.request.urlopen(url, timeout=15) as response:
                if response.status == 200:
                    data = response.read().decode('utf-8')
                    print(f"  ✅ Working - {len(data)} chars")
                    working_endpoints.append(endpoint)
                    
                    # Try to parse as JSON
                    try:
                        json_data = json.loads(data)
                        if isinstance(json_data, dict):
                            print(f"  📊 JSON response with {len(json_data)} keys")
                    except:
                        print("  📄 HTML/Text response")
                else:
                    print(f"  ❌ Status: {response.status}")
                    
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:50]}...")
    
    return working_endpoints

def main():
    """Main check process"""
    
    print("🔍 PREVIOUS APPLICATION ANALYSIS")
    print("=" * 50)
    
    # Check main application
    accessible, content = check_previous_app()
    
    if accessible:
        # Check API endpoints
        working_endpoints = check_api_endpoints()
        
        print(f"\n📊 SUMMARY")
        print("=" * 40)
        print("✅ Previous application is accessible!")
        print(f"📋 Working API endpoints: {len(working_endpoints)}")
        
        if working_endpoints:
            print("📋 Available endpoints:")
            for endpoint in working_endpoints:
                print(f"  - {endpoint}")
        
        print("\n💡 RECOMMENDATION:")
        print("We can potentially extract the working AI features")
        print("from this application and apply them to your current one!")
        
        return True
    else:
        print("\n❌ Previous application is not accessible")
        print("We'll need to build Phase 3 from scratch")
        return False

if __name__ == "__main__":
    main()