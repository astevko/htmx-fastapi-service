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

## DuckDB Database Management

This application uses DuckDB as its embedded database for message storage. A web-based management interface (Duck-UI) is available for database administration.

### Starting Duck-UI

**Option 1: Using the convenience script**
```bash
./scripts/start-duck-ui.sh
```

**Option 2: Using Docker Compose directly**
```bash
# Development mode
docker-compose --profile dev up -d duck-ui

# Production mode (includes Duck-UI)
docker-compose -f docker-compose.prod.yml up -d
```

### Accessing Duck-UI

Once started, Duck-UI will be available at: **http://localhost:5522**

### Duck-UI Features

- **Database Browser**: View all tables, schemas, and data
- **SQL Query Interface**: Execute SQL queries directly
- **Data Visualization**: Explore your message data
- **Database Management**: Create, modify, and delete tables

### Database Schema

The application creates the following schema:

```sql
CREATE SEQUENCE id_sequence START 1;
CREATE TABLE messages (
    id INTEGER DEFAULT nextval('id_sequence'),
    text VARCHAR NOT NULL,
    timestamp TIMESTAMP NOT NULL
);
```

### Useful SQL Queries

```sql
-- View all messages
SELECT * FROM messages ORDER BY timestamp DESC;

-- Count total messages
SELECT COUNT(*) FROM messages;

-- Messages from last 24 hours
SELECT * FROM messages 
WHERE timestamp >= now() - INTERVAL '1 day'
ORDER BY timestamp DESC;

-- Most active time periods
SELECT 
    DATE_TRUNC('hour', timestamp) as hour,
    COUNT(*) as message_count
FROM messages 
GROUP BY hour 
ORDER BY hour DESC;
```

### Data Persistence

- **Development**: Database files are stored in Docker volumes
- **Production**: Persistent storage with `duckdb_data` volume
- **Backup**: Database files are automatically backed up with container volumes

## Database Management Scripts

The project includes comprehensive scripts for database backup, restore, and export operations.

### Quick Start

**Interactive Database Management:**
```bash
./scripts/db-manage.sh
```

### Available Scripts

#### **1. Database Management (Interactive)**
```bash
./scripts/db-manage.sh
```
- Interactive menu for all database operations
- Backup, restore, export, statistics, and maintenance
- User-friendly interface with colored output

#### **2. Database Backup**
```bash
# Basic backup
./scripts/backup-duckdb.sh

# Compressed backup
./scripts/backup-duckdb.sh -c

# Custom options
./scripts/backup-duckdb.sh -d /path/to/db.duckdb -o /backups -c -k 5
```

**Backup Options:**
- `-d, --database`: Database file path
- `-o, --output`: Backup directory
- `-c, --compress`: Compress backup files
- `-r, --remote`: Upload to remote server
- `-k, --keep`: Keep N recent backups

#### **3. Database Restore**
```bash
# Interactive restore (list available backups)
./scripts/restore-duckdb.sh

# Restore specific backup
./scripts/restore-duckdb.sh messages_backup_20241201_143022.duckdb

# Force restore without confirmation
./scripts/restore-duckdb.sh -f backup.duckdb
```

**Restore Options:**
- `-l, --list`: List available backups
- `-d, --database`: Target database path
- `-f, --force`: Force restore without confirmation

#### **4. Data Export**
```bash
# Export all tables to CSV
./scripts/export-duckdb.sh

# Export to JSON
./scripts/export-duckdb.sh -f json

# Export specific table
./scripts/export-duckdb.sh -t messages -f json

# Export with custom query
./scripts/export-duckdb.sh -q "SELECT * FROM messages WHERE text LIKE '%test%'" -f csv
```

**Export Formats:**
- `csv`: Comma-separated values
- `json`: JSON format
- `sql`: SQL INSERT statements
- `parquet`: Apache Parquet format

### Backup Strategy

#### **Automated Backups**
```bash
# Add to crontab for daily backups
0 2 * * * /path/to/project/scripts/backup-duckdb.sh -c -k 30
```

#### **Backup Retention**
- **Development**: Keep 10 recent backups
- **Production**: Keep 30+ backups with compression
- **Remote Storage**: Upload to cloud storage for long-term retention

### Data Export Examples

#### **Export All Data**
```bash
# Export everything to CSV
./scripts/export-duckdb.sh -f csv

# Export to Parquet for analytics
./scripts/export-duckdb.sh -f parquet
```

#### **Custom Queries**
```bash
# Recent messages
./scripts/export-duckdb.sh -q "SELECT * FROM messages WHERE timestamp >= now() - INTERVAL '7 days'" -f json

# Message statistics
./scripts/export-duckdb.sh -q "SELECT DATE_TRUNC('day', timestamp) as day, COUNT(*) as count FROM messages GROUP BY day" -f csv

# Search messages
./scripts/export-duckdb.sh -q "SELECT * FROM messages WHERE text LIKE '%error%'" -f sql
```

### Database Maintenance

#### **Regular Maintenance**
```bash
# Run database maintenance
./scripts/db-manage.sh
# Select option 7: Database maintenance
```

#### **Statistics and Monitoring**
```bash
# View database statistics
./scripts/db-manage.sh
# Select option 5: Database statistics
```

### Disaster Recovery

#### **Full Restore Process**
1. **Stop Application**: Ensure no writes to database
2. **Create Emergency Backup**: `./scripts/backup-duckdb.sh -c`
3. **Restore Database**: `./scripts/restore-duckdb.sh`
4. **Verify Data**: Check statistics and test queries
5. **Restart Application**: Resume normal operations

#### **Data Validation**
```bash
# Export and verify data integrity
./scripts/export-duckdb.sh -f csv
./scripts/export-duckdb.sh -q "SELECT COUNT(*) FROM messages"
```

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

## Kubernetes Deployment

Deploy to Kubernetes (Docker Desktop) with the included manifests:

### Quick Start

```bash
# Deploy with NodePort (accessible on localhost:30080)
cd k8s
./deploy.sh
# Choose option 2

# Access the application
open http://localhost:30080
```

### Manual Deployment

```bash
# Create namespace and deploy
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service-nodeport.yaml

# Access at http://localhost:30080
```

### Features

- **2 replicas** for high availability
- **Health checks** with liveness and readiness probes
- **Resource limits** and security context
- **Multiple access methods**: NodePort, ClusterIP, Ingress
- **Easy cleanup** with provided scripts

For detailed Kubernetes deployment instructions, see [k8s/README.md](k8s/README.md).

## License

This project is open source and available under the [MIT License](LICENSE).
