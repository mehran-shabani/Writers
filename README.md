# Writers - AI-Powered Task Management System

An advanced task management system with AI-powered content processing and analysis.

<div>

## 📋 Table of Contents

- [Introduction](#introduction)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Technologies Used](#technologies-used)
- [Quick Installation and Setup](#quick-installation-and-setup)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Monitoring and Logging](#monitoring-and-logging)
- [Security](#security)
- [Scalability](#scalability)
- [Additional Documentation](#additional-documentation)

---

## 🎯 Introduction

Writers is a complete platform for task management, designed using a modern microservices architecture. This system provides file processing, content analysis, and user management with a modern user interface and a RESTful API.

### Key Specifications

- ✅ Microservices architecture with complete separation of Frontend and Backend
- ✅ Secure authentication with JWT and Cookie-based sessions
- ✅ Asynchronous task processing with Celery
- ✅ API Proxy in Next.js for better cookie and header management
- ✅ Complete monitoring with Prometheus and Grafana
- ✅ Centralized logging with Loki and Promtail
- ✅ Nginx configuration with SSL/TLS
- ✅ Automatic alerts for system resources (RAM, GPU, Disk)
- ✅ Ready for Production environment

---

## 🚀 Key Features

### User Management
- Secure registration and login
- JWT-based authentication
- Session management with Refresh Token
- Roles and permissions

### Task Management
- Create, edit, and delete tasks
- Upload and manage files
- Asynchronous processing with Celery
- Track processing status
- Advanced text editor with TipTap

### Infrastructure and Operations
- Load Balancing with Nginx
- SSL/TLS with Let's Encrypt
- Health Check endpoints
- Rate Limiting
- CORS Configuration

### Monitoring and Logging
- Metrics collection with Prometheus
- Grafana dashboards
- Centralized logs with Loki
- Automatic alerts with Alertmanager
- GPU and system resources monitoring

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        Client                           │
│                    (Browser/Mobile)                     │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTPS (443)
                        ▼
┌─────────────────────────────────────────────────────────┐
│                       Nginx                             │
│          (Reverse Proxy + Load Balancer)                │
│   - SSL/TLS Termination                                 │
│   - Rate Limiting                                       │
│   - Static File Serving                                 │
└────────┬───────────────────────┬────────────────────────┘
         │                       │
         │ /api/*               │ /*
         ▼                       ▼
┌─────────────────┐    ┌──────────────────┐
│   FastAPI       │    │    Next.js       │
│   Backend       │◄───│    Frontend      │
│   (Port 8000)   │    │   (Port 3000)    │
│                 │    │                  │
│ - Auth API      │    │ - API Proxy      │
│ - Tasks API     │    │ - SSR/CSR        │
│ - Metrics       │    │ - UI Components  │
└────────┬────────┘    └──────────────────┘
         │
         ├──────────┬──────────┬──────────┐
         ▼          ▼          ▼          ▼
    ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
    │ Postgres│ │ Redis │ │ Celery │ │ Storage│
    │   DB    │ │ Cache │ │ Worker │ │ Files  │
    └────────┘ └────────┘ └────────┘ └────────┘
         │          │          │
         └──────────┴──────────┘
                    │
                    ▼
         ┌────────────────────┐
         │    Monitoring      │
         │  - Prometheus      │
         │  - Grafana         │
         │  - Loki            │
         │  - Alertmanager    │
         └────────────────────┘
```

---

## 🛠️ Technologies Used

### Backend
- **FastAPI** - High-speed Python web framework
- **SQLAlchemy** - ORM for database management
- **Alembic** - Migration management
- **Pydantic** - Data validation
- **Python-JOSE** - JWT Token Management
- **Passlib** - Password hashing
- **Celery** - Asynchronous processing

### Frontend
- **Next.js 14** - React Framework with SSR/SSG
- **TypeScript** - Type Safety
- **TailwindCSS** - Styling
- **TipTap** - Rich Text Editor
- **Axios** - HTTP Client
- **SWR** - Data Fetching

### Database & Cache
- **PostgreSQL** - Main database
- **Redis** - Cache and Message Broker

### Infrastructure
- **Nginx** - Reverse Proxy and Load Balancer
- **Docker** - Containerization
- **Docker Compose** - Orchestration

### Monitoring & Logging
- **Prometheus** - Metrics Collection
- **Grafana** - Visualization
- **Loki** - Log Aggregation
- **Promtail** - Log Collection
- **Alertmanager** - Alert Management
- **Node Exporter** - System Metrics
- **PostgreSQL Exporter** - Database Metrics
- **Redis Exporter** - Cache Metrics
- **Nginx Exporter** - Web Server Metrics

---

## ⚡ Quick Installation and Setup

### Prerequisites

```bash
# Ubuntu/Debian
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- Nginx
```

### Development Setup

#### 1. Clone the project

```bash
git clone https://github.com/yourusername/writers.git
cd writers
```

#### 2. Backend Setup

```bash
cd backend

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp ../.env.example .env
# Edit .env and set the values

# Run migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the server
npm run dev
```

#### 4. Worker Setup

```bash
cd worker

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the Celery worker
celery -A tasks worker --loglevel=info
```

#### 5. Access the application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Production Setup

For a full production setup, refer to the [Setup Guide](SETUP_GUIDE.md).

#### Quick Install with Docker

```bash
cd infrastructure

# Start all services
docker-compose up -d

# Start monitoring
docker-compose -f docker-compose.monitoring.yml up -d
```

---

## 📁 Project Structure

```
writers/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── auth/              # Authentication module
│   │   ├── models/            # Database models
│   │   ├── routers/           # API Endpoints
│   │   ├── db.py              # Database settings
│   │   └── main.py            # Entry point
│   ├── alembic/               # Database Migrations
│   ├── tests/                 # Tests
│   └── requirements.txt
│
├── frontend/                   # Next.js Frontend
│   ├── app/
│   │   ├── api/              # Next.js API Proxy Routes
│   │   │   ├── auth/         # Proxy for authentication
│   │   │   └── tasks/        # Proxy for tasks
│   │   ├── dashboard/        # Dashboard pages
│   │   ├── login/            # Login page
│   │   └── register/         # Registration page
│   ├── components/           # React components
│   ├── lib/                  # Helper libraries
│   ├── __tests__/            # Integration tests
│   └── package.json
│
├── worker/                     # Celery Worker
│   ├── tasks.py              # Task definitions
│   └── requirements.txt
│
├── infrastructure/            # Infrastructure and DevOps
│   ├── nginx/
│   │   ├── nginx.conf        # Production configuration with SSL
│   │   └── nginx-local.conf  # Local configuration
│   ├── monitoring/
│   │   ├── prometheus/       # Prometheus settings
│   │   │   ├── prometheus.yml
│   │   │   └── alerts/       # Alert rules
│   │   ├── grafana/          # Dashboards and datasources
│   │   └── alertmanager/     # Alertmanager settings
│   ├── logging/
│   │   ├── loki/             # Loki settings
│   │   └── promtail/         # Promtail settings
│   ├── scripts/
│   │   ├── setup-ssl.sh      # Install SSL with Certbot
│   │   ├── deploy-nginx.sh   # Secure Nginx deployment
│   │   ├── health-check.sh   # Check service health
│   │   └── setup-monitoring.sh
│   ├── docker-compose.yml
│   └── docker-compose.monitoring.yml
│
├── .env.example               # Sample environment file
├── README.md                  # This file
└── SETUP_GUIDE.md            # Full setup guide
```

---

## 🔌 API Endpoints

### Authentication

```
POST   /api/auth/register      # Register a new user
POST   /api/auth/login         # Log in
POST   /api/auth/logout        # Log out
GET    /api/auth/me            # Current user information
POST   /api/auth/refresh       # Refresh token
```

### Tasks

```
GET    /api/tasks              # List tasks
POST   /api/tasks              # Create a new task
GET    /api/tasks/{id}         # Task details
PUT    /api/tasks/{id}         # Update a task
DELETE /api/tasks/{id}         # Delete a task
```

### Health & Metrics

```
GET    /health                 # Check service health
GET    /metrics                # Prometheus metrics
```

### Full API Documentation

Interactive Swagger documentation is available:
- Production: https://yourdomain.com/docs
- Development: http://localhost:8000/docs

---

## 📊 Monitoring and Logging

### Prometheus Metrics

The system automatically collects the following metrics:

- **System Metrics**: CPU, RAM, Disk, Network
- **Application Metrics**: Request count, Response time, Error rate
- **Database Metrics**: Connection pool, Query performance
- **Cache Metrics**: Hit rate, Memory usage
- **GPU Metrics**: Temperature, Memory, Utilization

### Grafana Dashboards

Ready-made dashboards:
- **System Overview**: Overview of system resources
- **Application Performance**: API and Backend performance
- **Database Performance**: PostgreSQL status
- **Error Tracking**: Track errors and exceptions

Access: http://localhost:3001 (admin/admin)

### Log Aggregation

All logs are collected in Loki:
- FastAPI application logs
- Nginx access/error logs
- Celery worker logs
- PostgreSQL logs
- System logs

Access: via Grafana > Explore > Loki

### Alert Rules

Defined alerts:

#### System Resources
- ✅ RAM > 85% (Warning)
- ⚠️ RAM > 95% (Critical)
- ✅ Disk > 80% (Warning)
- ⚠️ Disk > 90% (Critical)
- ✅ GPU Temp > 80°C (Warning)
- ⚠️ GPU Temp > 90°C (Critical)

#### Services
- ⚠️ Service Down (Critical)
- ✅ High Error Rate > 5% (Warning)
- ✅ High Response Time > 2s (Warning)
- ✅ Database Connection Pool > 80% (Warning)

---

## 🔒 Security

### Authentication
- JWT-based authentication
- HttpOnly cookies to prevent XSS
- Refresh token rotation
- Secure password hashing with Bcrypt

### HTTPS/SSL
- TLS 1.2/1.3
- Automatic certificate renewal with Let's Encrypt
- HSTS headers
- Secure cipher suites

### API Security
- Rate limiting (10 req/s for API, 5 req/s for auth)
- CORS configuration
- Input validation with Pydantic
- SQL injection protection with SQLAlchemy ORM

### Security Headers
```
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
```

---

## 📈 Scalability

### Hardware Recommendations

| Concurrent Users | RAM    | CPU Cores | Storage |
|---|---|---|---|
| < 100           | 16 GB  | 4         | 50 GB   |
| 100-500         | 32 GB  | 8         | 100 GB  |
| 500-1000        | 64 GB  | 16        | 200 GB  |
| 1000+           | 128 GB | 32+       | 500 GB+ |

### Increasing Capacity

#### Backend Workers
```bash
# in /etc/systemd/system/writers-backend.service
ExecStart=.../uvicorn app.main:app --workers 8
```

#### Celery Workers
```bash
# in /etc/systemd/system/writers-worker.service
ExecStart=.../celery -A tasks worker --concurrency=8
```

#### Horizontal Scaling

For horizontal scaling:

1. **Load Balancer**: Use Nginx upstream
```nginx
upstream backend_servers {
    least_conn;
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}
```

2. **Database Replication**: Set up Master-Slave PostgreSQL
3. **Redis Cluster**: For distributed cache
4. **Shared Storage**: For uploaded files

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest

# with coverage
pytest --cov=app --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm test

# with coverage
npm run test:coverage
```

### Integration Tests

```bash
# Test API proxy routes
cd frontend
npm test -- __tests__/api/proxy.test.ts
```

---

## 🚢 Deployment

### With Docker

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

### With Systemd

Full details in the [Setup Guide](SETUP_GUIDE.md)

### CI/CD

The project is ready for integration with:
- GitHub Actions
- GitLab CI
- Jenkins
- CircleCI

---

## 📚 Additional Documentation

- **[Full Setup Guide](SETUP_GUIDE.md)** - Detailed installation and configuration steps
- **[API Documentation](http://localhost:8000/docs)** - Interactive Swagger documentation
- **Infrastructure Docs**:
  - [QUICK_START.md](infrastructure/QUICK_START.md)
  - [DEPLOYMENT.md](infrastructure/DEPLOYMENT.md)
  - [SYSTEMD_SERVICES.md](infrastructure/SYSTEMD_SERVICES.md)

---

## 🤝 Contribution

To contribute to the project:

1. Fork the project
2. Create a new branch for a feature (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Create a Pull Request

### Code Standards

- **Python**: PEP 8
- **JavaScript/TypeScript**: ESLint + Prettier
- **Git Commits**: Conventional Commits

---

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 👥 Development Team

- **Backend Development**: FastAPI + SQLAlchemy
- **Frontend Development**: Next.js + TypeScript
- **DevOps**: Docker + Nginx + Monitoring
- **UI/UX**: Modern React Components

---

## 📞 Support

For bug reports or feature requests:
- **GitHub Issues**: [Create an issue](https://github.com/yourusername/writers/issues)
- **Email**: support@yourdomain.com
- **Documentation**: [Full Documentation](https://writers-docs.yourdomain.com)

---

## 🎉 Thanks

Thanks to everyone who contributed to the development of this project.

---

## 📊 Project Status

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-85%25-green)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![Node](https://img.shields.io/badge/node-18+-green)

---

**Made with ❤️ in Iran**

</div>
