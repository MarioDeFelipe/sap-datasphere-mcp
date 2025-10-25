#!/usr/bin/env python3
"""
Deploy Hello World Lambda Function to AWS
"""

import json
import zipfile
import boto3
import time
from pathlib import Path

def create_deployment_package():
    """Create a deployment package for Lambda"""
    
    print("📦 Creating deployment package...")
    
    # Create a zip file with the Lambda function
    with zipfile.ZipFile('hello-world-lambda.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write('app.py', 'app.py')
    
    print("✅ Deployment package created: hello-world-lambda.zip")
    return 'hello-world-lambda.zip'

def deploy_lambda_function():
    """Deploy the Lambda function to AWS"""
    
    print("🚀 Deploying Hello World Lambda Function...")
    
    # Initialize AWS clients
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    iam_client = boto3.client('iam', region_name='us-east-1')
    
    function_name = 'hello-world-datasphere'
    
    # Create IAM role for Lambda
    print("🔐 Creating IAM role...")
    
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    role_name = f"{function_name}-role"
    
    try:
        # Try to create the role
        role_response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for Hello World Lambda function'
        )
        role_arn = role_response['Role']['Arn']
        print(f"✅ Created IAM role: {role_arn}")
        
        # Attach basic execution policy
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        
        # Wait for role to be available
        print("⏳ Waiting for IAM role to be available...")
        time.sleep(10)
        
    except iam_client.exceptions.EntityAlreadyExistsException:
        # Role already exists, get its ARN
        role_response = iam_client.get_role(RoleName=role_name)
        role_arn = role_response['Role']['Arn']
        print(f"✅ Using existing IAM role: {role_arn}")
    
    # Create deployment package
    zip_file = create_deployment_package()
    
    # Read the zip file
    with open(zip_file, 'rb') as f:
        zip_content = f.read()
    
    try:
        # Try to create the Lambda function
        print("⚡ Creating Lambda function...")
        
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.13',
            Role=role_arn,
            Handler='app.lambda_handler',
            Code={'ZipFile': zip_content},
            Description='Hello World function for SAP Datasphere project',
            Timeout=30,
            MemorySize=128,
            Environment={
                'Variables': {
                    'ENVIRONMENT': 'production'
                }
            },
            Tags={
                'Project': 'SAP-Datasphere-Integration',
                'Environment': 'Demo',
                'Purpose': 'Hello-World'
            }
        )
        
        function_arn = response['FunctionArn']
        print(f"✅ Created Lambda function: {function_arn}")
        
    except lambda_client.exceptions.ResourceConflictException:
        # Function already exists, update it
        print("🔄 Function exists, updating code...")
        
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        
        function_arn = response['FunctionArn']
        print(f"✅ Updated Lambda function: {function_arn}")
    
    # Create Function URL for public access
    print("🌐 Creating public Function URL...")
    
    try:
        url_response = lambda_client.create_function_url_config(
            FunctionName=function_name,
            AuthType='NONE',  # Public access
            Cors={
                'AllowCredentials': False,
                'AllowHeaders': ['*'],
                'AllowMethods': ['GET', 'POST'],
                'AllowOrigins': ['*'],
                'ExposeHeaders': ['*'],
                'MaxAge': 86400
            }
        )
        
        function_url = url_response['FunctionUrl']
        print(f"✅ Created Function URL: {function_url}")
        
    except lambda_client.exceptions.ResourceConflictException:
        # URL already exists, get it
        url_response = lambda_client.get_function_url_config(FunctionName=function_name)
        function_url = url_response['FunctionUrl']
        print(f"✅ Using existing Function URL: {function_url}")
    
    # Add permission for Function URL to invoke the function
    print("🔐 Adding Function URL permission...")
    
    try:
        lambda_client.add_permission(
            FunctionName=function_name,
            StatementId='FunctionURLAllowPublicAccess',
            Action='lambda:InvokeFunctionUrl',
            Principal='*',
            FunctionUrlAuthType='NONE'
        )
        print("✅ Added Function URL permission")
        
    except lambda_client.exceptions.ResourceConflictException:
        print("✅ Function URL permission already exists")
    
    # Test the function
    print("🧪 Testing the function...")
    
    test_response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='RequestResponse',
        Payload=json.dumps({
            'requestContext': {
                'http': {
                    'method': 'GET',
                    'sourceIp': '127.0.0.1'
                }
            },
            'headers': {
                'user-agent': 'Deployment Test'
            }
        })
    )
    
    if test_response['StatusCode'] == 200:
        print("✅ Function test successful!")
    else:
        print(f"❌ Function test failed: {test_response['StatusCode']}")
    
    # Clean up deployment file
    Path(zip_file).unlink()
    
    return {
        'function_name': function_name,
        'function_arn': function_arn,
        'function_url': function_url,
        'role_arn': role_arn
    }

def main():
    """Main deployment function"""
    
    print("🚀 AWS Hello World Deployment")
    print("=" * 50)
    
    try:
        # Deploy the function
        result = deploy_lambda_function()
        
        print("\n" + "=" * 50)
        print("🎉 DEPLOYMENT SUCCESSFUL!")
        print("=" * 50)
        print(f"📍 Function Name: {result['function_name']}")
        print(f"⚡ Function ARN: {result['function_arn']}")
        print(f"🌐 Public URL: {result['function_url']}")
        print(f"🔐 IAM Role: {result['role_arn']}")
        
        print(f"\n🎯 ACCESS YOUR HELLO WORLD APP:")
        print(f"🔗 {result['function_url']}")
        
        print(f"\n📋 What you can do now:")
        print(f"  • Visit the URL above to see your Hello World app")
        print(f"  • Share the URL - it's publicly accessible")
        print(f"  • Use this as foundation for your control panel")
        print(f"  • Add FastAPI for REST APIs")
        print(f"  • Add React frontend for rich UI")
        
        return result
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()