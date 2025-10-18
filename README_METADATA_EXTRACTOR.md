# 🚀 Enhanced SAP Datasphere Metadata Extractor

A production-ready tool for extracting metadata from SAP Datasphere and replicating it to AWS Glue Data Catalog. Built on top of your successful MCP server integration with real API access.

## 🎯 What This Tool Does

- **Discovers** analytical models in your SAP Datasphere environment
- **Extracts** detailed metadata including tables, columns, and data types
- **Replicates** the metadata to AWS Glue Data Catalog for analytics
- **Maps** SAP data types to AWS Glue compatible types
- **Handles** authentication, error recovery, and logging

## ✅ Prerequisites

### SAP Datasphere
- Access to SAP Datasphere tenant
- OAuth2 client credentials with API access
- Technical user with consumption API permissions

### AWS
- AWS account with Glue permissions
- AWS credentials configured (IAM role, profile, or access keys)
- Permissions to create/update Glue databases and tables

### Python Environment
- Python 3.7+
- Required packages (see installation below)

## 🔧 Installation

1. **Clone or download the files:**
   ```bash
   # Download the enhanced metadata extractor files
   # enhanced_metadata_extractor.py
   # run_metadata_extraction.py
   # test_real_datasphere.py
   # setup_real_datasphere_config.py
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements_metadata_extractor.txt
   
   # Or install core dependencies only:
   pip install requests boto3 python-dotenv
   ```

3. **Set up environment variables:**
   ```bash
   # Required: SAP Datasphere OAuth client secret
   export DATASPHERE_CLIENT_SECRET="your_oauth_client_secret"
   
   # AWS credentials (choose one method):
   # Method 1: AWS Profile (recommended)
   export AWS_PROFILE="your_aws_profile"
   
   # Method 2: Access Keys (not recommended for production)
   export AWS_ACCESS_KEY_ID="your_access_key"
   export AWS_SECRET_ACCESS_KEY="your_secret_key"
   
   # Method 3: IAM Role (best for EC2/Lambda - no config needed)
   
   # Optional: AWS Region
   export AWS_REGION="us-east-1"
   ```

## 🚀 Quick Start

### Step 1: Test Your Connection
```bash
python test_real_datasphere.py
```

This will verify:
- ✅ OAuth authentication works
- ✅ API endpoints are accessible
- ✅ Metadata extraction is possible

### Step 2: Run Metadata Extraction
```bash
python run_metadata_extraction.py
```

This will:
- 🔍 Discover analytical models in Datasphere
- 📊 Extract metadata for each model
- ☁️ Create/update AWS Glue catalog
- 📄 Generate detailed results report

### Step 3: Verify Results
Check your AWS Glue Console:
- Database: `datasphere_real_catalog`
- Tables: `{space}_{model_name}` (e.g., `sap_content_new_analytic_model_2`)

## 📋 Configuration Options

### Using Configuration Files

Create a `.env` file:
```bash
# SAP Datasphere
DATASPHERE_CLIENT_SECRET=your_oauth_client_secret

# AWS
AWS_REGION=us-east-1
AWS_PROFILE=your_profile
```

### Interactive Setup
```bash
python setup_real_datasphere_config.py
```

This provides an interactive setup wizard for configuration.

## 🔍 Understanding the Output

### Successful Extraction
```
🎉 SUCCESS!
📊 Tables discovered: 2
✅ Tables replicated: 2
⏱️ Execution time: 15.32 seconds
```

### What Gets Created in AWS Glue

For each Datasphere analytical model, the tool creates:

**Database:** `datasphere_real_catalog`

**Table:** `{space}_{model}` with:
- Column definitions with proper data types
- Metadata parameters including:
  - `datasphere_source`: "true"
  - `datasphere_space`: Original space name
  - `datasphere_model`: Original model name
  - `source_url`: Direct API URL for data access
  - `metadata_url`: Metadata endpoint URL
  - `last_updated`: Extraction timestamp

### Data Type Mapping

| SAP Datasphere Type | AWS Glue Type |
|-------------------|---------------|
| Edm.String | string |
| Edm.Int32 | int |
| Edm.Int64 | bigint |
| Edm.Double | double |
| Edm.Decimal | decimal(18,2) |
| Edm.Boolean | boolean |
| Edm.DateTime | timestamp |
| Edm.Date | date |

