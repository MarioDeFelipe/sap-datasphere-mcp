# 🚀 SAP Datasphere MCP Server - Deployment Guide

Complete deployment guide for the SAP Datasphere MCP Server & AWS Integration Platform across all environments.

## 🎯 Deployment Overview

The platform supports three deployment environments:
- **🐕 Dog Environment**: Development with hot-reload and debugging
- **🐺 Wolf Environment**: Testing with production-like settings
- **🐻 Bear Environment**: Production serverless deployment on AWS Lambda

## 📋 Prerequisites

### Required Software
```bash
# Core requirements
Python 3.10+
Git
AWS CLI configured
SAP BTP account access

# Optional for AI integration
Claude Desktop
Cursor IDE
VS Code with MCP extension
```

### Required Accounts & Permissions
- **SAP BTP Account** with OAuth application creation rights
- **SAP Datasphere** with space access permissions
- **AWS Account** with the following services:
  - AWS Lambda (for Bear environment)
  - AWS Glue (for data replication)
  - AWS S3 Tables (for Apache Iceberg storage)
  - AWS Secrets Manager (for credential storage)
  - AWS IAM (for role management)

## 🔧 Initial Setup

### 1. Repository Setup
```bash
# Clone the repository
git clone https://github.com/MarioDeFelipe/sap-datasphere-mcp.git
cd sap-datasphere-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. SAP OAuth Configuration

#### Create OAuth Application in SAP BTP
1. **Access SAP BTP Cockpit**
   - Navigate to your subaccount
   - Go to Security → OAuth

2. **Create OAuth 2.0 Client**
   - Click "Create"
   - Set Name: "SAP Datasphere MCP Server"
   - Set Grant Types: "Authorization Code"

3. **Configure Redirect URIs**
   ```
   http://localhost:8080/callback  (Dog environment)
   http://localhost:5000/callback  (Wolf environment)
   https://your-production-domain/callback  (Bear environment)
   ```

4. **Note Credentials**
   - Client ID (format: `sb-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx!bxxxxxx|client!bxxxx`)
   - Client Secret (format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx$...`)

### 3. AWS Setup

#### Create IAM Role for Glue ETL
```bash
# Create IAM role for Glue jobs
aws iam create-role \
  --role-name GlueServiceRole-SAP-Replication \
  --assume-role-policy-document file://glue-trust-policy.json

# Attach required policies
aws iam attach-role-policy \
  --role-name GlueServiceRole-SAP-Replication \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole

aws iam attach-role-policy \
  --role-name GlueServiceRole-SAP-Replication \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```

#### Create S3 Tables Bucket
```bash
# Create S3 Tables bucket for Apache Iceberg
aws s3tables create-table-bucket \
  --name sap-datasphere-s3-tables \
  --region us-east-1
```

#### Store SAP Credentials in Secrets Manager
```bash
# Create secret for SAP credentials
aws secretsmanager create-secret \
  --name sap-datasphere-credentials \
  --description "SAP Datasphere OAuth credentials" \
  --secret-string '{
    "client_id": "your_oauth_client_id",
    "client_secret": "your_oauth_client_secret",
    "base_url": "https://your-tenant.eu20.hcs.cloud.sap",
    "token_url": "https://your-tenant.authentication.eu20.hana.ondemand.com/oauth/token"
  }'
```

## 🐕 Dog Environment Deployment (Development)

### Configuration
```bash
# Configure Dog environment
python mcp_server_config.py --environment dog

# Set environment variables
export MCP_ENVIRONMENT=dog
export SAP_CLIENT_ID="your_oauth_client_id"
export SAP_CLIENT_SECRET="your_oauth_client_secret"
export AWS_REGION="us-east-1"
```

### Start Services
```bash
# Start MCP server for AI integration
python start_mcp_server.py --environment dog

# In another terminal, start web dashboard
python web_dashboard.py
```

### Validate Deployment
```bash
# Test MCP server
python test_mcp_server.py --environment dog

# Test web dashboard
curl http://localhost:8001/api/status

# Test OAuth flow
python test_oauth_authorization_code_flow.py
```

### AI Assistant Integration
Add to Claude Desktop configuration:
```json
{
  "mcpServers": {
    "sap-datasphere": {
      "command": "python",
      "args": ["/path/to/sap-datasphere-mcp/start_mcp_server.py", "--environment", "dog"],
      "env": {
        "SAP_CLIENT_ID": "your_oauth_client_id",
        "SAP_CLIENT_SECRET": "your_oauth_client_secret"
      }
    }
  }
}
```

## 🐺 Wolf Environment Deployment (Testing)

