#!/usr/bin/env python3
"""
Test the Hello World Lambda function locally
"""

from app import lambda_handler
import json

def test_lambda_locally():
    """Test the Lambda function locally"""
    
    print("🧪 Testing Hello World Lambda Function Locally")
    print("=" * 50)
    
    # Create test event
    test_event = {
        'requestContext': {
            'http': {
                'method': 'GET',
                'sourceIp': '127.0.0.1'
            }
        },
        'headers': {
            'user-agent': 'Local Test Browser/1.0'
        }
    }
    
    try:
        # Call the Lambda handler
        result = lambda_handler(test_event, None)
        
        print(f"✅ Status Code: {result['statusCode']}")
        print(f"✅ Content Type: {result['headers']['Content-Type']}")
        print(f"✅ Body Length: {len(result['body'])} characters")
        
        # Save HTML to file for viewing
        with open('test_output.html', 'w', encoding='utf-8') as f:
            f.write(result['body'])
        
        print(f"✅ HTML saved to: test_output.html")
        print(f"📋 Open test_output.html in your browser to preview")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_lambda_locally()
    
    if success:
        print(f"\n🎉 Local test successful!")
        print(f"🚀 Ready to deploy to AWS!")
    else:
        print(f"\n❌ Local test failed. Fix issues before deploying.")