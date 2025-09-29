# HTMX-FastAPI Service Architecture Report

## 🏗️ Project Overview

**HTMX-FastAPI Service** is a modern web application demonstrating server-side rendering with dynamic interactions using FastAPI and HTMX. This project showcases a complete full-stack solution with authentication, real-time messaging, and comprehensive deployment strategies.

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│  🌐 Browser (HTMX + Tailwind CSS)                              │
│  ├── Login Interface                                           │
│  ├── Message Dashboard                                         │
│  └── Real-time Updates                                        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ HTTPS/HTTP
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    REVERSE PROXY LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│  🔄 Nginx (Production)                                         │
│  ├── Rate Limiting (10 req/s API, 5 req/min login)            │
│  ├── Gzip Compression                                          │
│  ├── Security Headers                                          │
│  ├── Static File Caching                                       │
│  └── Load Balancing                                            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ Internal Network
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│  🚀 FastAPI Application                                        │
│  ├── JWT Authentication                                        │
│  ├── HTMX Endpoints                                            │
│  ├── Jinja2 Templates                                          │
│  ├── Timezone Support                                          │
│  └── Health Checks                                             │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ SQLAlchemy ORM
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│  🗄️ PostgreSQL Database                                       │
│  ├── Messages Table                                            │
│  ├── Auto-incrementing IDs                                     │
│  ├── UTC Timestamps                                            │
│  └── Connection Pooling                                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Core Features

### 🔐 Authentication System
- **JWT Token-based Authentication**
  - Secure token generation with HS256 algorithm
  - 30-minute token expiration
  - HttpOnly cookies for security
  - Timezone-aware sessions

- **Demo User Credentials**
  - Username: `user@example.com`
  - Password: `12341234`
  - SHA-256 password hashing (demo implementation)

### 💬 Real-time Messaging
- **HTMX-powered Dynamic Updates**
  - Form submissions without page refresh
  - Real-time message display
  - Automatic message loading on page load
  - Partial template updates

- **Message Management**
  - Store messages with timestamps
  - Retrieve messages in descending order
  - Timezone-aware timestamp formatting
  - Search and filtering capabilities

### 🌍 Timezone Support
- **Automatic Timezone Detection**
  - Browser-based timezone detection
  - Server-side timezone conversion
  - User-specific timezone preferences
  - UTC storage with local display

---

## 🛠️ Technology Stack

### Backend Technologies
| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | 0.117.1+ | Modern web framework with automatic API docs |
| **Python** | 3.13+ | Core programming language |
| **SQLAlchemy** | 2.0.0+ | ORM for database operations |
| **PostgreSQL** | 16-alpine | Primary database |
| **psycopg** | 3.2.10+ | PostgreSQL adapter |
| **python-jose** | 3.3.0+ | JWT token handling |
| **pytz** | 2025.2+ | Timezone handling |
| **uvicorn** | 0.37.0+ | ASGI server |

### Frontend Technologies
| Technology | Version | Purpose |
|------------|---------|---------|
| **HTMX** | 1.9.10 | Dynamic HTML interactions |
| **Tailwind CSS** | 2.2.19 | Utility-first CSS framework |
| **Jinja2** | 3.1.6+ | Server-side templating |
| **JavaScript** | Native | Timezone detection |

### Development Tools
| Tool | Purpose |
|------|---------|
| **uv** | Fast Python package manager |
| **pytest** | Testing framework |
| **black** | Code formatting |
| **isort** | Import sorting |
| **flake8** | Linting |

---

## 🐳 Deployment Architecture

### Development Environment
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Service   │    │   PostgreSQL    │    │   Redis Cache   │
│   Port: 8000    │◄──►│   Port: 5432    │    │   Port: 6379    │
│   Hot Reload    │    │   Development   │    │   (Optional)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Production Environment
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │    │   Web Service   │    │   PostgreSQL    │
│   Port: 80/443  │◄──►│   Port: 8000    │◄──►│   Port: 5432    │
│   Reverse Proxy │    │   Internal      │    │   Persistent    │
│   SSL/TLS       │    │   Health Checks │    │   Storage       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Kubernetes Deployment
```
┌─────────────────────────────────────────────────────────────────┐
│                        Kubernetes Cluster                       │
├─────────────────────────────────────────────────────────────────┤
│  📦 Namespace: htmx-fastapi                                     │
│  ├── 🚀 Deployment (2 replicas)                              │
│  │   ├── Container: htmx-fastapi-service                       │
│  │   ├── Resources: 128Mi-512Mi memory, 100m-500m CPU          │
│  │   ├── Health Checks: Liveness & Readiness probes           │
│  │   └── Security: Non-root user, dropped capabilities        │
│  ├── 🌐 Service (NodePort: 30080)                             │
│  ├── 📋 ConfigMap (Environment variables)                     │
│  └── 🔧 Ingress (Optional)                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔌 API Endpoints

### Authentication Endpoints
| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| `GET` | `/` | Login page | None |
| `POST` | `/api/login` | User authentication | None |
| `GET` | `/api/logout` | User logout | JWT Cookie |

### Message Endpoints
| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| `GET` | `/msgs` | Messages dashboard | JWT Cookie |
| `POST` | `/api/message` | Create new message | JWT Cookie |
| `GET` | `/api/messages` | Get all messages | JWT Cookie |

### Static Resources
| Resource | Path | Description |
|----------|------|-------------|
| CSS | `/static/css/style.css` | Custom styles |
| JS | `/static/js/` | JavaScript files |

---

## 🗄️ Database Schema

### Messages Table
```sql
CREATE SEQUENCE id_sequence START 1;