### Configuration
```bash
# Configure Wolf environment
python mcp_server_config.py --environment wolf

# Update configuration for testing
python -c "
from mcp_server_config import MCPConfigManager
config = MCPConfigManager()
config.update_environment_config('wolf', {
    'enable_performance_monitoring': True,
    'log_level': 'INFO',
    'cache_ttl_seconds': 600
})
"
```

### Start Services
```bash
# Start Wolf environment
python start_mcp_server.py --environment wolf

# Start web dashboard on Wolf port
python web_dashboard.py --port 5000 --environment wolf
```

### Performance Testing
```bash
# Run load tests
python test_performance_load.py --environment wolf

# Monitor performance
python monitor_mcp_performance.py --environment wolf

# Validate with production data
python test_real_datasphere.py --environment wolf
```

## 🐻 Bear Environment Deployment (Production)

### AWS Lambda Deployment

#### 1. Prepare Deployment Package
```bash
# Create deployment directory
mkdir lambda-deployment
cd lambda-deployment

# Copy source files
cp -r ../src/* .
cp ../requirements.txt .

# Install dependencies for Lambda
pip install -r requirements.txt -t .

# Create deployment package
zip -r sap-datasphere-mcp-lambda.zip .
```

#### 2. Create Lambda Function
```bash
# Create Lambda function
aws lambda create-function \
  --function-name sap-datasphere-mcp-server \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-execution-role \
  --handler lambda_handler.handler \
  --zip-file fileb://sap-datasphere-mcp-lambda.zip \
  --timeout 900 \
  --memory-size 1024

# Create function URL for public access
aws lambda create-function-url-config \
  --function-name sap-datasphere-mcp-server \
  --auth-type NONE \
  --cors '{
    "AllowCredentials": false,
    "AllowHeaders": ["*"],
    "AllowMethods": ["*"],
    "AllowOrigins": ["*"],
    "ExposeHeaders": ["*"],
    "MaxAge": 86400
  }'
```

#### 3. Configure Environment Variables
```bash
# Set Lambda environment variables
aws lambda update-function-configuration \
  --function-name sap-datasphere-mcp-server \
  --environment Variables='{
    "MCP_ENVIRONMENT": "bear",
    "AWS_REGION": "us-east-1",
    "SAP_CREDENTIALS_SECRET": "sap-datasphere-credentials"
  }'
```

### CloudFormation Deployment (Recommended)
```bash
# Deploy using CloudFormation template
aws cloudformation deploy \
  --template-file cloudformation/bear-environment.yaml \
  --stack-name sap-datasphere-mcp-production \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    SAPCredentialsSecret=sap-datasphere-credentials \
    S3TablesBucket=sap-datasphere-s3-tables
```

### Validate Production Deployment
```bash
# Test Lambda function
aws lambda invoke \
  --function-name sap-datasphere-mcp-server \
  --payload '{"httpMethod": "GET", "path": "/health"}' \
  response.json

# Test public endpoint
curl https://your-lambda-url.lambda-url.us-east-1.on.aws/health

# Run production tests
python test_mcp_server.py --environment bear --endpoint https://your-lambda-url
```

## 🔄 Data Replication Deployment

### Glue ETL Job Setup
```bash
# Create Glue database
aws glue create-database \
  --database-input '{
    "Name": "sap_datasphere_s3_tables",
    "Description": "SAP Datasphere replicated data in S3 Tables"
  }'

# Deploy ETL job script to S3
aws s3 cp glue-scripts/odata_to_s3_tables.py \
  s3://sap-glue-scripts/odata_to_s3_tables.py

# Create Glue ETL job
aws glue create-job \
  --name sap-odata-to-s3-tables-etl \
  --role arn:aws:iam::YOUR_ACCOUNT:role/GlueServiceRole-SAP-Replication \
  --command '{
    "Name": "glueetl",
    "ScriptLocation": "s3://sap-glue-scripts/odata_to_s3_tables.py",
    "PythonVersion": "3"
  }' \
  --default-arguments '{
    "--job-language": "python",
    "--enable-metrics": "true",
    "--enable-spark-ui": "true"
  }' \
  --max-retries 2 \
  --timeout 2880 \
  --worker-type G.2X \
  --number-of-workers 4
```

### Test Data Replication
```bash
# Test replication with sample asset
python comprehensive_asset_discovery_and_sync.py \
  --asset SAP_SC_FI_T_Products \
  --target-format ICEBERG \
  --dry-run

# Start actual replication
python comprehensive_asset_discovery_and_sync.py \
  --asset SAP_SC_FI_T_Products \
  --target-format ICEBERG
```

## 📊 Monitoring & Observability

