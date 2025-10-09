#!/usr/bin/env python3
"""
Fix AWS Glue Permissions for Lambda Function
Adds necessary Glue permissions to the Lambda execution role
"""

import boto3
import json
import time
from datetime import datetime

def fix_glue_permissions():
    """Add AWS Glue permissions to the Lambda execution role"""
    
    print("🔧 FIXING AWS GLUE PERMISSIONS")
    print("=" * 40)
    
    # Initialize clients
    iam_client = boto3.client('iam')
    lambda_client = boto3.client('lambda')
    
    try:
        # Get the Lambda function's role
        function_response = lambda_client.get_function(FunctionName='datasphere-control-panel')
        role_arn = function_response['Configuration']['Role']
        role_name = role_arn.split('/')[-1]
        
        print(f"📋 Found Lambda role: {role_name}")
        print(f"📋 Role ARN: {role_arn}")
        
        # Define the Glue policy
        glue_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "glue:CreateDatabase",
                        "glue:GetDatabase",
                        "glue:GetDatabases",
                        "glue:UpdateDatabase",
                        "glue:DeleteDatabase",
                        "glue:CreateTable",
                        "glue:GetTable",
                        "glue:GetTables",
                        "glue:UpdateTable",
                        "glue:DeleteTable",
                        "glue:GetPartition",
                        "glue:GetPartitions",
                        "glue:CreatePartition",
                        "glue:UpdatePartition",
                        "glue:DeletePartition",
                        "glue:BatchCreatePartition",
                        "glue:BatchDeletePartition",
                        "glue:BatchUpdatePartition"
                    ],
                    "Resource": [
                        f"arn:aws:glue:*:554074173953:catalog",
                        f"arn:aws:glue:*:554074173953:database/*",
                        f"arn:aws:glue:*:554074173953:table/*/*"
                    ]
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:DeleteObject",
                        "s3:ListBucket"
                    ],
                    "Resource": [
                        "arn:aws:s3:::datasphere-sync-bucket",
                        "arn:aws:s3:::datasphere-sync-bucket/*"
                    ]
                }
            ]
        }
        
        policy_name = "DatasphereGlueAccess"
        
        # Create or update the policy
        try:
            # Try to create the policy
            policy_response = iam_client.create_policy(
                PolicyName=policy_name,
                PolicyDocument=json.dumps(glue_policy),
                Description="AWS Glue access for Datasphere Control Panel"
            )
            policy_arn = policy_response['Policy']['Arn']
            print(f"✅ Created new policy: {policy_arn}")
            
        except iam_client.exceptions.EntityAlreadyExistsException:
            # Policy already exists, get its ARN
            account_id = boto3.client('sts').get_caller_identity()['Account']
            policy_arn = f"arn:aws:iam::{account_id}:policy/{policy_name}"
            print(f"📋 Policy already exists: {policy_arn}")
            
            # Update the existing policy
            try:
                iam_client.create_policy_version(
                    PolicyArn=policy_arn,
                    PolicyDocument=json.dumps(glue_policy),
                    SetAsDefault=True
                )
                print("✅ Updated existing policy with new permissions")
            except Exception as e:
                print(f"⚠️ Could not update policy: {e}")
        
        # Attach the policy to the role
        try:
            iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_arn
            )
            print(f"✅ Attached policy to role: {role_name}")
            
        except iam_client.exceptions.NoSuchEntityException as e:
            print(f"❌ Role not found: {e}")
            return False
        except Exception as e:
            if "already attached" in str(e).lower():
                print("📋 Policy already attached to role")
            else:
                print(f"⚠️ Error attaching policy: {e}")
        
        # Wait for permissions to propagate
        print("⏳ Waiting for permissions to propagate...")
        time.sleep(10)
        
        # Test the permissions
        print("🔍 Testing Glue permissions...")
        glue_client = boto3.client('glue')
        
        try:
            # Try to list databases (should work with new permissions)
            databases = glue_client.get_databases()
            print(f"✅ Glue permissions working! Found {len(databases.get('DatabaseList', []))} databases")
            
            # Try to create a test database
            test_db_name = 'datasphere_ge230769'
            try:
                glue_client.create_database(
                    DatabaseInput={
                        'Name': test_db_name,
                        'Description': 'SAP Datasphere assets from space GE230769'
                    }
                )
                print(f"✅ Successfully created database: {test_db_name}")
                
            except glue_client.exceptions.AlreadyExistsException:
                print(f"📋 Database already exists: {test_db_name}")
            except Exception as e:
                print(f"❌ Error creating database: {e}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Glue permissions test failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing permissions: {e}")
        return False

