# 🚀 Hello World AWS Lambda

A simple "Hello World" web application deployed on AWS Lambda with public access.

## 🎯 What This Is

This is a serverless web application that:
- ✅ Runs on AWS Lambda (Python 3.13)
- ✅ Has a public URL (no authentication required)
- ✅ Shows a beautiful HTML page with request information
- ✅ Serves as foundation for your SAP Datasphere Control Panel

## 📋 Prerequisites

- AWS CLI installed and configured
- Python 3.7+ (for local testing)
- AWS account with appropriate permissions

## 🚀 Quick Deployment

### Option 1: Using Bash Script (Recommended)
```bash
# Make script executable
chmod +x deploy.sh

# Deploy to AWS
./deploy.sh
```

### Option 2: Using Python Script
```bash
# Deploy using Python
python deploy.py
```

### Option 3: Manual AWS CLI Commands
```bash
# Create deployment package
zip hello-world-lambda.zip app.py

# Create IAM role
aws iam create-role \
    --role-name hello-world-datasphere-role \
    --assume-role-policy-document file://trust-policy.json

# Attach execution policy
aws iam attach-role-policy \
    --role-name hello-world-datasphere-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Create Lambda function
aws lambda create-function \
    --function-name hello-world-datasphere \
    --runtime python3.13 \
    --role arn:aws:iam::YOUR_ACCOUNT:role/hello-world-datasphere-role \
    --handler app.lambda_handler \
    --zip-file fileb://hello-world-lambda.zip

# Create public Function URL
aws lambda create-function-url-config \
    --function-name hello-world-datasphere \
    --config AuthType=NONE
```

## 🧪 Local Testing

Test the function locally before deploying:

```bash
# Test locally
python test_local.py

# Open the generated HTML file
open test_output.html  # macOS
start test_output.html # Windows
```

## 📊 What You'll Get

After deployment, you'll receive:

- **Function Name**: `hello-world-datasphere`
- **Public URL**: `https://xxxxxxxxxx.lambda-url.us-east-1.on.aws/`
- **IAM Role**: `hello-world-datasphere-role`

## 🌐 Accessing Your App

1. **Get the URL** from the deployment output
2. **Open in browser** - no authentication needed
3. **Share with anyone** - it's publicly accessible

## 🎨 What the App Shows

The Hello World app displays:

- 👋 Welcome message
- 📊 Request information (timestamp, IP, user agent)
- 🛠️ Technology stack used
- 🎯 Next steps for building your control panel

## 🔧 Customization

### Modify the HTML
Edit `app.py` and update the `html_content` variable to customize:
- Styling (CSS)
- Content
- Functionality

### Add API Endpoints
```python
def lambda_handler(event, context):
    path = event.get('rawPath', '/')
    method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
    
    if path == '/api/health':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'status': 'healthy'})
        }
    
    # Default HTML response
    return html_response()
```

### Environment Variables
Add environment variables in the deployment:
```bash
aws lambda update-function-configuration \
    --function-name hello-world-datasphere \
    --environment Variables='{API_KEY=your-key,DEBUG=true}'
```

## 🚀 Next Steps

This Hello World app is your foundation for building the SAP Datasphere Control Panel:

### Phase 1: API Backend
- Add FastAPI framework
- Create REST endpoints
- Add database connectivity
- Implement authentication

### Phase 2: Frontend
- Add React frontend
- Create dashboard components
- Implement real-time updates
- Add data visualization

### Phase 3: Integration
- Connect to Datasphere APIs
- Implement sync functionality
- Add monitoring and alerts
- Deploy production version

## 📁 File Structure

```
hello-world-aws/
├── app.py              # Lambda function code
├── deploy.py           # Python deployment script
├── deploy.sh           # Bash deployment script
├── test_local.py       # Local testing script
└── README.md           # This file
```

## 🛠️ Troubleshooting

### Common Issues

1. **Permission Denied**
   ```bash
   # Ensure AWS CLI is configured
   aws configure
   
   # Check permissions
   aws sts get-caller-identity
   ```

2. **Role Creation Failed**
   ```bash
   # Role might already exist
   aws iam get-role --role-name hello-world-datasphere-role
   ```

3. **Function URL Not Working**
   ```bash
   # Check Function URL configuration
   aws lambda get-function-url-config --function-name hello-world-datasphere
   ```

### Cleanup

To remove all resources:
```bash
# Delete Function URL
aws lambda delete-function-url-config --function-name hello-world-datasphere

# Delete Lambda function
aws lambda delete-function --function-name hello-world-datasphere

# Detach policy and delete role
aws iam detach-role-policy \
    --role-name hello-world-datasphere-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam delete-role --role-name hello-world-datasphere-role
```

## 🎉 Success!

Once deployed, you'll have:
- ✅ A working serverless web application
- ✅ Public URL accessible from anywhere
- ✅ Foundation for your control panel
- ✅ Experience with AWS Lambda deployment

**Ready to build amazing things on AWS!** 🌟