# GitHub Actions Workflows

This repository includes several GitHub Actions workflows for building, testing, and publishing Docker images.

## Workflows

### 1. Docker Build and Test (`docker-test.yml`)
- **Triggers**: Push to `main`/`develop` branches, Pull Requests to `main`
- **Purpose**: Build and test Docker image without publishing
- **Features**:
  - Builds Docker image
  - Runs health checks
  - Tests API endpoints
  - Tests timezone functionality
  - Security scanning with Trivy

### 2. Docker Hub Publishing (`docker-build.yml`)
- **Triggers**: Push to `main`/`develop` branches, Tags starting with `v`
- **Purpose**: Build and publish to Docker Hub
- **Features**:
  - Multi-platform builds (AMD64, ARM64)
  - Automatic tagging based on branch/tag
  - Security scanning
  - Staging and production deployment hooks

### 3. GitHub Container Registry (`docker-publish-ghcr.yml`)
- **Triggers**: Push to `main` branch, Tags starting with `v`
- **Purpose**: Build and publish to GitHub Container Registry
- **Features**:
  - Multi-platform builds
  - Automatic tagging
  - Security scanning
  - Uses GitHub token for authentication

## Setup Instructions

### For Docker Hub Publishing

**Note**: Your GitHub username and Docker Hub username can be different. The workflows are configured to use `andystevko` as the Docker Hub username.

1. **Create Docker Hub Account**: Sign up at [hub.docker.com](https://hub.docker.com)

2. **Create Access Token**:
   - Go to Docker Hub → Account Settings → Security
   - Create a new access token
   - Copy the token

3. **Add Secrets to GitHub Repository**:
   - Go to your GitHub repository → Settings → Secrets and variables → Actions
   - Add the following secrets:
     - `DOCKER_USERNAME`: `andystevko` (your Docker Hub username)
     - `DOCKER_TOKEN`: Your Docker Hub access token

### For GitHub Container Registry

No additional setup required! The workflow uses the built-in `GITHUB_TOKEN`.

## Image Tags

The workflows automatically create tags based on:

- **Branch pushes**: `main`, `develop`
- **Pull requests**: `pr-123`
- **Tags**: `v1.0.0`, `v1.0`, `v1`, `latest` (for main branch)

## Security Features

- **Trivy Security Scanning**: Scans for vulnerabilities
- **Multi-platform builds**: Supports AMD64 and ARM64
- **Cache optimization**: Uses GitHub Actions cache for faster builds
- **Permission controls**: Minimal required permissions

## Usage Examples

### Pulling Images

**Docker Hub**:
```bash
docker pull andystevko/htmx-fastapi-service:latest
docker pull andystevko/htmx-fastapi-service:v1.0.0
```

**GitHub Container Registry**:
```bash
docker pull ghcr.io/andystevko/htmx-fastapi-service:latest
docker pull ghcr.io/andystevko/htmx-fastapi-service:v1.0.0
```

### Running Images

```bash
# Run with default settings
docker run -p 8000:8000 andystevko/htmx-fastapi-service:latest

# Run with environment variables
docker run -p 8000:8000 -e PYTHONPATH=/app andystevko/htmx-fastapi-service:latest
```

## Troubleshooting

### Common Issues

1. **Build Failures**: Check the Actions logs for specific error messages
2. **Authentication Errors**: Verify Docker Hub credentials are correct
3. **Permission Errors**: Ensure repository has proper permissions for packages

### Manual Testing

You can test the Docker image locally:

```bash
# Build the image
docker build -t htmx-fastapi-service .

# Run the container
docker run -p 8000:8000 htmx-fastapi-service

# Test the endpoints
curl http://localhost:8000/
curl http://localhost:8000/api/messages
```

## Contributing

When contributing to this repository:

1. Create a feature branch
2. Make your changes
3. Create a pull request
4. The workflows will automatically test your changes
5. Once merged, images will be automatically built and published
