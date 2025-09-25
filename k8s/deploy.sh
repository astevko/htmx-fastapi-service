#!/bin/bash

# Kubernetes deployment script for HTMX FastAPI Service

set -e

echo "🚀 Deploying HTMX FastAPI Service to Kubernetes"
echo "================================================"

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed or not in PATH"
    echo "Please install kubectl: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

# Check if Docker Desktop Kubernetes is running
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Kubernetes cluster is not accessible"
    echo "Please ensure Docker Desktop Kubernetes is enabled and running"
    exit 1
fi

echo "✅ kubectl is available and cluster is accessible"

# Apply manifests in order
echo ""
echo "📦 Creating namespace..."
kubectl apply -f namespace.yaml

echo "⚙️  Creating ConfigMap..."
kubectl apply -f configmap.yaml

echo "🚀 Deploying application..."
kubectl apply -f deployment.yaml

echo "🔗 Creating ClusterIP service..."
kubectl apply -f service.yaml

# Ask user which service type to use
echo ""
echo "Choose service type:"
echo "1) ClusterIP (internal access only)"
echo "2) NodePort (accessible on localhost:30080)"
echo "3) Ingress (requires ingress controller)"
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo "✅ Using ClusterIP service"
        echo "📝 To access the service, use port-forwarding:"
        echo "   kubectl port-forward -n htmx-fastapi svc/htmx-fastapi-service 8000:8000"
        echo "   Then visit: http://localhost:8000"
        ;;
    2)
        echo "🌐 Creating NodePort service..."
        kubectl apply -f service-nodeport.yaml
        echo "✅ Service accessible at: http://localhost:30080"
        ;;
    3)
        echo "🌐 Creating Ingress..."
        kubectl apply -f ingress.yaml
        echo "✅ Ingress created"
        echo "📝 Add to /etc/hosts: 127.0.0.1 htmx-fastapi.local"
        echo "   Then visit: http://htmx-fastapi.local"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "⏳ Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/htmx-fastapi-deployment -n htmx-fastapi

echo ""
echo "📊 Deployment status:"
kubectl get pods -n htmx-fastapi
kubectl get services -n htmx-fastapi

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Useful commands:"
echo "  View logs:     kubectl logs -n htmx-fastapi deployment/htmx-fastapi-deployment -f"
echo "  Scale up:      kubectl scale -n htmx-fastapi deployment/htmx-fastapi-deployment --replicas=3"
echo "  Port forward:  kubectl port-forward -n htmx-fastapi svc/htmx-fastapi-service 8000:8000"
echo "  Delete all:    kubectl delete namespace htmx-fastapi"
