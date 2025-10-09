"""
Fix the Lambda function that has the Function URL
"""

import boto3
import json
import zipfile
import os

def find_function_with_url():
    """Find which Lambda function has the Function URL"""
    
    lambda_client = boto3.client('lambda')
    
    print("🔍 Finding Lambda function with your URL...")
    
    try:
        # List all functions
        paginator = lambda_client.get_paginator('list_functions')
        
        for page in paginator.paginate():
            for func in page['Functions']:
                try:
                    # Check if function has a Function URL
                    url_config = lambda_client.get_function_url_config(
                        FunctionName=func['FunctionName']
                    )
                    
                    if 'krb7735xufadsj233kdnpaabta0eatck' in url_config['FunctionUrl']:
                        print(f"✅ Found function: {func['FunctionName']}")
                        return func['FunctionName']
                        
                except lambda_client.exceptions.ResourceNotFoundException:
                    # Function doesn't have a URL, continue
                    continue
                except Exception as e:
                    continue
        
        print("❌ Could not find function with that URL")
        return None
        
    except Exception as e:
        print(f"❌ Error searching functions: {e}")
        return None

def fix_function_with_url(function_name):
    """Fix the specific function that has the URL"""
    
    lambda_client = boto3.client('lambda')
    
    print(f"🔧 Fixing function: {function_name}")
    
    try:
        # Read your original working app
        with open('app.py', 'r', encoding='utf-8') as f:
            original_code = f.read()
        
        # Create a simple working version
        working_code = original_code.replace(
            'handler = Mangum(app)',
            '''handler = Mangum(app)

def lambda_handler(event, context):
    """AWS Lambda handler"""
    try:
        return handler(event, context)
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }'''
        )
        
        # Create deployment package
        zip_filename = 'fix_url_function.zip'
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr('lambda_function.py', working_code)
        
        # Read deployment package
        with open(zip_filename, 'rb') as f:
            zip_content = f.read()
        
        # Update function code
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        
        print(f"✅ Updated {function_name} successfully!")
        
        # Clean up
        if os.path.exists(zip_filename):
            os.remove(zip_filename)
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating function: {e}")
        return False

def main():
    """Main function"""
    
    print("🚨 Fixing Lambda Function URL Error")
    print("=" * 40)
    
    # Find the function with your URL
    function_name = find_function_with_url()
    
    if not function_name:
        print("\n💡 Let me try common function names...")
        # Try common names
        possible_names = [
            'hello-world-datasphere',
            'datasphere-control-panel',
            'ailien-studio-app',
            'sap-datasphere-app'
        ]
        
        lambda_client = boto3.client('lambda')
        
        for name in possible_names:
            try:
                # Check if function exists and has URL
                lambda_client.get_function(FunctionName=name)
                try:
                    url_config = lambda_client.get_function_url_config(FunctionName=name)
                    print(f"📋 Function {name} has URL: {url_config['FunctionUrl']}")
                    
                    if 'krb7735xufadsj233kdnpaabta0eatck' in url_config['FunctionUrl']:
                        function_name = name
                        break
                except:
                    pass
            except:
                continue
    
    if function_name:
        print(f"\n🎯 Fixing function: {function_name}")
        success = fix_function_with_url(function_name)
        
        if success:
            print("\n✅ Function fixed!")
            print("🔗 Your URL should work now:")
            print("https://krb7735xufadsj233kdnpaabta0eatck.lambda-url.us-east-1.on.aws")
        else:
            print("\n❌ Fix failed")
    else:
        print("\n❌ Could not identify the function with your URL")
        print("💡 Please check AWS Console to see which function has the Function URL")

if __name__ == "__main__":
    main()