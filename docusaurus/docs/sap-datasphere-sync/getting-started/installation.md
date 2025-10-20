# Installation Guide

This guide will walk you through installing and setting up the SAP Datasphere to AWS metadata synchronization system.

## 📋 Prerequisites

### System Requirements
- **Python 3.10+** (Python 3.13 recommended)
- **Node.js 18+** (for web dashboard)
- **Docker** (for development environment)
- **AWS CLI** configured with appropriate permissions
- **SAP Datasphere** access with OAuth credentials

### AWS Permissions Required
Your AWS credentials need the following permissions:
- **AWS Glue**: Full access to Data Catalog operations
- **AWS Lake Formation**: Data location and governance permissions
- **Amazon QuickSight**: Dataset and dashboard creation (optional)
- **Amazon DataZone**: Domain and data product management (optional)

### SAP Datasphere Requirements
- **OAuth Application** registered in Datasphere
- **API Access** to consumption and enhanced metadata APIs
- **Browser Authentication** capability for enhanced features

## 🚀 Quick Installation

### Option 1: Using uv (Recommended)

```bash
# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/awslabs/mcp.git
cd mcp

# Install dependencies and create virtual environment
uv venv && uv sync --all-groups

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
```

### Option 2: Using pip

```bash
# Clone the repository
git clone https://github.com/awslabs/mcp.git
cd mcp

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

## ⚙️ Configuration Setup

### 1. AWS Configuration

Configure your AWS credentials using one of these methods:

#### AWS CLI Configuration
```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and default region
```

#### Environment Variables
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

#### AWS Profile
```bash
# Create named profile
aws configure --profile datasphere-sync

# Use profile in application
export AWS_PROFILE=datasphere-sync
```

### 2. SAP Datasphere Configuration

Create your Datasphere OAuth configuration:

```bash
# Copy the example configuration
cp datasphere-oauth-config.json.example datasphere-oauth-config.json
```

Edit `datasphere-oauth-config.json`:

```json
{
  "base_url": "https://your-tenant.datasphere.cloud.sap",
  "client_id": "your_oauth_client_id",
  "client_secret": "your_oauth_client_secret",
  "token_url": "https://your-tenant.authentication.sap.hana.ondemand.com/oauth/token",
  "scope": "uaa.resource",
  "environment": "ailien-test"
}
```

### 3. Application Configuration

Create the main configuration file:

```bash
# Copy example configuration
cp config/app-config.json.example config/app-config.json
```

Edit `config/app-config.json`:

```json
{
  "datasphere": {
    "config_file": "datasphere-oauth-config.json",
    "enhanced_apis": true,
    "browser_auth": true
  },
  "aws": {
    "region": "us-east-1",
    "glue_database_prefix": "datasphere_",
    "enable_lake_formation": true
  },
  "sync": {
    "incremental_enabled": true,
    "checkpoint_dir": "checkpoints",
    "max_workers": 5,
    "priority_scheduling": true
  },
  "web_dashboard": {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": false
  }
}
```

## 🧪 Verify Installation

### 1. Test Datasphere Connection

```bash
python test_datasphere_integration.py
```

Expected output:
```
✅ Datasphere connector initialized successfully
✅ OAuth authentication successful
✅ Enhanced APIs accessible
✅ Metadata extraction working
```

### 2. Test AWS Connection

```bash
python test_glue_integration.py
```

Expected output:
```
✅ AWS Glue connector initialized successfully
✅ Data Catalog access confirmed
✅ Database creation permissions verified
```

### 3. Test Incremental Sync Engine

```bash
python test_incremental_sync.py
```

Expected output:
```
✅ Checkpoint management: PASS
✅ Change detection: PASS
✅ Incremental sync engine: PASS
✅ Orchestrator integration: PASS
✅ Performance benefits: PASS
```

## 🌐 Start the Web Dashboard

Launch the web-based management interface:

```bash
python web_dashboard.py
```

The dashboard will be available at: **http://localhost:8000**

### Dashboard Features
- **📊 Features Overview**: Comprehensive capability showcase
- **🔗 Connection Management**: Test and configure connections
- **📈 Sync Monitoring**: Real-time synchronization status
- **⚙️ Configuration**: Manage sync rules and settings

## 🐳 Docker Development Environment

For development with isolated dependencies:

### Build and Run
```bash
# Build the Docker image
docker build -t datasphere-sync .

# Run with environment variables
docker run -d \
  --name datasphere-sync \
  -p 8000:8000 \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret \
  -e AWS_DEFAULT_REGION=us-east-1 \
  -v $(pwd)/config:/app/config \
  datasphere-sync
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'
services:
  datasphere-sync:
    build: .
    ports:
      - "8000:8000"
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_DEFAULT_REGION=us-east-1
    volumes:
      - ./config:/app/config
      - ./checkpoints:/app/checkpoints
```

Run with Docker Compose:
```bash
docker-compose up -d
```

## 🔧 Development Setup

For development and contribution:

### Install Development Dependencies
```bash
# Using uv
uv sync --all-groups --dev

# Using pip
pip install -r requirements-dev.txt
```

### Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run all checks
pre-commit run --all-files
```

### Code Quality Tools
```bash
# Run linting and formatting
ruff check --fix
ruff format

# Type checking
pyright --stats

# Run tests with coverage
pytest --cov --cov-branch --cov-report=term-missing
```

## 🚨 Troubleshooting

### Common Issues

#### 1. OAuth Authentication Fails
```bash
# Check your OAuth configuration
python -c "
import json
with open('datasphere-oauth-config.json') as f:
    config = json.load(f)
    print('Base URL:', config['base_url'])
    print('Client ID:', config['client_id'][:8] + '...')
"
```

#### 2. AWS Permissions Error
```bash
# Test AWS permissions
aws sts get-caller-identity
aws glue get-databases --max-results 1
```

#### 3. Enhanced APIs Not Accessible
- Ensure browser authentication is enabled
- Check that you're using the correct Datasphere environment
- Verify enhanced API endpoints are available in your tenant

#### 4. Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill the process or use a different port
python web_dashboard.py --port 8001
```

### Getting Help

- **📖 Documentation**: Check the comprehensive documentation
- **🐛 Issues**: Report bugs on [GitHub Issues](https://github.com/awslabs/mcp/issues)
- **💬 Discussions**: Join [GitHub Discussions](https://github.com/awslabs/mcp/discussions)

## ✅ Next Steps

Once installation is complete:

1. **[Configuration Guide](./configuration)** - Detailed configuration options
2. **[Quick Start Tutorial](./quick-start)** - Run your first synchronization


---

🎉 **Congratulations!** You've successfully installed the SAP Datasphere to AWS metadata synchronization system. Ready to start syncing? Head to the [Quick Start Guide](./quick-start)!