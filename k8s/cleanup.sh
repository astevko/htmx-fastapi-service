#!/bin/bash

# Kubernetes cleanup script for HTMX FastAPI Service

set -e

echo "🧹 Cleaning up HTMX FastAPI Service from Kubernetes"
echo "=================================================="

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed or not in PATH"
    exit 1
fi

echo "🗑️  Deleting namespace and all resources..."
kubectl delete namespace htmx-fastapi --ignore-not-found=true

echo ""
echo "✅ Cleanup completed!"
echo "📝 All HTMX FastAPI Service resources have been removed from Kubernetes"