CREATE TABLE messages (
    id INTEGER DEFAULT nextval('id_sequence'),
    text VARCHAR NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### Data Models
```python
# Pydantic Models
class MessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)

class MessageResponse(BaseModel):
    text: str
    timestamp: str

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=100)
    user_timezone: str = Field(..., min_length=1, max_length=50)

# SQLAlchemy Models
class MessageDB(Base):
    __tablename__ = "messages"
    id = Column(Integer, Sequence('id_sequence'), primary_key=True)
    text = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
```

---

## 🔒 Security Features

### Authentication Security
- **JWT Tokens**: Secure token-based authentication
- **HttpOnly Cookies**: Prevents XSS attacks
- **Password Hashing**: SHA-256 hashing (demo implementation)
- **Session Management**: Timezone-aware sessions

### Network Security
- **Rate Limiting**: 10 req/s for API, 5 req/min for login
- **Security Headers**: XSS protection, content type options
- **HTTPS Support**: SSL/TLS configuration ready
- **CORS Protection**: Same-origin policy enforcement

### Container Security
- **Non-root User**: Application runs as non-privileged user
- **Resource Limits**: Memory and CPU constraints
- **Health Checks**: Automatic container monitoring
- **Security Context**: Dropped capabilities

---

## 🚀 CI/CD Pipeline

### GitHub Actions Workflows
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Code Push     │    │   Build & Test  │    │   Deploy        │
│   (Any Branch)  │───►│   Docker Image │───►│   Multi-Registry│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Security Scan   │
                       │ (Trivy)         │
                       └─────────────────┘
```

### Deployment Targets
- **Docker Hub**: `andystevko/htmx-fastapi-service`
- **GitHub Container Registry**: `ghcr.io/astevko/htmx-fastapi-service`
- **Multi-platform**: AMD64 and ARM64 support

---

## 📈 Performance Features

### Caching Strategy
- **Static File Caching**: 1-year cache for static assets
- **Nginx Caching**: Reverse proxy caching
- **Database Connection Pooling**: SQLAlchemy connection pooling

### Optimization Features
- **Gzip Compression**: Automatic compression for text assets
- **Resource Limits**: Memory and CPU constraints
- **Health Monitoring**: Liveness and readiness probes
- **Load Balancing**: Multiple replica support

---

## 🔧 Development Workflow

### Local Development
```bash
# Install dependencies
uv sync

# Run development server
uv run python main.py

# Run tests
uv run pytest

# Format code
uv run black .
uv run isort .
```

### Docker Development
```bash
# Development with hot reload
docker-compose up --build

# Production deployment
docker-compose -f docker-compose.prod.yml up --build -d
```

### Kubernetes Deployment
```bash
# Deploy to Kubernetes
cd k8s
./deploy.sh

# Access application
open http://localhost:30080
```

---

## 📊 Monitoring & Observability

### Health Checks
- **Application Health**: HTTP endpoint monitoring
- **Database Health**: Connection testing
- **Container Health**: Docker health checks
- **Kubernetes Probes**: Liveness and readiness

### Logging
- **Structured Logging**: Python logging with levels
- **Nginx Access Logs**: Request tracking
- **Error Logging**: Comprehensive error tracking
- **Debug Logging**: Development debugging

---

## 🎨 Frontend Architecture

### HTMX Integration
```html
<!-- Form submission without page refresh -->
<form hx-post="/api/message" hx-target="#messages-container" hx-swap="afterbegin">
    <input type="text" name="message" placeholder="Enter your message...">
    <button type="submit">Send</button>
</form>

<!-- Real-time message loading -->
<div id="messages-container" hx-get="/api/messages" hx-trigger="load">
    <!-- Messages loaded automatically -->
</div>
```

### Responsive Design
- **Mobile-first**: Responsive design with Tailwind CSS
- **Progressive Enhancement**: Works without JavaScript
- **Accessibility**: Semantic HTML and ARIA labels
- **Performance**: Optimized CSS and minimal JavaScript

---

## 🔄 Data Flow

### Message Creation Flow
```
1. User submits form → HTMX intercepts
2. POST /api/message → FastAPI endpoint
3. JWT validation → Authentication check
4. Message storage → PostgreSQL database
5. Template rendering → Jinja2 partial
6. DOM update → HTMX swap
7. User sees new message → Real-time update
```

### Authentication Flow
```
1. User enters credentials → Login form
2. POST /api/login → FastAPI endpoint
3. Password verification → Hash comparison
4. JWT generation → Token creation
5. Cookie setting → HttpOnly cookies
6. Redirect → HTMX redirect header
7. Dashboard access → Authenticated user
```

---

## 📋 Project Structure

```
htmx-fastapi-service/
├── 📁 k8s/                    # Kubernetes manifests
│   ├── deployment.yaml        # K8s deployment config
│   ├── service.yaml          # K8s service config
│   ├── configmap.yaml        # Environment variables
│   └── deploy.sh            # Deployment script
├── 📁 scripts/               # Utility scripts
│   ├── docker-dev.sh        # Development Docker
│   ├── docker-prod.sh        # Production Docker
│   └── db-manage.sh         # Database management
├── 📁 static/                # Static assets
│   ├── css/style.css        # Custom styles
│   └── js/                  # JavaScript files
├── 📁 templates/             # Jinja2 templates
│   ├── index.html           # Login page
│   ├── msgs.html            # Messages dashboard
│   ├── message_partial.html # Message partial
│   └── messages_list.html   # Messages list
├── 📄 main.py               # FastAPI application
├── 📄 models.py             # Pydantic models
├── 📄 database.py           # Database configuration
├── 📄 messages.py           # Message operations
├── 📄 pyproject.toml        # Project dependencies
├── 📄 Dockerfile            # Container definition
├── 📄 docker-compose.yml    # Development compose
├── 📄 docker-compose.prod.yml # Production compose
└── 📄 nginx.conf            # Nginx configuration
```

---

## 🎯 Key Integrations

### External Services
- **Docker Hub**: Container image registry
- **GitHub Container Registry**: Alternative registry
- **GitHub Actions**: CI/CD pipeline
- **Kubernetes**: Container orchestration

### Development Tools
- **uv**: Package management
- **pytest**: Testing framework
- **black/isort**: Code formatting
- **flake8**: Code linting

### Production Tools
- **Nginx**: Reverse proxy and load balancer
- **PostgreSQL**: Primary database
- **Docker**: Containerization
- **Kubernetes**: Orchestration platform

---

## 🚀 Future Enhancements

### Planned Features
- **User Management**: Multi-user support with registration
- **Message Threading**: Reply and conversation features
- **File Uploads**: Image and file sharing
- **Real-time Notifications**: WebSocket integration
- **Advanced Search**: Full-text search capabilities

### Technical Improvements
- **Database Migrations**: Alembic integration
- **Caching Layer**: Redis integration
- **Monitoring**: Prometheus and Grafana
- **Logging**: Structured logging with ELK stack
- **Security**: OAuth2 and RBAC implementation

---

## 📊 Performance Metrics

### Resource Usage
- **Memory**: 128Mi-512Mi per container
- **CPU**: 100m-500m per container
- **Storage**: Persistent PostgreSQL volumes
- **Network**: Optimized with connection pooling

### Scalability
- **Horizontal Scaling**: Multiple replicas supported
- **Load Balancing**: Nginx upstream configuration
- **Database Scaling**: Connection pooling and optimization
- **Caching**: Multi-layer caching strategy

---

## 🎉 Conclusion

The HTMX-FastAPI Service represents a modern, production-ready web application that demonstrates best practices in:

- **Full-stack Development**: FastAPI backend with HTMX frontend
- **Containerization**: Docker and Kubernetes deployment
- **Security**: JWT authentication and security headers
- **Performance**: Caching, compression, and optimization
- **DevOps**: CI/CD pipelines and automated deployment
- **Monitoring**: Health checks and observability

This architecture provides a solid foundation for building scalable, maintainable web applications with modern technologies and deployment strategies.

---

*Generated on: $(date)*
*Project Version: 0.1.0*
*Architecture Report Version: 1.0*
