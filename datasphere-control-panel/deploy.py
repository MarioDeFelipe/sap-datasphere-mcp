#!/usr/bin/env python3
"""
Deploy SAP Datasphere Control Panel to AWS Lambda
"""

import json
import zipfile
import boto3
import time
import subprocess
import sys
from pathlib import Path

def install_dependencies():
    """Install dependencies to a local directory"""
    
    print("📦 Installing dependencies...")
    
    # Create a temporary directory for dependencies
    deps_dir = Path("dependencies")
    if deps_dir.exists():
        import shutil
        shutil.rmtree(deps_dir)
    
    deps_dir.mkdir()
    
    # Install dependencies
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "-r", "requirements.txt",
        "-t", str(deps_dir),
        "--no-deps"  # Don't install sub-dependencies to keep size small
    ])
    
    # Install core dependencies manually
    core_deps = [
        "fastapi==0.104.1",
        "mangum==0.17.0", 
        "requests==2.31.0",
        "boto3==1.34.0",
        "pydantic==2.5.0",
        "starlette==0.27.0",
        "typing-extensions==4.8.0"
    ]
    
    for dep in core_deps:
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                dep,
                "-t", str(deps_dir),
                "--upgrade",
                "--no-deps"
            ])
        except subprocess.CalledProcessError:
            print(f"⚠️ Warning: Could not install {dep}")
    
    print("✅ Dependencies installed")
    return deps_dir

def create_deployment_package():
    """Create a deployment package for Lambda"""
    
    print("📦 Creating deployment package...")
    
    # Install dependencies
    deps_dir = install_dependencies()
    
    # Create zip file
    zip_path = "control-panel-lambda.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add main application
        zipf.write('app.py', 'app.py')
        
        # Add dependencies
        for file_path in deps_dir.rglob('*'):
            if file_path.is_file():
                # Calculate relative path from deps_dir
                rel_path = file_path.relative_to(deps_dir)
                zipf.write(file_path, str(rel_path))
    
    # Clean up
    import shutil
    shutil.rmtree(deps_dir)
    
    print(f"✅ Deployment package created: {zip_path}")
    return zip_path

def deploy_control_panel():
    """Deploy the control panel to AWS Lambda"""
    
    print("🚀 Deploying SAP Datasphere Control Panel...")
    
    # Initialize AWS clients
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    iam_client = boto3.client('iam', region_name='us-east-1')
    
    function_name = 'datasphere-control-panel'
    
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
    
    # IAM policy for Glue access
    glue_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "glue:GetDatabase",
                    "glue:GetDatabases", 
                    "glue:GetTable",
                    "glue:GetTables",
                    "glue:CreateTable",
                    "glue:UpdateTable",
                    "glue:DeleteTable"
                ],
                "Resource": "*"
            }
        ]
    }
    
    role_name = f"{function_name}-role"
    
    try:
        # Try to create the role
        role_response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for Datasphere Control Panel Lambda function'
        )
        role_arn = role_response['Role']['Arn']
        print(f"✅ Created IAM role: {role_arn}")
        
        # Attach basic execution policy
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        
        # Create and attach Glue policy
        policy_name = f"{function_name}-glue-policy"
        try:
            policy_response = iam_client.create_policy(
                PolicyName=policy_name,
                PolicyDocument=json.dumps(glue_policy),
                Description='Policy for Glue access'
            )
            
            iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_response['Policy']['Arn']
            )
            print("✅ Created and attached Glue policy")
            
        except iam_client.exceptions.EntityAlreadyExistsException:
            # Policy exists, attach it
            account_id = boto3.client('sts').get_caller_identity()['Account']
            policy_arn = f"arn:aws:iam::{account_id}:policy/{policy_name}"
            iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_arn
            )
            print("✅ Attached existing Glue policy")
        
        # Wait for role to be available
        print("⏳ Waiting for IAM role to be available...")
        time.sleep(15)
        
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
    
    print(f"📊 Package size: {len(zip_content) / 1024 / 1024:.1f} MB")
    
    try:
        # Try to create the Lambda function
        print("⚡ Creating Lambda function...")
        
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.13',
            Role=role_arn,
            Handler='app.handler',
            Code={'ZipFile': zip_content},
            Description='SAP Datasphere Control Panel - FastAPI application',
            Timeout=30,
            MemorySize=512,  # More memory for FastAPI
            Environment={
                'Variables': {
                    'ENVIRONMENT': 'production'
                }
            },
            Tags={
                'Project': 'SAP-Datasphere-Integration',
                'Environment': 'Production',
                'Purpose': 'Control-Panel'
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
        
        # Update configuration
        lambda_client.update_function_configuration(
            FunctionName=function_name,
            Timeout=30,
            MemorySize=512
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
                'AllowMethods': ['GET', 'POST', 'PUT', 'DELETE'],
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
    
    # Add permission for Function URL
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
            'httpMethod': 'GET',
            'path': '/api/status',
            'headers': {},
            'body': None
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
    
    print("🚀 SAP Datasphere Control Panel Deployment")
    print("=" * 60)
    
    try:
        # Deploy the function
        result = deploy_control_panel()
        
        print("\n" + "=" * 60)
        print("🎉 DEPLOYMENT SUCCESSFUL!")
        print("=" * 60)
        print(f"📍 Function Name: {result['function_name']}")
        print(f"⚡ Function ARN: {result['function_arn']}")
        print(f"🌐 Control Panel URL: {result['function_url']}")
        print(f"🔐 IAM Role: {result['role_arn']}")
        
        print(f"\n🎯 ACCESS YOUR CONTROL PANEL:")
        print(f"🔗 {result['function_url']}")
        
        print(f"\n📋 Available Endpoints:")
        print(f"  • Dashboard: {result['function_url']}")
        print(f"  • Assets API: {result['function_url']}api/assets")
        print(f"  • Sync API: {result['function_url']}api/sync")
        print(f"  • Status API: {result['function_url']}api/status")
        
        print(f"\n🎯 What you can do now:")
        print(f"  • Open the control panel in your browser")
        print(f"  • Discover your Datasphere assets")
        print(f"  • Sync assets to AWS Glue")
        print(f"  • Preview data from your assets")
        print(f"  • Monitor system status")
        
        return result
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()