#!/bin/bash
# Ailien Platform - Build and Push Docker Image

set -e

# Configuration
REGISTRY="ghcr.io"
IMAGE_NAME="ailien-studio/ailien-platform"
VERSION=${1:-"latest"}

echo "🐳 Ailien Platform - Build and Push"
echo "===================================="
echo "Registry: $REGISTRY"
echo "Image: $IMAGE_NAME"
echo "Version: $VERSION"
echo ""

# Build the image
echo "📦 Building Docker image..."
docker build -t $IMAGE_NAME:$VERSION .
docker tag $IMAGE_NAME:$VERSION $REGISTRY/$IMAGE_NAME:$VERSION

# Push to registry
echo "📤 Pushing to registry..."
docker push $REGISTRY/$IMAGE_NAME:$VERSION

echo "✅ Image pushed successfully!"
echo "🔗 Image: $REGISTRY/$IMAGE_NAME:$VERSION"