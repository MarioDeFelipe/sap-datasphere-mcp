#!/bin/bash
# Ailien Platform - Helm Deployment Script

set -e

# Configuration
NAMESPACE=${1:-"default"}
RELEASE_NAME=${2:-"ailien-platform"}
VERSION=${3:-"latest"}

echo "⚓ Ailien Platform - Helm Deployment"
echo "===================================="
echo "Namespace: $NAMESPACE"
echo "Release: $RELEASE_NAME"
echo "Version: $VERSION"
echo ""

# Check if kubectl is configured
if ! kubectl cluster-info > /dev/null 2>&1; then
    echo "❌ kubectl is not configured or cluster is not accessible"
    exit 1
fi

# Check if Helm is installed
if ! command -v helm &> /dev/null; then
    echo "❌ Helm is not installed. Please install Helm first."
    exit 1
fi

# Create namespace if it doesn't exist
echo "📁 Creating namespace if needed..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Deploy with Helm
echo "🚀 Deploying with Helm..."
helm upgrade --install $RELEASE_NAME ./helm/ailien-platform \
    --namespace $NAMESPACE \
    --set image.tag=$VERSION \
    --wait \
    --timeout=300s

echo "✅ Deployment completed!"
echo ""
echo "📋 Useful commands:"
echo "  kubectl get pods -n $NAMESPACE"
echo "  kubectl logs -f deployment/$RELEASE_NAME -n $NAMESPACE"
echo "  helm status $RELEASE_NAME -n $NAMESPACE"
echo "  helm uninstall $RELEASE_NAME -n $NAMESPACE"