# HTMX FastAPI Service

[![Docker Build and Test](https://github.com/astevko/htmx-fastapi-service/actions/workflows/docker-test.yml/badge.svg)](https://github.com/astevko/htmx-fastapi-service/actions/workflows/docker-test.yml)
[![Docker Hub](https://img.shields.io/docker/v/andystevko/htmx-fastapi-service?label=docker%20hub)](https://hub.docker.com/r/andystevko/htmx-fastapi-service)
[![GitHub Container Registry](https://img.shields.io/badge/GHCR-available-blue)](https://github.com/astevko/htmx-fastapi-service/pkgs/container/htmx-fastapi-service)

A modern web application built with FastAPI and HTMX, demonstrating server-side rendering with dynamic interactions.

## Features

- **FastAPI**: Modern, fast web framework for building APIs
- **HTMX**: Dynamic HTML interactions without writing JavaScript
- **Jinja2 Templates**: Server-side templating engine
- **Tailwind CSS**: Utility-first CSS framework for styling
- **uv**: Fast Python package manager and project manager

## Project Structure

```
htmx-fastapi-service/
├── main.py                 # FastAPI application
├── pyproject.toml          # Project configuration and dependencies
├── templates/              # Jinja2 HTML templates
│   ├── index.html         # Main page template
│   ├── message_partial.html # Message partial template
│   └── messages_list.html  # Messages list template
├── static/                 # Static files (CSS, JS, images)
│   ├── css/
│   └── js/
└── README.md              # This file
```

## Getting Started

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

1. Clone or navigate to the project directory:
   ```bash
   cd htmx-fastapi-service
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Run the development server:
   ```bash
   uv run python main.py
   ```

   Or alternatively:
   ```bash
   uv run uvicorn main:app --reload
   ```

4. Open your browser and visit: http://localhost:8000

## Development

### Adding Dependencies

To add new dependencies:
```bash
uv add package-name
```

To add development dependencies:
```bash
uv add --dev package-name
```

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run black .
uv run isort .
```

## API Endpoints

- `GET /` - Home page with HTMX demo
- `POST /api/message` - Create a new message (HTMX endpoint)
- `GET /api/messages` - Get all messages (HTMX endpoint)

## HTMX Features Demonstrated

- **Form Submission**: Adding messages without page refresh
- **Dynamic Content Loading**: Refreshing messages list
- **Partial Updates**: Updating specific parts of the page
- **Server-Side Rendering**: Templates rendered on the server

## Technologies Used

- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [HTMX](https://htmx.org/) - Dynamic HTML
- [Jinja2](https://jinja.palletsprojects.com/) - Template engine
- [Tailwind CSS](https://tailwindcss.com/) - CSS framework
- [uv](https://docs.astral.sh/uv/) - Python package manager
- [Uvicorn](https://www.uvicorn.org/) - ASGI server

## Docker Deployment

### Development Mode

Run the application in development mode with hot reloading:

```bash
# Using Docker Compose
docker-compose up --build

# Or using the convenience script
./scripts/docker-dev.sh
```

The application will be available at:
- **Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Production Mode

Deploy the application in production mode with Nginx reverse proxy:

```bash
# Using Docker Compose
docker-compose -f docker-compose.prod.yml up --build -d

# Or using the convenience script
./scripts/docker-prod.sh
```

The application will be available at:
- **Application**: http://localhost (port 80)
- **API Documentation**: http://localhost/docs

### Docker Commands

```bash
# Validate Docker setup
./scripts/validate-docker.sh

# Build the image
docker build -t htmx-fastapi-service .

# Run the container
docker run -p 8000:8000 htmx-fastapi-service

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build --force-recreate
```

### Production Features

- **Nginx Reverse Proxy**: Handles static files and load balancing
- **Health Checks**: Automatic container health monitoring
- **Security Headers**: XSS protection, content type options, etc.
- **Rate Limiting**: API rate limiting to prevent abuse
- **Gzip Compression**: Automatic compression for better performance
- **Resource Limits**: Memory and CPU limits for containers

## GitHub Actions CI/CD

This project includes automated CI/CD workflows for building and publishing Docker images:

### Available Workflows

- **`docker-test.yml`**: Builds and tests Docker image on every push/PR
- **`docker-build.yml`**: Publishes to Docker Hub on main branch and tags
- **`docker-publish-ghcr.yml`**: Publishes to GitHub Container Registry

### Setup for Docker Hub Publishing

**Note**: Your GitHub username and Docker Hub username can be different. This project uses `andystevko` as the Docker Hub username.

1. Create a Docker Hub account at [hub.docker.com](https://hub.docker.com)
2. Create an access token in Docker Hub settings
3. Add these secrets to your GitHub repository:
   - `DOCKER_USERNAME`: `andystevko` (your Docker Hub username)
   - `DOCKER_TOKEN`: Your Docker Hub access token

### Automatic Features

- **Multi-platform builds**: AMD64 and ARM64 support
- **Security scanning**: Trivy vulnerability scanning
- **Automatic tagging**: Based on branches and git tags
- **Cache optimization**: Faster builds with GitHub Actions cache

### Pulling Images

```bash
# Docker Hub (uses Docker Hub username: andystevko)
docker pull andystevko/htmx-fastapi-service:latest

# GitHub Container Registry (uses GitHub username: astevko)
docker pull ghcr.io/astevko/htmx-fastapi-service:latest
```

For detailed setup instructions, see [.github/README.md](.github/README.md).

## License

This project is open source and available under the [MIT License](LICENSE).
