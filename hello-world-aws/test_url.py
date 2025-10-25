#!/usr/bin/env python3
"""
Test the Hello World Lambda Function URL
"""

import requests
import time

def test_function_url():
    """Test the Function URL"""
    
    url = "https://7zj6bjcux2fsezxj3hq5cxbosa0jawwt.lambda-url.us-east-1.on.aws/"
    
    print("🧪 Testing Hello World Function URL")
    print("=" * 50)
    print(f"🔗 URL: {url}")
    
    try:
        print("📡 Making HTTP request...")
        response = requests.get(url, timeout=30)
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Content Type: {response.headers.get('content-type')}")
        print(f"✅ Response Length: {len(response.text)} characters")
        
        if response.status_code == 200:
            print("🎉 SUCCESS! Your Hello World app is working!")
            print(f"📄 Response preview:")
            print(response.text[:200] + "..." if len(response.text) > 200 else response.text)
            
            # Save full response
            with open('url_test_response.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"💾 Full response saved to: url_test_response.html")
            
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
        
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_function_url()
    
    if success:
        print(f"\n🎯 Your Hello World app is live and accessible!")
        print(f"🌐 Share this URL with anyone:")
        print(f"🔗 https://7zj6bjcux2fsezxj3hq5cxbosa0jawwt.lambda-url.us-east-1.on.aws/")
    else:
        print(f"\n❌ There's still an issue with the Function URL")
        print(f"💡 Try waiting a few minutes for AWS to propagate the changes")