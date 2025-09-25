# Kubernetes Deployment for HTMX FastAPI Service

This directory contains Kubernetes manifests for deploying the HTMX FastAPI service on Docker Desktop.

## Prerequisites

- Docker Desktop with Kubernetes enabled
- kubectl installed and configured
- Docker image `andystevko/htmx-fastapi-service:latest` available locally or from Docker Hub

## Quick Start

### Deploy with NodePort (Recommended for local testing)

```bash
# Deploy the application
./deploy.sh
# Choose option 2 for NodePort

# Access the application
open http://localhost:30080
```

### Deploy with Port Forwarding

```bash
# Deploy with ClusterIP service
./deploy.sh
# Choose option 1 for ClusterIP

# Port forward to access locally
kubectl port-forward -n htmx-fastapi svc/htmx-fastapi-service 8000:8000

# Access the application
open http://localhost:8000
```

## Manual Deployment

### 1. Create Namespace and ConfigMap

```bash
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
```

### 2. Deploy Application

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

### 3. Choose Access Method

#### Option A: NodePort (Easiest)

```bash
kubectl apply -f service-nodeport.yaml
# Access at http://localhost:30080
```

#### Option B: Port Forwarding

```bash
kubectl port-forward -n htmx-fastapi svc/htmx-fastapi-service 8000:8000
# Access at http://localhost:8000
```

#### Option C: Ingress (Requires ingress controller)

```bash
kubectl apply -f ingress.yaml
# Add to /etc/hosts: 127.0.0.1 htmx-fastapi.local
# Access at http://htmx-fastapi.local
```

## Configuration

### Environment Variables

The application is configured via ConfigMap (`configmap.yaml`):

- `PYTHONPATH`: Application path
- `PYTHONUNBUFFERED`: Python output buffering
- `LOG_LEVEL`: Logging level
- `HOST`: Server host (0.0.0.0 for container)
- `PORT`: Server port (8000)

### Resource Limits

- **Requests**: 128Mi memory, 100m CPU
- **Limits**: 512Mi memory, 500m CPU

### Health Checks

- **Liveness Probe**: HTTP GET on `/` every 10 seconds
- **Readiness Probe**: HTTP GET on `/` every 5 seconds

## Monitoring and Debugging

### View Logs

```bash
# Follow logs from all pods
kubectl logs -n htmx-fastapi deployment/htmx-fastapi-deployment -f

# View logs from specific pod
kubectl logs -n htmx-fastapi <pod-name> -f
```

### Check Status

```bash
# Pod status
kubectl get pods -n htmx-fastapi

# Service status
kubectl get services -n htmx-fastapi

# Deployment status
kubectl get deployments -n htmx-fastapi

# Describe resources for detailed info
kubectl describe deployment htmx-fastapi-deployment -n htmx-fastapi
```

### Scale Application

```bash
# Scale to 3 replicas
kubectl scale -n htmx-fastapi deployment/htmx-fastapi-deployment --replicas=3

# Scale to 1 replica
kubectl scale -n htmx-fastapi deployment/htmx-fastapi-deployment --replicas=1
```

## Security Features

- **Non-root user**: Container runs as user 1000
- **Privilege escalation disabled**: `allowPrivilegeEscalation: false`
- **Dropped capabilities**: All Linux capabilities dropped
- **Security context**: Restricted security context applied

## Cleanup

### Remove Everything

```bash
./cleanup.sh
```

### Manual Cleanup

```bash
kubectl delete namespace htmx-fastapi
```

## Troubleshooting

### Container Won't Start

1. Check pod logs:
   ```bash
   kubectl logs -n htmx-fastapi deployment/htmx-fastapi-deployment
   ```

2. Check pod status:
   ```bash
   kubectl describe pod -n htmx-fastapi <pod-name>
   ```

### Service Not Accessible

1. Check service endpoints:
   ```bash
   kubectl get endpoints -n htmx-fastapi
   ```

2. Test service connectivity:
   ```bash
   kubectl port-forward -n htmx-fastapi svc/htmx-fastapi-service 8000:8000
   curl http://localhost:8000
   ```

### Image Pull Issues

1. Ensure Docker image exists:
   ```bash
   docker images | grep andystevko/htmx-fastapi-service
   ```

2. Pull latest image:
   ```bash
   docker pull andystevko/htmx-fastapi-service:latest
   ```

## Files Overview

- `namespace.yaml` - Creates the `htmx-fastapi` namespace
- `configmap.yaml` - Application configuration
- `deployment.yaml` - Application deployment with 2 replicas
- `service.yaml` - ClusterIP service for internal access
- `service-nodeport.yaml` - NodePort service for external access
- `ingress.yaml` - Ingress for domain-based access (requires ingress controller)
- `deploy.sh` - Automated deployment script
- `cleanup.sh` - Cleanup script
- `README.md` - This documentation

## Production Considerations

For production deployments, consider:

1. **Resource limits**: Adjust based on actual usage
2. **Replica count**: Scale based on load
3. **Ingress controller**: Use proper ingress controller (nginx, traefik)
4. **SSL/TLS**: Configure HTTPS certificates
5. **Monitoring**: Add Prometheus/Grafana monitoring
6. **Logging**: Centralized logging with ELK stack
7. **Secrets**: Use Kubernetes secrets for sensitive data
8. **ConfigMaps**: Externalize all configuration
9. **Health checks**: Fine-tune probe timings
10. **Security**: Network policies, pod security standards
