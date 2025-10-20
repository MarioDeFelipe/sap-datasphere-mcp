# Installation

SAP Datasphere Sync can be deployed in three different environments depending on your needs. Follow the installation guide for your target environment.

## Prerequisites

Before installing SAP Datasphere Sync, ensure you have:

1. **SAP Datasphere Access**
   - SAP Datasphere tenant with OAuth 2.0 client credentials
   - Appropriate permissions for metadata extraction
   - Network access to your Datasphere environment

2. **AWS Account Setup**
   - AWS account with Glue Data Catalog access
   - AWS CLI configured with appropriate IAM permissions
   - AWS Secrets Manager for secure credential storage

3. **Development Environment**
   - Python 3.10+ installed
   - Git for source code management
   - Docker (optional, for containerized deployment)

## 🐕 DOG Environment (Development)

The DOG environment provides a full-featured development setup with live SAP Datasphere and AWS Glue integration.

### Quick Start

1. **Clone the Repository**
   ```bash
   git clone https://github.com/ailien-studio/sap-datasphere-sync.git
   cd sap-datasphere-sync
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure SAP Credentials**
   Store your SAP Datasphere OAuth credentials in AWS Secrets Manager:
   ```bash
   aws secretsmanager create-secret \
     --name "sap-datasphere-credentials" \
     --description "SAP Datasphere OAuth credentials for data sync" \
     --secret-string '{
       "tenant_name": "your-tenant",
       "base_url": "https://your-tenant.eu20.hcs.cloud.sap",
       "client_id": "your-client-id",
       "client_secret": "your-client-secret",
       "token_url": "https://your-tenant.authentication.eu20.hana.ondemand.com/oauth/token"
     }'
   ```

4. **Start the Web Dashboard**
   ```bash
   python web_dashboard.py
   ```

5. **Access the Dashboard**
   Open [http://localhost:8001](http://localhost:8001) in your browser

## 🐺 WOLF Environment (Testing)

The WOLF environment provides comprehensive integration testing with performance monitoring.

### Setup Instructions

1. **Configure Testing Environment**
   ```bash
   # Set environment variables for testing
   export SAP_ENVIRONMENT=testing
   export AWS_REGION=us-east-1
   export SYNC_MODE=validation
   ```

2. **Run Integration Tests**
   ```bash
   python test_integration.py
   ```

3. **Start WOLF Dashboard**
   ```bash
   python wolf_dashboard.py --port 5000
   ```

## 🐻 BEAR Environment (Production)

The BEAR environment provides enterprise-scale serverless deployment on AWS Lambda.

### Deployment Steps

1. **Prepare for Deployment**
   ```bash
   cd datasphere-control-panel
   pip install -r requirements.txt
   ```

2. **Deploy to AWS Lambda**
   ```bash
   python deploy.py
   ```

3. **Access Production Endpoint**
   The deployment will provide a Lambda URL for production access.

## Configuration

### SAP Datasphere OAuth Setup

1. **Create OAuth Client in SAP Datasphere**
   - Navigate to System → Administration → App Integration
   - Create new OAuth2.0 Client Application
   - Configure redirect URIs and scopes
   - Note the Client ID and Client Secret

2. **Configure AWS Secrets Manager**
   ```json
   {
     "tenant_name": "your-tenant-name",
     "base_url": "https://your-tenant.eu20.hcs.cloud.sap",
     "client_id": "sb-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx!bxxxxxx|client!bxxxx",
     "client_secret": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx$xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx=",
     "authorization_url": "https://your-tenant.authentication.eu20.hana.ondemand.com/oauth/authorize",
     "token_url": "https://your-tenant.authentication.eu20.hana.ondemand.com/oauth/token",
     "oauth_token_url": "https://your-tenant.authentication.eu20.hana.ondemand.com/oauth/token/alias/your-tenant.azure-live-eu20",
     "saml_audience": "https://your-tenant.authentication.eu20.hana.ondemand.com"
   }
   ```

### AWS IAM Permissions

Ensure your AWS credentials have the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "glue:GetDatabase",
        "glue:GetDatabases",
        "glue:CreateDatabase",
        "glue:UpdateDatabase",
        "glue:GetTable",
        "glue:GetTables",
        "glue:CreateTable",
        "glue:UpdateTable",
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": "*"
    }
  ]
}
```

## Troubleshooting

### Common Issues

#### Connection Test Failures

**SAP Datasphere OAuth Issues:**
```bash
# Check if credentials are properly stored
aws secretsmanager get-secret-value --secret-id sap-datasphere-credentials

# Verify OAuth token generation
curl -X POST "https://your-tenant.authentication.eu20.hana.ondemand.com/oauth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET"
```

**AWS Glue Access Issues:**
```bash
# Test AWS credentials
aws sts get-caller-identity

# Test Glue access
aws glue get-databases --region us-east-1
```

#### Performance Issues

**Slow Synchronization:**
- Check network connectivity between environments
- Verify AWS Glue Data Catalog region settings
- Monitor SAP Datasphere API rate limits

**Memory Issues:**
- Increase Python memory limits for large metadata sets
- Consider batch processing for large synchronization jobs

### Logging and Debugging

Enable detailed logging for troubleshooting:

```python
# Set environment variables for debug logging
export LOG_LEVEL=DEBUG
export SAP_DEBUG=true
export AWS_DEBUG=true
```

### Support

For additional support:
- Check the [GitHub Issues](https://github.com/ailien-studio/sap-datasphere-sync/issues)
- Review the [API Documentation](http://localhost:8001/api/docs)
- Contact [Ailien Studio](https://ailien.studio) for enterprise support
