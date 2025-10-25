# Ailien Platform Control Panel - Kubernetes Edition

## 🚀 Modern DevOps Architecture

This is the containerized, Kubernetes-ready version of the Ailien Platform Control Panel.

### Architecture Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GitHub Repo   │───▶│  Docker Image   │───▶│  Kubernetes     │
│   (Source Code) │    │  (ECR/DockerHub)│    │  (EKS/Local)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
   ┌──────────┐           ┌──────────┐           ┌──────────┐
   │ CI/CD    │           │ Registry │           │ Helm     │
   │ Pipeline │           │ Tags     │           │ Charts   │
   └──────────┘           └──────────┘           └──────────┘
```

### Technology Stack
- **Container**: Docker
- **Orchestration**: Kubernetes + Helm
- **CI/CD**: GitHub Actions
- **Registry**: Amazon ECR
- **Backend**: Python FastAPI
- **Frontend**: Professional Dashboard (HTML/CSS/JS)
- **Database**: In-memory + SAP Datasphere API
- **Monitoring**: Kubernetes native + CloudWatch

### Quick Start
```bash
# Local Development
docker-compose up -d

# Kubernetes Deployment
helm install ailien-platform ./helm/ailien-platform

# Build & Push
docker build -t ailien-platform:latest .
docker push your-registry/ailien-platform:latest
```

### Directory Structure
```
ailien-platform-k8s/
├── app/                    # Application source code
├── docker/                 # Docker configuration
├── helm/                   # Helm charts
├── .github/workflows/      # CI/CD pipelines
├── k8s/                    # Kubernetes manifests
├── docs/                   # Documentation
└── scripts/                # Deployment scripts
```