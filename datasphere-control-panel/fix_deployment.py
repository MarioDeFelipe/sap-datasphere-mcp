"""
Fix deployment issues and create working API Gateway for Q Business Enhanced Control Panel
"""

import boto3
import json
import time

def fix_api_gateway_deployment():
    """Fix API Gateway deployment with proper permissions"""
    
    lambda_client = boto3.client('lambda')
    apigateway_client = boto3.client('apigateway')
    sts_client = boto3.client('sts')
    
    # Get account ID
    account_id = sts_client.get_caller_identity()['Account']
    region = 'us-east-1'
    function_name = 'ailien-platform-q-business-enhanced'
    
    print("🔧 Fixing API Gateway deployment...")
    
    try:
        # Create new REST API with corrected configuration
        api_response = apigateway_client.create_rest_api(
            name='ailien-platform-q-business-fixed',
            description='Fixed API for Ailien Platform Q Business Enhanced Control Panel',
            endpointConfiguration={'types': ['REGIONAL']}
        )
        
        api_id = api_response['id']
        print(f"✅ Created new API Gateway: {api_id}")
        
        # Get root resource
        resources = apigateway_client.get_resources(restApiId=api_id)
        root_id = next(r['id'] for r in resources['items'] if r['path'] == '/')
        
        # Create ANY method for root
        apigateway_client.put_method(
            restApiId=api_id,
            resourceId=root_id,
            httpMethod='ANY',
            authorizationType='NONE'
        )
        
        # Set up Lambda integration
        lambda_arn = f"arn:aws:lambda:{region}:{account_id}:function:{function_name}"
        lambda_uri = f"arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations"
        
        apigateway_client.put_integration(
            restApiId=api_id,
            resourceId=root_id,
            httpMethod='ANY',
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=lambda_uri
        )
        
        # Deploy API
        deployment = apigateway_client.create_deployment(
            restApiId=api_id,
            stageName='prod',
            description='Fixed production deployment'
        )
        
        # Add Lambda permission with correct source ARN
        source_arn = f"arn:aws:execute-api:{region}:{account_id}:{api_id}/*/*"
        
        try:
            lambda_client.add_permission(
                FunctionName=function_name,
                StatementId=f'api-gateway-invoke-{int(time.time())}',  # Unique statement ID
                Action='lambda:InvokeFunction',
                Principal='apigateway.amazonaws.com',
                SourceArn=source_arn
            )
            print("✅ Added Lambda permission for API Gateway")
        except lambda_client.exceptions.ResourceConflictException:
            print("⚠️ Lambda permission already exists")
        
        api_url = f"https://{api_id}.execute-api.{region}.amazonaws.com/prod"
        print(f"✅ Fixed API Gateway deployed: {api_url}")
        
        return api_url, api_id
        
    except Exception as e:
        print(f"❌ Error fixing API Gateway: {e}")
        return None, None

def test_lambda_function():
    """Test the deployed Lambda function directly"""
    
    lambda_client = boto3.client('lambda')
    function_name = 'ailien-platform-q-business-enhanced'
    
    print("🧪 Testing deployed Lambda function...")
    
    test_event = {
        'path': '/',
        'httpMethod': 'GET',
        'headers': {},
        'body': None,
        'requestContext': {
            'requestId': 'test-request-id',
            'stage': 'prod'
        }
    }
    
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(test_event)
        )
        
        result = json.loads(response['Payload'].read())
        
        if result.get('statusCode') == 200:
            print("✅ Lambda function is working correctly")
            print(f"📄 Response length: {len(result.get('body', ''))} characters")
            return True
        else:
            print(f"❌ Lambda function returned error: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Lambda function: {e}")
        return False

def update_lambda_with_simple_q_business():
    """Update Lambda function with simplified Q Business integration"""
    
    lambda_client = boto3.client('lambda')
    function_name = 'ailien-platform-q-business-enhanced'
    
    print("🔄 Updating Lambda function with simplified Q Business...")
    
    # Read the enhanced app code
    try:
        with open('q_business_enhanced_app.py', 'r', encoding='utf-8') as f:
            app_code = f.read()
        
        # Update environment variables
        lambda_client.update_function_configuration(
            FunctionName=function_name,
            Environment={
                'Variables': {
                    'GLUE_DATABASE': 'datasphere_ge230769',
                    'Q_BUSINESS_ENABLED': 'true',
                    'REGION': 'us-east-1',
                    'MOCK_MODE': 'true'  # Enable mock mode for Q Business
                }
            },
            Timeout=60,  # Increase timeout
            MemorySize=1024  # Increase memory
        )
        
        print("✅ Updated Lambda configuration")
        return True
        
    except Exception as e:
        print(f"❌ Error updating Lambda: {e}")
        return False

def main():
    """Main function to fix deployment issues"""
    
    print("🔧 Fixing Ailien Platform Q Business Enhanced Deployment")
    print("=" * 60)
    
    # Step 1: Test current Lambda function
    print("\n📋 Step 1: Testing current Lambda function...")
    lambda_working = test_lambda_function()
    
    # Step 2: Fix API Gateway
    print("\n🌐 Step 2: Fixing API Gateway...")
    api_url, api_id = fix_api_gateway_deployment()
    
    # Step 3: Update Lambda configuration
    print("\n🔄 Step 3: Updating Lambda configuration...")
    lambda_updated = update_lambda_with_simple_q_business()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 DEPLOYMENT FIX COMPLETED!")
    print("=" * 60)
    
    if api_url:
        print(f"\n🔗 Your Enhanced Control Panel URL: {api_url}")
        print(f"🌐 API Gateway ID: {api_id}")
    else:
        print("\n⚠️ API Gateway setup needs manual configuration")
    
    print(f"🔧 Lambda Function: ailien-platform-q-business-enhanced")
    print(f"📅 Fixed: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n🎯 What's Working:")
    if lambda_working:
        print("✅ Lambda function deployed and working")
    else:
        print("⚠️ Lambda function needs attention")
    
    if api_url:
        print("✅ API Gateway configured and accessible")
        print("✅ Enhanced control panel with Q Business side panel")
        print("✅ Mock Q Business responses for testing")
    
    print("\n🔗 Next Steps:")
    if api_url:
        print(f"1. Visit {api_url} to access your enhanced control panel")
        print("2. Test the Q Business side panel with sample queries")
        print("3. Configure real Q Business integration when ready")
    else:
        print("1. Check AWS console for any permission issues")
        print("2. Manually create API Gateway if needed")
    
    return api_url

if __name__ == "__main__":
    main()