"""
Fix the Function URL configuration to resolve Forbidden error
"""

import boto3
import json
import time

def check_and_fix_function_url():
    """Check and fix the Function URL configuration"""
    
    lambda_client = boto3.client('lambda')
    function_name = 'ailien-studio-control-panel'
    
    print("🔍 Checking Function URL configuration...")
    
    try:
        # Check current Function URL config
        try:
            url_config = lambda_client.get_function_url_config(FunctionName=function_name)
            print(f"📋 Current Function URL: {url_config['FunctionUrl']}")
            print(f"📋 Auth Type: {url_config['AuthType']}")
            print(f"📋 Creation Time: {url_config['CreationTime']}")
            
            if url_config['AuthType'] != 'NONE':
                print("❌ Auth Type is not NONE - this could cause Forbidden errors")
                
                # Delete and recreate with correct auth
                print("🔧 Recreating Function URL with correct auth...")
                
                lambda_client.delete_function_url_config(FunctionName=function_name)
                time.sleep(2)
                
                # Create new Function URL with NONE auth
                new_url_response = lambda_client.create_function_url_config(
                    FunctionName=function_name,
                    AuthType='NONE',
                    Cors={
                        'AllowCredentials': False,
                        'AllowHeaders': ['*'],
                        'AllowMethods': ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS'],
                        'AllowOrigins': ['*'],
                        'MaxAge': 86400
                    }
                )
                
                new_url = new_url_response['FunctionUrl']
                print(f"✅ Created new Function URL: {new_url}")
                return new_url
            else:
                print("✅ Auth Type is correctly set to NONE")
                return url_config['FunctionUrl']
                
        except lambda_client.exceptions.ResourceNotFoundException:
            print("❌ Function URL not found - creating new one...")
            
            # Create Function URL
            url_response = lambda_client.create_function_url_config(
                FunctionName=function_name,
                AuthType='NONE',
                Cors={
                    'AllowCredentials': False,
                    'AllowHeaders': ['*'],
                    'AllowMethods': ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS'],
                    'AllowOrigins': ['*'],
                    'MaxAge': 86400
                }
            )
            
            new_url = url_response['FunctionUrl']
            print(f"✅ Created Function URL: {new_url}")
            return new_url
        
    except Exception as e:
        print(f"❌ Error with Function URL: {e}")
        return None

def test_function_directly():
    """Test the Lambda function directly to see if it works"""
    
    lambda_client = boto3.client('lambda')
    function_name = 'ailien-studio-control-panel'
    
    print("🧪 Testing Lambda function directly...")
    
    try:
        # Test with a simple event
        test_event = {
            "requestContext": {
                "http": {
                    "method": "GET",
                    "path": "/",
                    "protocol": "HTTP/1.1"
                }
            },
            "headers": {
                "host": "example.com"
            }
        }
        
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(test_event)
        )
        
        payload = response['Payload'].read()
        result = json.loads(payload)
        
        print(f"📋 Direct test result:")
        print(f"   Status Code: {response.get('StatusCode', 'Unknown')}")
        
        if 'errorMessage' in result:
            print(f"❌ Error: {result['errorMessage']}")
            return False
        else:
            print(f"✅ Function works - Status: {result.get('statusCode', 'Unknown')}")
            return True
            
    except Exception as e:
        print(f"❌ Error testing function: {e}")
        return False

def check_function_permissions():
    """Check if the function has proper permissions"""
    
    lambda_client = boto3.client('lambda')
    function_name = 'ailien-studio-control-panel'
    
    print("🔐 Checking function permissions...")
    
    try:
        # Get function configuration
        func_config = lambda_client.get_function(FunctionName=function_name)
        
        print(f"📋 Function State: {func_config['Configuration'].get('State', 'Unknown')}")
        print(f"📋 Runtime: {func_config['Configuration'].get('Runtime', 'Unknown')}")
        print(f"📋 Handler: {func_config['Configuration'].get('Handler', 'Unknown')}")
        
        # Check if function is active
        if func_config['Configuration'].get('State') != 'Active':
            print(f"❌ Function is not in Active state: {func_config['Configuration'].get('State')}")
            return False
        
        # Try to get function policy (this might not exist and that's OK)
        try:
            policy = lambda_client.get_policy(FunctionName=function_name)
            print("📋 Function has a resource policy")
        except lambda_client.exceptions.ResourceNotFoundException:
            print("📋 No resource policy (this is normal for Function URLs)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking permissions: {e}")
        return False

def main():
    """Main function"""
    
    print("🔧 FIXING FUNCTION URL FORBIDDEN ERROR")
    print("=" * 42)
    
    # Step 1: Check function permissions
    print("\n📋 Step 1: Checking function permissions...")
    permissions_ok = check_function_permissions()
    
    # Step 2: Test function directly
    print("\n📋 Step 2: Testing function directly...")
    function_works = test_function_directly()
    
    # Step 3: Check and fix Function URL
    print("\n📋 Step 3: Checking Function URL configuration...")
    new_url = check_and_fix_function_url()
    
    # Summary
    print("\n" + "=" * 42)
    print("🔍 DIAGNOSIS SUMMARY")
    print("=" * 42)
    
    print(f"✅ Function Permissions: {'OK' if permissions_ok else 'ISSUES'}")
    print(f"✅ Function Execution: {'OK' if function_works else 'ISSUES'}")
    print(f"✅ Function URL: {'FIXED' if new_url else 'ISSUES'}")
    
    if new_url and function_works and permissions_ok:
        print(f"\n🎉 EVERYTHING SHOULD WORK NOW!")
        print(f"🔗 Try this URL: {new_url}")
        print(f"\n💡 If you still get Forbidden:")
        print(f"1. Wait 1-2 minutes for AWS to propagate changes")
        print(f"2. Try in an incognito/private browser window")
        print(f"3. Clear your browser cache")
    else:
        print(f"\n❌ ISSUES DETECTED:")
        if not permissions_ok:
            print(f"• Function permissions need attention")
        if not function_works:
            print(f"• Function execution has errors")
        if not new_url:
            print(f"• Function URL configuration failed")

if __name__ == "__main__":
    main()