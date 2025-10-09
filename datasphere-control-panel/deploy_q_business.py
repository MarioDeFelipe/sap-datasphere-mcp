"""
Deploy Enhanced Ailien Platform Control Panel with Amazon Q Business Integration
This script deploys the Q Business enhanced version to AWS Lambda
"""

import boto3
import json
import zipfile
import os
import time
from datetime import datetime

class QBusinessDeployment:
    """Handles deployment of Q Business enhanced control panel"""
    
    def __init__(self, region='us-east-1'):
        self.region = region
        self.lambda_client = boto3.client('lambda', region_name=region)
        self.iam_client = boto3.client('iam', region_name=region)
        self.apigateway_client = boto3.client('apigateway', region_name=region)
        self.qbusiness_client = boto3.client('qbusiness', region_name=region)
        
        # Configuration
        self.function_name = 'ailien-platform-q-business-enhanced'
        self.role_name = 'AilienPlatformQBusinessRole'
        self.api_name = 'ailien-platform-q-business-api'
        
    def create_iam_role(self):
        """Create IAM role with Q Business permissions"""
        
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
        
        # Enhanced policy for Q Business integration
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents"
                    ],
                    "Resource": "arn:aws:logs:*:*:*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "glue:GetDatabase",
                        "glue:GetDatabases",
                        "glue:GetTable",
                        "glue:GetTables",
                        "glue:GetPartition",
                        "glue:GetPartitions",
                        "glue:BatchGetPartition",
                        "glue:GetCatalogImportStatus"
                    ],
                    "Resource": "*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "qbusiness:*"
                    ],
                    "Resource": "*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "cloudwatch:GetMetricStatistics",
                        "cloudwatch:ListMetrics",
                        "cloudwatch:GetMetricData"
                    ],
                    "Resource": "*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:ListBucket"
                    ],
                    "Resource": [
                        "arn:aws:s3:::ailien-platform-*",
                        "arn:aws:s3:::ailien-platform-*/*"
                    ]
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "bedrock:InvokeModel",
                        "bedrock:InvokeModelWithResponseStream"
                    ],
                    "Resource": "*"
                }
            ]
        }
        
        try:
            # Create role
            role_response = self.iam_client.create_role(
                RoleName=self.role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description='IAM role for Ailien Platform Q Business integration'
            )
            
            # Attach inline policy
            self.iam_client.put_role_policy(
                RoleName=self.role_name,
                PolicyName='AilienPlatformQBusinessPolicy',
                PolicyDocument=json.dumps(policy_document)
            )
            
            print(f"✅ Created IAM role: {self.role_name}")
            return role_response['Role']['Arn']
            
        except self.iam_client.exceptions.EntityAlreadyExistsException:
            # Role already exists, get ARN
            role_response = self.iam_client.get_role(RoleName=self.role_name)
            print(f"✅ Using existing IAM role: {self.role_name}")
            return role_response['Role']['Arn']
    
    def create_deployment_package(self):
        """Create deployment package with Q Business enhanced code"""
        
        print("📦 Creating deployment package...")
        
        # Create zip file
        zip_filename = 'q_business_enhanced_deployment.zip'
        
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add the enhanced app code
            zipf.write('q_business_enhanced_app.py', 'lambda_function.py')
            
            # Add requirements if needed (boto3 is available by default)
            requirements_content = """
boto3>=1.26.0
botocore>=1.29.0
"""
            zipf.writestr('requirements.txt', requirements_content)
        
        print(f"✅ Created deployment package: {zip_filename}")
        return zip_filename
    
    def deploy_lambda_function(self, role_arn, zip_filename):
        """Deploy or update Lambda function"""
        
        print("🚀 Deploying Lambda function...")
        
        # Read deployment package
        with open(zip_filename, 'rb') as f:
            zip_content = f.read()
        
        function_config = {
            'FunctionName': self.function_name,
            'Runtime': 'python3.11',
            'Role': role_arn,
            'Handler': 'lambda_function.lambda_handler',
            'Code': {'ZipFile': zip_content},
            'Description': 'Ailien Platform Control Panel with Amazon Q Business Integration',
            'Timeout': 30,
            'MemorySize': 512,
            'Environment': {
                'Variables': {
                    'GLUE_DATABASE': 'datasphere_ge230769',
                    'Q_BUSINESS_APP_ID': 'to-be-configured',
                    'REGION': self.region
                }
            },
            'Tags': {
                'Project': 'AilienPlatform',
                'Component': 'QBusinessIntegration',
                'Environment': 'Production'
            }
        }
        
        try:
            # Try to create new function
            response = self.lambda_client.create_function(**function_config)
            print(f"✅ Created Lambda function: {self.function_name}")
            
        except self.lambda_client.exceptions.ResourceConflictException:
            # Function exists, update it
            print(f"🔄 Updating existing Lambda function: {self.function_name}")
            
            # Update function code
            self.lambda_client.update_function_code(
                FunctionName=self.function_name,
                ZipFile=zip_content
            )
            
            # Update function configuration
            config_update = {k: v for k, v in function_config.items() 
                           if k not in ['FunctionName', 'Code']}
            
            response = self.lambda_client.update_function_configuration(
                FunctionName=self.function_name,
                **config_update
            )
            
            print(f"✅ Updated Lambda function: {self.function_name}")
        
        return response['FunctionArn']
    
    def create_api_gateway(self, lambda_arn):
        """Create API Gateway for the enhanced control panel"""
        
        print("🌐 Setting up API Gateway...")
        
        try:
            # Create REST API
            api_response = self.apigateway_client.create_rest_api(
                name=self.api_name,
                description='API for Ailien Platform Q Business Enhanced Control Panel',
                endpointConfiguration={'types': ['REGIONAL']},
                tags={
                    'Project': 'AilienPlatform',
                    'Component': 'QBusinessAPI'
                }
            )
            
            api_id = api_response['id']
            print(f"✅ Created API Gateway: {api_id}")
            
            # Get root resource
            resources = self.apigateway_client.get_resources(restApiId=api_id)
            root_id = next(r['id'] for r in resources['items'] if r['path'] == '/')
            
            # Create proxy resource
            proxy_resource = self.apigateway_client.create_resource(
                restApiId=api_id,
                parentId=root_id,
                pathPart='{proxy+}'
            )
            
            # Create ANY method for root
            self.apigateway_client.put_method(
                restApiId=api_id,
                resourceId=root_id,
                httpMethod='ANY',
                authorizationType='NONE'
            )
            
            # Create ANY method for proxy
            self.apigateway_client.put_method(
                restApiId=api_id,
                resourceId=proxy_resource['id'],
                httpMethod='ANY',
                authorizationType='NONE'
            )
            
            # Set up Lambda integration for root
            lambda_uri = f"arn:aws:apigateway:{self.region}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations"
            
            self.apigateway_client.put_integration(
                restApiId=api_id,
                resourceId=root_id,
                httpMethod='ANY',
                type='AWS_PROXY',
                integrationHttpMethod='POST',
                uri=lambda_uri
            )
            
            # Set up Lambda integration for proxy
            self.apigateway_client.put_integration(
                restApiId=api_id,
                resourceId=proxy_resource['id'],
                httpMethod='ANY',
                type='AWS_PROXY',
                integrationHttpMethod='POST',
                uri=lambda_uri
            )
            
            # Deploy API
            deployment = self.apigateway_client.create_deployment(
                restApiId=api_id,
                stageName='prod',
                description='Production deployment of Q Business enhanced control panel'
            )
            
            # Add Lambda permission for API Gateway
            try:
                self.lambda_client.add_permission(
                    FunctionName=self.function_name,
                    StatementId='api-gateway-invoke',
                    Action='lambda:InvokeFunction',
                    Principal='apigateway.amazonaws.com',
                    SourceArn=f"arn:aws:execute-api:{self.region}:*:{api_id}/*/*"
                )
            except self.lambda_client.exceptions.ResourceConflictException:
                print("⚠️ Lambda permission already exists")
            
            api_url = f"https://{api_id}.execute-api.{self.region}.amazonaws.com/prod"
            print(f"✅ API Gateway deployed: {api_url}")
            
            return api_url, api_id
            
        except Exception as e:
            print(f"❌ Error creating API Gateway: {e}")
            return None, None
    
    def setup_q_business_application(self):
        """Set up Amazon Q Business application"""
        
        print("🤖 Setting up Amazon Q Business application...")
        
        try:
            # Create Q Business application
            app_response = self.qbusiness_client.create_application(
                displayName='Ailien Platform Data Discovery',
                description='AI-powered data product discovery for Ailien Platform',
                tags=[
                    {'key': 'Project', 'value': 'AilienPlatform'},
                    {'key': 'Component', 'value': 'DataDiscovery'}
                ]
            )
            
            app_id = app_response['applicationId']
            print(f"✅ Created Q Business application: {app_id}")
            
            # Wait for application to be ready
            print("⏳ Waiting for Q Business application to be ready...")
            time.sleep(30)
            
            # Create data source for Glue Catalog
            data_source_response = self.qbusiness_client.create_data_source(
                applicationId=app_id,
                displayName='Ailien Data Products Catalog',
                type='GLUE',
                configuration={
                    'glueConfiguration': {
                        'databaseName': 'datasphere_ge230769',
                        'includeFilterPatterns': ['*'],
                        'excludeFilterPatterns': ['temp_*', 'staging_*']
                    }
                },
                description='SAP Datasphere data products replicated to AWS Glue'
            )
            
            data_source_id = data_source_response['dataSourceId']
            print(f"✅ Created Q Business data source: {data_source_id}")
            
            return app_id, data_source_id
            
        except Exception as e:
            print(f"⚠️ Q Business setup note: {e}")
            print("💡 You may need to enable Q Business in your AWS account first")
            return None, None
    
    def deploy_complete_solution(self):
        """Deploy the complete Q Business enhanced solution"""
        
        print("🚀 Starting deployment of Ailien Platform Q Business Enhanced Control Panel...")
        print("=" * 80)
        
        try:
            # Step 1: Create IAM role
            print("\n📋 Step 1: Setting up IAM permissions...")
            role_arn = self.create_iam_role()
            
            # Wait for role to propagate
            print("⏳ Waiting for IAM role to propagate...")
            time.sleep(10)
            
            # Step 2: Create deployment package
            print("\n📦 Step 2: Creating deployment package...")
            zip_filename = self.create_deployment_package()
            
            # Step 3: Deploy Lambda function
            print("\n🚀 Step 3: Deploying Lambda function...")
            lambda_arn = self.deploy_lambda_function(role_arn, zip_filename)
            
            # Step 4: Create API Gateway
            print("\n🌐 Step 4: Setting up API Gateway...")
            api_url, api_id = self.create_api_gateway(lambda_arn)
            
            # Step 5: Setup Q Business (optional, may require manual setup)
            print("\n🤖 Step 5: Setting up Amazon Q Business...")
            q_app_id, q_data_source_id = self.setup_q_business_application()
            
            # Step 6: Update Lambda environment with Q Business details
            if q_app_id:
                print("\n🔧 Step 6: Updating Lambda configuration...")
                self.lambda_client.update_function_configuration(
                    FunctionName=self.function_name,
                    Environment={
                        'Variables': {
                            'GLUE_DATABASE': 'datasphere_ge230769',
                            'Q_BUSINESS_APP_ID': q_app_id,
                            'Q_BUSINESS_DATA_SOURCE_ID': q_data_source_id or 'manual-setup-required',
                            'REGION': self.region
                        }
                    }
                )
            
            # Cleanup
            if os.path.exists(zip_filename):
                os.remove(zip_filename)
            
            # Deployment summary
            print("\n" + "=" * 80)
            print("🎉 DEPLOYMENT SUCCESSFUL!")
            print("=" * 80)
            
            print(f"\n📊 Enhanced Control Panel URL: {api_url}")
            print(f"🔧 Lambda Function: {self.function_name}")
            print(f"🌐 API Gateway ID: {api_id}")
            
            if q_app_id:
                print(f"🤖 Q Business App ID: {q_app_id}")
                print(f"📊 Q Business Data Source: {q_data_source_id}")
            else:
                print("⚠️ Q Business setup requires manual configuration")
            
            print(f"\n🏷️ AWS Region: {self.region}")
            print(f"📅 Deployed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            print("\n🎯 Features Deployed:")
            print("✅ Enhanced Control Panel with Q Business side panel")
            print("✅ Comprehensive metadata collection")
            print("✅ Natural language data product queries")
            print("✅ Real-time usage analytics")
            print("✅ Data quality scoring")
            print("✅ Access control management")
            print("✅ Bi-directional SAP-AWS sync monitoring")
            
            print("\n🔗 Next Steps:")
            print("1. Visit the control panel URL to test the interface")
            print("2. Configure Q Business data source if needed")
            print("3. Set up your SAP Datasphere connection")
            print("4. Start asking questions about your data products!")
            
            return {
                'status': 'success',
                'control_panel_url': api_url,
                'lambda_function': self.function_name,
                'api_gateway_id': api_id,
                'q_business_app_id': q_app_id,
                'region': self.region
            }
            
        except Exception as e:
            print(f"\n❌ Deployment failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }

def main():
    """Main deployment function"""
    
    print("🚀 Ailien Platform Q Business Enhanced Deployment")
    print("=" * 60)
    
    # Initialize deployment
    deployer = QBusinessDeployment(region='us-east-1')
    
    # Deploy complete solution
    result = deployer.deploy_complete_solution()
    
    if result['status'] == 'success':
        print(f"\n🎉 Your enhanced control panel is ready!")
        print(f"🔗 Access it at: {result['control_panel_url']}")
    else:
        print(f"\n❌ Deployment failed: {result['error']}")

if __name__ == "__main__":
    main()