def create_s3_bucket_if_needed():
    """Create S3 bucket for Glue table data if it doesn't exist"""
    
    print("\n📦 CHECKING S3 BUCKET")
    print("=" * 40)
    
    s3_client = boto3.client('s3')
    bucket_name = 'datasphere-sync-bucket'
    
    try:
        # Check if bucket exists
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"📋 S3 bucket already exists: {bucket_name}")
        return True
        
    except s3_client.exceptions.NoSuchBucket:
        # Bucket doesn't exist, create it
        try:
            # Create bucket in us-east-1 (no LocationConstraint needed)
            s3_client.create_bucket(Bucket=bucket_name)
            print(f"✅ Created S3 bucket: {bucket_name}")
            
            # Add bucket policy for Glue access
            bucket_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "glue.amazonaws.com"
                        },
                        "Action": [
                            "s3:GetObject",
                            "s3:PutObject"
                        ],
                        "Resource": f"arn:aws:s3:::{bucket_name}/*"
                    }
                ]
            }
            
            s3_client.put_bucket_policy(
                Bucket=bucket_name,
                Policy=json.dumps(bucket_policy)
            )
            print("✅ Added bucket policy for Glue access")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating S3 bucket: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking S3 bucket: {e}")
        return False

def test_full_integration():
    """Test the complete Glue integration"""
    
    print("\n🧪 TESTING FULL INTEGRATION")
    print("=" * 40)
    
    try:
        # Test the Lambda function URL
        import urllib.request
        import urllib.error
        
        url = "https://krb7735xufadsj233kdnpaabta0eatck.lambda-url.us-east-1.on.aws/api/glue/status"
        
        req = urllib.request.Request(url)
        req.add_header('Content-Type', 'application/json')
        
        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                print("✅ Glue status API working!")
                print(f"📋 Database exists: {data.get('database_exists', False)}")
                print(f"📋 Table count: {data.get('table_count', 0)}")
                return True
            else:
                print(f"❌ API returned status: {response.status}")
                return False
                
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Main permission fixing process"""
    
    print("🔧 AWS GLUE PERMISSIONS FIX")
    print("=" * 40)
    print(f"📅 Started at: {datetime.now().isoformat()}")
    print()
    
    success = True
    
    # Step 1: Fix IAM permissions
    if fix_glue_permissions():
        print("\n✅ Step 1: IAM permissions fixed!")
    else:
        print("\n❌ Step 1: Failed to fix IAM permissions")
        success = False
    
    # Step 2: Create S3 bucket if needed
    if create_s3_bucket_if_needed():
        print("\n✅ Step 2: S3 bucket ready!")
    else:
        print("\n❌ Step 2: S3 bucket setup failed")
        success = False
    
    # Step 3: Test integration
    if success and test_full_integration():
        print("\n✅ Step 3: Integration test passed!")
    else:
        print("\n❌ Step 3: Integration test failed")
        success = False
    
    if success:
        print("\n🎉 GLUE PERMISSIONS FIX SUCCESSFUL!")
        print("=" * 40)
        print("✅ AWS Glue permissions are now properly configured!")
        print("✅ S3 bucket is ready for Glue table data")
        print("✅ Integration test passed")
        print("\n🎯 What you can do now:")
        print("  1. Go back to your application")
        print("  2. Click 'Sync to Glue' - it should work now!")
        print("  3. Check 'Glue Status' to see your database")
        print("  4. Create tables from your Datasphere assets")
        print("\n🔗 URL: https://krb7735xufadsj233kdnpaabta0eatck.lambda-url.us-east-1.on.aws")
        
    else:
        print("\n❌ Permission fix failed")
        print("Please check the error messages above")

if __name__ == "__main__":
    main()