## 🔧 Advanced Usage

### Custom Configuration
```python
from enhanced_metadata_extractor import run_enhanced_metadata_extraction

# Custom configuration
datasphere_config = {
    "base_url": "https://your-tenant.eu10.hcs.cloud.sap",
    "oauth": {
        "client_id": "your_client_id",
        "client_secret": "your_client_secret",
        "token_url": "https://your-tenant.eu10.hcs.cloud.sap/oauth/token"
    }
}

aws_config = {
    "region": "us-west-2"
}

# Run extraction
result = run_enhanced_metadata_extraction(
    datasphere_config=datasphere_config,
    aws_config=aws_config,
    glue_database="my_custom_database"
)
```

### Scheduled Extraction

Set up a cron job for regular updates:
```bash
# Run every day at 2 AM
0 2 * * * /usr/bin/python3 /path/to/run_metadata_extraction.py
```

Or use AWS Lambda with EventBridge for cloud-based scheduling.

## 🐛 Troubleshooting

### Common Issues

**OAuth Authentication Failed**
```
❌ OAuth failed: HTTP 401
```
- Check your `DATASPHERE_CLIENT_SECRET`
- Verify client ID is correct
- Ensure technical user has API permissions

**AWS Permissions Error**
```
❌ Failed to create database: AccessDenied
```
- Check AWS credentials are configured
- Verify Glue permissions in IAM policy
- Ensure region is correct

**No Models Discovered**
```
⚠️ No analytical models discovered
```
- Check if you have access to analytical models
- Verify space permissions in Datasphere
- Try the test script to debug API access

**Metadata Extraction Failed**
```
❌ Failed to extract metadata: HTTP 406
```
- XML metadata endpoint may not accept JSON requests
- Tool will fallback to data inference
- This is a known limitation, extraction will still work

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Getting Help

1. Run the test script: `python test_real_datasphere.py`
2. Check the generated log files
3. Verify your credentials and permissions
4. Review the error messages in the results JSON file

## 📊 Performance Considerations

### Optimization Tips

- **Batch Processing**: The tool processes models sequentially
- **Caching**: OAuth tokens are cached during execution
- **Error Recovery**: Failed models don't stop the entire process
- **Incremental Updates**: Existing tables are updated, not recreated

### Scaling for Large Environments

For environments with many models:
- Consider running in parallel batches
- Use AWS Lambda for serverless execution
- Implement selective extraction by space/model
- Set up monitoring and alerting

## 🔒 Security Best Practices

### Credential Management
- Use AWS IAM roles when possible
- Store secrets in AWS Secrets Manager or similar
- Rotate OAuth client secrets regularly
- Use least-privilege access policies

### Network Security
- Run in private subnets when possible
- Use VPC endpoints for AWS services
- Implement proper firewall rules
- Monitor API access logs

## 🎯 Integration with Your Existing MCP Server

This metadata extractor complements your existing MCP server:

**MCP Server**: Real-time data access and querying
**Metadata Extractor**: Batch metadata replication to AWS

Together they provide:
- ✅ Real-time AI assistant integration (MCP)
- ✅ Batch analytics preparation (Metadata Extractor)
- ✅ AWS native data catalog (Glue)
- ✅ Query capability (Athena)

## 📈 Next Steps

### Immediate
1. ✅ Test your connection
2. ✅ Run first extraction
3. ✅ Verify results in AWS Glue Console
4. ✅ Query data with Amazon Athena

### Advanced
- Set up scheduled extractions
- Build data pipelines with AWS Glue ETL
- Create dashboards with Amazon QuickSight
- Implement data governance with AWS Lake Formation

## 🎉 Success Metrics

Your metadata extraction is successful when you can:
- ✅ See Datasphere tables in AWS Glue Console
- ✅ Query the metadata using Amazon Athena
- ✅ Access data through the replicated schema
- ✅ Build analytics on top of the extracted metadata

---

## 📞 Support

This tool builds on your successful MCP server integration. If you encounter issues:

1. Check the test results from `test_real_datasphere.py`
2. Review the detailed error logs
3. Verify your working MCP server still functions
4. Compare configurations between working MCP and metadata extractor

**Built with ❤️ on top of your 85.7% successful SAP Datasphere MCP integration!**