### CloudWatch Setup
```bash
# Create CloudWatch dashboard
aws cloudwatch put-dashboard \
  --dashboard-name SAP-Datasphere-MCP \
  --dashboard-body file://cloudwatch-dashboard.json

# Create alarms
aws cloudwatch put-metric-alarm \
  --alarm-name "MCP-Server-Errors" \
  --alarm-description "MCP Server error rate" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold
```

### Log Aggregation
```bash
# Create log groups
aws logs create-log-group --log-group-name /aws/lambda/sap-datasphere-mcp-server
aws logs create-log-group --log-group-name /aws/glue/sap-odata-to-s3-tables-etl

# Set retention policy
aws logs put-retention-policy \
  --log-group-name /aws/lambda/sap-datasphere-mcp-server \
  --retention-in-days 30
```

## 🔐 Security Hardening

### Network Security
```bash
# Create VPC for secure deployment (optional)
aws ec2 create-vpc --cidr-block 10.0.0.0/16

# Configure security groups
aws ec2 create-security-group \
  --group-name sap-datasphere-mcp-sg \
  --description "Security group for SAP Datasphere MCP Server"
```

### IAM Policies
```bash
# Create least-privilege IAM policy
aws iam create-policy \
  --policy-name SAP-Datasphere-MCP-Policy \
  --policy-document file://iam-policy.json

# Attach to Lambda execution role
aws iam attach-role-policy \
  --role-name lambda-execution-role \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT:policy/SAP-Datasphere-MCP-Policy
```

### Secrets Rotation
```bash
# Enable automatic rotation for SAP credentials
aws secretsmanager update-secret \
  --secret-id sap-datasphere-credentials \
  --description "SAP Datasphere OAuth credentials with auto-rotation" \
  --kms-key-id alias/aws/secretsmanager
```

## 🧪 Testing & Validation

### Comprehensive Testing Suite
```bash
# Run all environment tests
for env in dog wolf bear; do
  echo "Testing $env environment..."
  python test_mcp_server.py --environment $env --comprehensive
done

# Test data replication end-to-end
python test_comprehensive_replication.py

# Validate OAuth flows
python test_oauth_comprehensive.py

# Performance benchmarking
python benchmark_all_environments.py
```

### Health Checks
```bash
# Create health check script
cat > health_check.sh << 'EOF'
#!/bin/bash
echo "Checking Dog environment..."
curl -f http://localhost:8001/api/status || exit 1

echo "Checking Wolf environment..."
curl -f http://localhost:5000/api/status || exit 1

echo "Checking Bear environment..."
curl -f https://your-lambda-url.lambda-url.us-east-1.on.aws/health || exit 1

echo "All environments healthy!"
EOF

chmod +x health_check.sh
./health_check.sh
```

## 🔄 Maintenance & Updates

### Automated Deployment Pipeline
```yaml
# GitHub Actions workflow example
name: Deploy SAP Datasphere MCP Server
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Dog
        run: python deploy.py --environment dog
      - name: Test Dog deployment
        run: python test_mcp_server.py --environment dog
      - name: Deploy to Wolf
        run: python deploy.py --environment wolf
      - name: Deploy to Bear
        run: python deploy.py --environment bear
```

### Backup & Recovery
```bash
# Backup configuration
aws s3 cp config/ s3://sap-mcp-backups/config/ --recursive

# Backup secrets
aws secretsmanager describe-secret --secret-id sap-datasphere-credentials > backup-secrets.json

# Create AMI for EC2 deployments (if applicable)
aws ec2 create-image --instance-id i-1234567890abcdef0 --name "SAP-MCP-Server-$(date +%Y%m%d)"
```

## 📞 Support & Troubleshooting

### Common Issues

#### OAuth Authentication Failures
```bash
# Validate OAuth configuration
python validate_oauth_config.py --environment dog

# Test token refresh
python test_token_refresh.py
```

#### Lambda Cold Start Issues
```bash
# Enable provisioned concurrency
aws lambda put-provisioned-concurrency-config \
  --function-name sap-datasphere-mcp-server \
  --qualifier $LATEST \
  --provisioned-concurrency-config ProvisionedConcurrencyUnits=2
```

#### Performance Issues
```bash
# Monitor CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=sap-datasphere-mcp-server \
  --start-time 2024-10-24T00:00:00Z \
  --end-time 2024-10-24T23:59:59Z \
  --period 3600 \
  --statistics Average
```

### Getting Help
- **Documentation**: [Complete guides and API reference](README.md)
- **GitHub Issues**: [Report bugs and request features](https://github.com/MarioDeFelipe/sap-datasphere-mcp/issues)
- **Community**: [Discussions and support](https://github.com/MarioDeFelipe/sap-datasphere-mcp/discussions)

---

**🎉 Congratulations! Your SAP Datasphere MCP Server is now deployed and ready for AI-powered data operations across all environments!** 🚀