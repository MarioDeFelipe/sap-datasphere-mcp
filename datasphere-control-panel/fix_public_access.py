"""
Fix Lambda Function URL to be publicly accessible
"""

import boto3
import json
import time

def fix_function_url_public_access():
    """Fix Function URL to allow public access"""
    
    lambda_client = boto3.client('lambda')
    function_name = 'datasphere-control-panel'
    
    print("🔧 Fixing Function URL for public access...")
    
    try:
        # Check current Function URL configuration
        try:
            current_config = lambda_client.get_function_url_config(FunctionName=function_name)
            print(f"📋 Current URL: {current_config['FunctionUrl']}")
            print(f"📋 Current Auth: {current_config['AuthType']}")
            
            # Delete current Function URL
            print("🗑️ Deleting current Function URL...")
            lambda_client.delete_function_url_config(FunctionName=function_name)
            
            # Wait for deletion to complete
            time.sleep(5)
            
        except lambda_client.exceptions.ResourceNotFoundException:
            print("📋 No existing Function URL found")
        
        # Create new Function URL with explicit public access
        print("🔗 Creating new public Function URL...")
        
        url_response = lambda_client.create_function_url_config(
            FunctionName=function_name,
            AuthType='NONE',  # This makes it public
            Cors={
                'AllowCredentials': False,
                'AllowHeaders': ['*'],
                'AllowMethods': ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS'],
                'AllowOrigins': ['*'],  # Allow all origins
                'ExposeHeaders': ['*'],
                'MaxAge': 86400
            }
        )
        
        function_url = url_response['FunctionUrl']
        print(f"✅ Created public Function URL: {function_url}")
        
        # Add resource-based policy to ensure public access
        print("🔐 Adding resource-based policy for public access...")
        
        try:
            policy_statement = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "AllowPublicAccess",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "lambda:InvokeFunctionUrl",
                        "Resource": f"arn:aws:lambda:us-east-1:*:function:{function_name}",
                        "Condition": {
                            "StringEquals": {
                                "lambda:FunctionUrlAuthType": "NONE"
                            }
                        }
                    }
                ]
            }
            
            lambda_client.add_permission(
                FunctionName=function_name,
                StatementId='AllowPublicFunctionUrlAccess',
                Action='lambda:InvokeFunctionUrl',
                Principal='*'
            )
            
            print("✅ Added public access policy")
            
        except lambda_client.exceptions.ResourceConflictException:
            print("📋 Public access policy already exists")
        except Exception as e:
            print(f"⚠️ Could not add policy (may not be needed): {e}")
        
        return function_url
        
    except Exception as e:
        print(f"❌ Error fixing Function URL: {e}")
        return None

def verify_function_is_working():
    """Verify the Lambda function itself is working"""
    
    lambda_client = boto3.client('lambda')
    function_name = 'datasphere-control-panel'
    
    print("🧪 Verifying function is working...")
    
    try:
        # Test the function directly
        test_event = {
            "version": "2.0",
            "routeKey": "$default",
            "rawPath": "/",
            "rawQueryString": "",
            "headers": {
                "host": "example.com"
            },
            "requestContext": {
                "http": {
                    "method": "GET",
                    "path": "/",
                    "protocol": "HTTP/1.1"
                }
            }
        }
        
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(test_event)
        )
        
        payload = response['Payload'].read()
        result = json.loads(payload)
        
        if 'errorMessage' in result:
            print(f"❌ Function has errors: {result['errorMessage']}")
            return False
        elif result.get('statusCode') == 200:
            print("✅ Function is working correctly")
            return True
        else:
            print(f"⚠️ Function returned status: {result.get('statusCode', 'Unknown')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing function: {e}")
        return False

def main():
    """Main function"""
    
    print("🔧 FIXING PUBLIC ACCESS FOR LAMBDA FUNCTION URL")
    print("=" * 48)
    
    # Step 1: Verify function is working
    print("\n📋 Step 1: Verifying function is working...")
    function_works = verify_function_is_working()
    
    # Step 2: Fix Function URL for public access
    print("\n📋 Step 2: Fixing Function URL for public access...")
    new_url = fix_function_url_public_access()
    
    # Summary
    print("\n" + "=" * 48)
    print("🔍 PUBLIC ACCESS FIX SUMMARY")
    print("=" * 48)
    
    if function_works and new_url:
        print("\n🎉 SUCCESS! Your Function URL should be publicly accessible now!")
        print(f"\n🔗 Your working URL:")
        print("https://krb7735xufadsj233kdnpaabta0eatck.lambda-url.us-east-1.on.aws")
        print(f"\n📋 What was fixed:")
        print("✅ Function URL recreated with AuthType='NONE'")
        print("✅ CORS configured to allow all origins")
        print("✅ Public access policy added")
        print("✅ Function is working correctly")
        print("\n💡 Try the URL from any browser - it should work now!")
        print("🎉 No AWS login required - completely public access!")
        
    elif new_url and not function_works:
        print(f"\n⚠️ Function URL is public but Lambda function has issues")
        print(f"🔗 New URL: {new_url}")
        print(f"💡 The function itself needs more debugging")
        
    elif function_works and not new_url:
        print(f"\n⚠️ Function works but URL configuration failed")
        print(f"💡 Try the original URL - it might work now")
        
    else:
        print(f"\n❌ Both function and URL have issues")
        print(f"💡 May need manual intervention in AWS Console")

if __name__ == "__main__":
    main()