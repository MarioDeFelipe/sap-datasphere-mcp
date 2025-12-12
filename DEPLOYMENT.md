# SAP Datasphere MCP Server - Production Deployment Guide

**Version**: 1.0.0
**Last Updated**: December 12, 2025
**Status**: Production Ready

This guide covers deploying the SAP Datasphere MCP Server in production environments.

---

## 🎯 Deployment Options

| Option | Use Case | Difficulty | Setup Time |
|--------|----------|------------|------------|
| [Docker](#docker-deployment) | Single server, easy management | Easy | 5 minutes |
| [Docker Compose](#docker-compose-deployment) | Multi-container | Easy | 10 minutes |
| [Kubernetes](#kubernetes-deployment) | Enterprise, auto-scaling | Medium | 30 minutes |
| [PyPI Package](#pypi-installation) | Python environments | Easy | 2 minutes |
| [Manual](#manual-deployment) | Custom setups | Medium | 15 minutes |

---

## 🐳 Docker Deployment

### Quick Start

**1. Build the image**:
```bash
docker build -t sap-datasphere-mcp:latest .
```

**2. Create .env file** (see [Configuration](#configuration))

**3. Run the container**:
```bash
docker run -d \
  --name sap-mcp-server \
  --env-file .env \
  --restart unless-stopped \
  sap-datasphere-mcp:latest
```

**4. Verify it's running**:
```bash
docker logs sap-mcp-server
# Should show: ✅ Server listening on stdio
```

### Production Configuration

```bash
docker run -d \
  --name sap-mcp-server \
  --env-file .env \
  --restart unless-stopped \
  --memory="512m" \
  --cpus="1.0" \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  -v $(pwd)/logs:/app/logs \
  sap-datasphere-mcp:latest
```

---

## 🐳 Docker Compose Deployment

**1. Start services**:
```bash
docker-compose up -d
```

**2. Check status**:
```bash
docker-compose ps
docker-compose logs -f sap-datasphere-mcp
```

**3. Stop services**:
```bash
docker-compose down
```

**docker-compose.yml** already included in repository!

---

## ☸️ Kubernetes Deployment

### Kubernetes Manifests

**1. Create ConfigMap for .env**:
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: sap-mcp-config
  namespace: default
data:
  LOG_LEVEL: "INFO"
  SERVER_PORT: "8080"
  USE_MOCK_DATA: "false"
```

**2. Create Secret for OAuth credentials**:
```bash
kubectl create secret generic sap-mcp-secrets \
  --from-literal=DATASPHERE_CLIENT_ID='your-client-id' \
  --from-literal=DATASPHERE_CLIENT_SECRET='your-client-secret' \
  --from-literal=DATASPHERE_TOKEN_URL='your-token-url' \
  --from-literal=DATASPHERE_BASE_URL='your-base-url' \
  --from-literal=DATASPHERE_TENANT_ID='your-tenant-id'
```

**3. Create Deployment**:
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sap-mcp-server
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: sap-mcp-server
  template:
    metadata:
      labels:
        app: sap-mcp-server
    spec:
      containers:
      - name: sap-mcp-server
        image: sap-datasphere-mcp:latest
        imagePullPolicy: Always
        envFrom:
        - configMapRef:
            name: sap-mcp-config
        - secretRef:
            name: sap-mcp-secrets
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "1000m"
        livenessProbe:
          exec:
            command: ["python", "-c", "import sys; sys.exit(0)"]
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          exec:
            command: ["python", "-c", "import sys; sys.exit(0)"]
          initialDelaySeconds: 10
          periodSeconds: 10
```

**4. Deploy**:
```bash
kubectl apply -f k8s/
kubectl get pods -l app=sap-mcp-server
```

---

## 📦 PyPI Installation

**Once published to PyPI**:

```bash
# Install
pip install sap-datasphere-mcp

# Create .env file
cat > .env << EOF
DATASPHERE_BASE_URL=https://your-tenant.eu20.hcs.cloud.sap
DATASPHERE_CLIENT_ID=your-client-id
DATASPHERE_CLIENT_SECRET=your-client-secret
DATASPHERE_TOKEN_URL=your-token-url
DATASPHERE_TENANT_ID=your-tenant-id
USE_MOCK_DATA=false
LOG_LEVEL=INFO
EOF

# Run
sap-datasphere-mcp
```

---

## 🔧 Configuration

### Environment Variables

**Required**:
```bash
# SAP Datasphere connection
DATASPHERE_BASE_URL=https://tenant.region.hcs.cloud.sap
DATASPHERE_TENANT_ID=your-tenant-id

# OAuth 2.0 credentials
DATASPHERE_CLIENT_ID=sb-xxxxx!b130936|client!b3944
DATASPHERE_CLIENT_SECRET=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx$xxxxx
DATASPHERE_TOKEN_URL=https://tenant.authentication.region.hana.ondemand.com/oauth/token
```

**Optional**:
```bash
# Server configuration
LOG_LEVEL=INFO           # DEBUG, INFO, WARNING, ERROR
SERVER_PORT=8080         # If using HTTP mode
USE_MOCK_DATA=false      # Always false for production

# OAuth scope (optional)
DATASPHERE_SCOPE=        # Leave empty for default scopes
```

### Getting OAuth Credentials

1. Log into SAP Datasphere
2. Go to **System → Administration → App Integration**
3. Click **Add New OAuth Client**
4. Configure:
   - Name: `MCP Server Production`
   - Purpose: `Data Access via MCP`
   - Scopes: Select `DWC_DATA_ACCESS`, `DWC_CATALOG_READ`
5. Copy **Client ID** and **Client Secret**
6. Note the **Token URL** from client details

---

## 🔒 Security Best Practices

### 1. Secrets Management

**❌ Never**:
- Commit `.env` to git
- Share credentials in plain text
- Use default/weak passwords
- Expose credentials in logs

**✅ Always**:
- Use Kubernetes Secrets or Docker Secrets
- Rotate credentials regularly
- Use environment-specific credentials
- Monitor access logs

**Example with Kubernetes Secrets**:
```bash
# Store in Kubernetes secret
kubectl create secret generic sap-oauth \
  --from-literal=client-id=xxx \
  --from-literal=client-secret=yyy

# Reference in deployment
envFrom:
- secretRef:
    name: sap-oauth
```

### 2. Network Security

**Firewall Rules**:
```bash
# Allow outbound to SAP Datasphere
- Destination: your-tenant.region.hcs.cloud.sap
- Port: 443 (HTTPS)
- Protocol: TCP
```

**Reverse Proxy (Optional)**:
```nginx
# nginx.conf
server {
    listen 443 ssl;
    server_name mcp.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Access Control

**Principle of Least Privilege**:
- Grant minimum required OAuth scopes
- Use read-only access where possible
- Separate prod/dev credentials

**Audit Logging**:
```python
# Enable detailed logging in production
LOG_LEVEL=INFO  # Captures all API calls
```

---

## 📊 Monitoring

### Health Checks

**Docker**:
```bash
docker inspect --format='{{.State.Health.Status}}' sap-mcp-server
```

**Kubernetes**:
```bash
kubectl get pods -l app=sap-mcp-server
kubectl describe pod <pod-name>
```

### Logging

**View Logs (Docker)**:
```bash
# Tail logs
docker logs -f sap-mcp-server

# Last 100 lines
docker logs --tail 100 sap-mcp-server

# Since 1 hour ago
docker logs --since 1h sap-mcp-server
```

**View Logs (Kubernetes)**:
```bash
# Tail logs
kubectl logs -f deployment/sap-mcp-server

# Multiple pods
kubectl logs -f -l app=sap-mcp-server
```

### Metrics to Monitor

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| CPU Usage | Server CPU utilization | > 80% |
| Memory Usage | RAM consumption | > 80% |
| Request Latency | API response time | > 5 seconds |
| Error Rate | Failed requests | > 5% |
| OAuth Token Refresh | Token refresh failures | Any failure |

---

## 🚀 Scaling

### Horizontal Scaling (Kubernetes)

**Scale up**:
```bash
kubectl scale deployment sap-mcp-server --replicas=5
```

**Auto-scaling**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: sap-mcp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: sap-mcp-server
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Vertical Scaling

**Increase resources**:
```yaml
resources:
  requests:
    memory: "512Mi"  # Was 256Mi
    cpu: "500m"      # Was 250m
  limits:
    memory: "1Gi"    # Was 512Mi
    cpu: "2000m"     # Was 1000m
```

---

## 🔄 Updates and Maintenance

### Zero-Downtime Updates (Kubernetes)

```yaml
# deployment.yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
```

**Deploy update**:
```bash
# Update image
kubectl set image deployment/sap-mcp-server \
  sap-mcp-server=sap-datasphere-mcp:v1.1.0

# Check rollout status
kubectl rollout status deployment/sap-mcp-server

# Rollback if needed
kubectl rollout undo deployment/sap-mcp-server
```

### Backup and Disaster Recovery

**What to backup**:
- `.env` file (securely encrypted)
- OAuth credentials
- Configuration files
- Custom modifications

**Backup script**:
```bash
#!/bin/bash
BACKUP_DIR="/backups/sap-mcp/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup .env (encrypted)
gpg --encrypt --recipient admin@example.com \
  --output $BACKUP_DIR/.env.gpg .env

# Backup configs
cp docker-compose.yml $BACKUP_DIR/
cp k8s/*.yaml $BACKUP_DIR/

echo "Backup complete: $BACKUP_DIR"
```

---

## ✅ Production Checklist

### Pre-Deployment
- [ ] OAuth credentials configured and tested
- [ ] `.env` file created with production values
- [ ] `USE_MOCK_DATA=false` confirmed
- [ ] Network firewall rules configured
- [ ] SSL/TLS certificates obtained (if using HTTPS)
- [ ] Monitoring tools set up
- [ ] Backup strategy defined

### Deployment
- [ ] Container/deployment created successfully
- [ ] Health checks passing
- [ ] Logs show no errors
- [ ] Test connection succeeds
- [ ] Can list spaces successfully
- [ ] Can query data successfully

### Post-Deployment
- [ ] Monitor for 24 hours
- [ ] Check error rates
- [ ] Verify OAuth token refresh working
- [ ] Test failover (if using replicas)
- [ ] Document any issues
- [ ] Train operations team

---

## 🆘 Troubleshooting Production Issues

### Issue: Container keeps restarting

**Check logs**:
```bash
docker logs sap-mcp-server | tail -50
```

**Common causes**:
1. Missing .env file
2. Invalid OAuth credentials
3. Network connectivity issues
4. Memory limits too low

**Fix**:
```bash
# Increase memory limit
docker update --memory="1g" sap-mcp-server

# Restart
docker restart sap-mcp-server
```

### Issue: High latency

**Check metrics**:
```bash
# CPU/Memory usage
docker stats sap-mcp-server
```

**Solutions**:
1. Increase resources
2. Enable caching (if implemented)
3. Scale horizontally
4. Check SAP Datasphere tenant performance

---

## 📚 Additional Resources

- **[Getting Started Guide](GETTING_STARTED_GUIDE.md)** - Initial setup
- **[Tools Catalog](TOOLS_CATALOG.md)** - All 41 tools
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues
- **[API Reference](API_REFERENCE.md)** - Developer docs

---

**Document Version**: 1.0
**Last Updated**: December 12, 2025
**Status**: Production Ready ✅
