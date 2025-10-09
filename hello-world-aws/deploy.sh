#!/bin/bash

# Deploy Hello World Lambda Function to AWS
echo "🚀 Deploying Hello World to AWS Lambda..."

# Function configuration
FUNCTION_NAME="hello-world-datasphere"
ROLE_NAME="${FUNCTION_NAME}-role"
REGION="us-east-1"

# Create deployment package
echo "📦 Creating deployment package..."
zip -q hello-world-lambda.zip app.py
echo "✅ Created hello-world-lambda.zip"

# Create IAM role (if it doesn't exist)
echo "🔐 Setting up IAM role..."

# Trust policy for Lambda
cat > trust-policy.json << EOF
{
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
EOF

# Create role (ignore error if exists)
aws iam create-role \
    --role-name $ROLE_NAME \
    --assume-role-policy-document file://trust-policy.json \
    --description "Role for Hello World Lambda function" \
    --region $REGION 2>/dev/null || echo "Role already exists"

# Attach basic execution policy
aws iam attach-role-policy \
    --role-name $ROLE_NAME \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole \
    --region $REGION 2>/dev/null || echo "Policy already attached"

# Get role ARN
ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text --region $REGION)
echo "✅ Using IAM role: $ROLE_ARN"

# Wait for role to be available
echo "⏳ Waiting for IAM role to be available..."
sleep 10

# Create or update Lambda function
echo "⚡ Deploying Lambda function..."

# Try to create function
aws lambda create-function \
    --function-name $FUNCTION_NAME \
    --runtime python3.13 \
    --role $ROLE_ARN \
    --handler app.lambda_handler \
    --zip-file fileb://hello-world-lambda.zip \
    --description "Hello World function for SAP Datasphere project" \
    --timeout 30 \
    --memory-size 128 \
    --environment Variables='{ENVIRONMENT=production}' \
    --tags Project=SAP-Datasphere-Integration,Environment=Demo,Purpose=Hello-World \
    --region $REGION 2>/dev/null

# If creation failed (function exists), update it
if [ $? -ne 0 ]; then
    echo "🔄 Function exists, updating code..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://hello-world-lambda.zip \
        --region $REGION
fi

echo "✅ Lambda function deployed"

# Create Function URL for public access
echo "🌐 Creating public Function URL..."

# Create Function URL (ignore error if exists)
aws lambda create-function-url-config \
    --function-name $FUNCTION_NAME \
    --config AuthType=NONE \
    --cors AllowCredentials=false,AllowHeaders="*",AllowMethods="GET,POST",AllowOrigins="*",ExposeHeaders="*",MaxAge=86400 \
    --region $REGION 2>/dev/null || echo "Function URL already exists"

# Get Function URL
FUNCTION_URL=$(aws lambda get-function-url-config \
    --function-name $FUNCTION_NAME \
    --query 'FunctionUrl' \
    --output text \
    --region $REGION)

# Test the function
echo "🧪 Testing the function..."
aws lambda invoke \
    --function-name $FUNCTION_NAME \
    --payload '{"requestContext":{"http":{"method":"GET","sourceIp":"127.0.0.1"}},"headers":{"user-agent":"Deployment Test"}}' \
    --region $REGION \
    test-response.json > /dev/null

if [ $? -eq 0 ]; then
    echo "✅ Function test successful!"
else
    echo "❌ Function test failed"
fi

# Clean up
rm -f hello-world-lambda.zip trust-policy.json test-response.json

# Display results
echo ""
echo "=================================================="
echo "🎉 DEPLOYMENT SUCCESSFUL!"
echo "=================================================="
echo "📍 Function Name: $FUNCTION_NAME"
echo "🌐 Public URL: $FUNCTION_URL"
echo "🔐 IAM Role: $ROLE_ARN"
echo ""
echo "🎯 ACCESS YOUR HELLO WORLD APP:"
echo "🔗 $FUNCTION_URL"
echo ""
echo "📋 What you can do now:"
echo "  • Visit the URL above to see your Hello World app"
echo "  • Share the URL - it's publicly accessible"
echo "  • Use this as foundation for your control panel"
echo "  • Add FastAPI for REST APIs"
echo "  • Add React frontend for rich UI"
echo ""