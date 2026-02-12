# FastAPI Blueprint

How I build FastAPI backends, an opinionated blueprint with authentication, security, CI, and Docker.

## 👤 Author

**Alexey Shpetny**

- Email: alexey.shpetny.work@gmail.com
- LinkedIn: [linkedin.com/in/shpetnyalexey](https://www.linkedin.com/in/shpetnyalexey)
- Telegram: [@alexeyshpetny](https://t.me/alexeyshpetny)

## 📋 Table of Contents

- [Features](#-features)
- [Architecture & Project Structure](#️-architecture--project-structure)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [API Documentation](#-api-documentation)
- [Development](#-development)
- [Testing](#-testing)
- [Production Deployment](#-production-deployment)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### Security
Complete authentication and authorization system with enterprise-grade security features.

- ✅ **JWT Authentication** - Access and refresh tokens with automatic rotation
- ✅ **Token Management** - Redis-based blacklist for token revocation
- ✅ **Role-Based Access Control** - Flexible authorization with role dependencies
- ✅ **Password Security** - bcrypt hashing with configurable strength
- ✅ **Email Protection** - Generic error messages prevent user enumeration
- ✅ **Rate Limiting** - Per-endpoint limits with Redis support for multi-worker deployments
- ✅ **Security Headers** - X-Content-Type-Options, X-Frame-Options, HSTS, CSP, and more
- ✅ **CORS** - Validated configuration with secure defaults
- ✅ **Input Validation** - Request size limits, trusted hosts, and Pydantic validation
- ✅ **Environment Validation** - Automatic checks prevent production misconfigurations

### Reliability
Production-ready infrastructure with robust error handling and logging.

- ✅ **Health Checks** - Separate liveness and readiness endpoints for orchestration
- ✅ **Graceful Shutdown** - Proper cleanup of connections and resources
- ✅ **Database Pooling** - Optimized PostgreSQL connection management
- ✅ **Redis Caching** - FastAPI Cache integration for improved performance
- ✅ **Error Handling** - Structured error responses with proper HTTP status codes
- ✅ **Structured Logging** - JSON logs with request ID tracking for debugging

### Developer Experience
Everything you need to build, test, and deploy with confidence.

- ✅ **Type Safety** - Full type hints with MyPy validation
- ✅ **Code Quality** - Ruff for fast linting and automatic formatting
- ✅ **Testing** - pytest with unit and integration test markers
- ✅ **API Docs** - Auto-generated Swagger UI and ReDoc
- ✅ **Docker** - Multi-stage builds with healthchecks
- ✅ **CI/CD** - Automated testing, linting, and security scanning
- ✅ **Migrations** - Alembic for database schema management
- ✅ **Deployment Ready** - Docker Compose for local development, Gunicorn with Uvicorn workers for production

## 🏗️ Architecture & Project Structure

This blueprint follows clean architecture principles with clear separation of concerns.

### Key Patterns
- **Repository Pattern** - Clean data access abstraction
- **Dependency Injection** - FastAPI's dependency system
- **Service Layer** - Business logic separation
- **Settings Management** - Pydantic Settings with validation
- **Middleware Stack** - Logging, security headers, request size limits, CORS, trusted hosts

### Project Structure

```
fastapi-blueprint/
├── src/                    # Source code
│   ├── api/               # API routes and schemas
│   │   └── v1/           # Versioned endpoints
│   ├── auth/             # Authentication (JWT, password, dependencies)
│   ├── cache/            # Redis caching
│   ├── core/             # Core functionality
│   │   ├── exceptions/   # Exception handlers
│   │   ├── middlewares/  # Middleware (logging, security headers, request size limits)
│   │   └── settings/     # Configuration settings
│   ├── db/               # Database configuration
│   ├── models/           # SQLAlchemy models
│   ├── adapters/         # Repository pattern (data access layer)
│   ├── services/         # Business logic layer
│   ├── dependencies/     # FastAPI dependency injection
│   ├── rate_limit/       # Rate limiting implementation
│   ├── migrations/       # Alembic database migrations
│   └── main.py           # Application entry point
├── tests/                # Test suite
│   ├── test_api/        # API integration tests
│   ├── test_auth/       # Authentication tests
│   └── test_core/       # Core functionality tests
├── scripts/              # Utility scripts
│   └── entrypoint.sh    # Docker entrypoint
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile            # Docker image definition
├── pyproject.toml        # Project configuration and dependencies
├── Makefile              # Development commands
└── README.md             # This file
```

## 📦 Prerequisites

- **Python 3.13+** - Programming language runtime
- **Docker & Docker Compose** - Containerization platform for running services
- **uv** - Fast Python package installer and dependency manager

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd fastapi-blueprint
```

### 2. Install Dependencies

Using `uv` (recommended):
```bash
uv sync --group dev
```

Or using `pip`:
```bash
pip install -e ".[dev]"
```

### 3. Configure Environment

This template is configured for **development** by default, with production-safe defaults. The default environment is `development`, which allows for easier local development while maintaining security best practices.

**Default Configuration:**
- `APP_ENVIRONMENT=development` - Development mode (permissive CORS, relaxed validation)
- `APP_DEBUG=false` - Production-safe default (prevents exposing stack traces)
- `APP_CORS_ALLOW_ORIGINS=["*"]` - Permissive for local development
- Security features enabled by default (rate limiting, security headers, etc.)

**For Production:** Set `APP_ENVIRONMENT=production` and configure production-specific settings (CORS origins, secrets, etc.).

**Quick Setup:** Copy the example environment file:

```bash
cp .env.example .env
```

Then edit `.env` and adjust values as needed. The `.env.example` file contains minimal essential variables for getting started.

**Manual Setup:** Create a `.env` file in the project root with the following minimal configuration:

```bash
# Application
APP_ENVIRONMENT=development
APP_DEBUG=false

# PostgreSQL Docker Container
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=fastapi_blueprint

# Database Connection
APP_DB_HOST=postgres
APP_DB_PORT=5432
APP_DB_USER=postgres
APP_DB_PASSWORD=postgres
APP_DB_NAME=fastapi_blueprint

# Cache (Redis)
APP_CACHE_ENABLED=true
APP_CACHE_HOST=redis
APP_CACHE_PORT=6379

# Authentication
APP_JWT_SECRET_KEY=change-me-in-production-minimum-32-characters-long-secret-key

# Rate Limiting
APP_RATE_LIMIT_ENABLED=true
APP_RATE_LIMIT_DEFAULT=100/minute
```

**Note:** The `.env.example` file includes only essential variables. See [Configuration](#-configuration) for all available options and their defaults.

### 4. Start Services

**Recommended: Use Make commands** (simplest way to run the project):

```bash
# Build and start all services (PostgreSQL, Redis, API)
make start

# View logs
make logs

# Stop services
make down

# Rebuild images
make build
```

**Alternative: Manual Docker Compose commands**

```bash
# Start all services
docker compose up -d

# View logs
docker logs -f fastapi-blueprint-api

# Stop services
docker compose down

# Build images
docker compose build
```

**Alternative: Run without Docker**

```bash
# Start PostgreSQL and Redis (requires local installation)
# Then run migrations
make migrate

# Start the application
uvicorn src.main:application --reload --host 0.0.0.0 --port 8080
```

### 5. Access the API

- **API Base URL**: http://localhost:8080/api/v1
- **Swagger UI**: http://localhost:8080/api/docs
- **ReDoc**: http://localhost:8080/api/redoc
- **Readiness Check**: http://localhost:8080/api/v1/health/readiness

## ⚙️ Configuration

All configuration is done via environment variables with the `APP_` prefix. Settings are validated on startup and provide helpful error messages for misconfigurations.

### Application Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_ENVIRONMENT` | `development` | Environment: `production`, `development`, or `testing` |
| `APP_DEBUG` | `false` | Enable FastAPI debug mode (never enable in production) |
| `APP_SERVICE_NAME` | `fastapi-blueprint` | Service name for health checks |
| `APP_API_V1_PREFIX` | `/api/v1` | API v1 URL prefix |

### Database Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_DB_HOST` | `localhost` | PostgreSQL host |
| `APP_DB_PORT` | `5432` | PostgreSQL port |
| `APP_DB_USER` | `postgres` | Database user |
| `APP_DB_PASSWORD` | `postgres` | Database password (validated in production) |
| `APP_DB_NAME` | `fastapi_blueprint` | Database name |
| `APP_DB_POOL_SIZE` | `5` | Connection pool size |
| `APP_DB_MAX_OVERFLOW` | `10` | Maximum overflow connections |

### Cache Settings (Redis)

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_CACHE_ENABLED` | `true` | Enable Redis caching |
| `APP_CACHE_HOST` | `localhost` | Redis host |
| `APP_CACHE_PORT` | `6379` | Redis port |
| `APP_CACHE_PASSWORD` | `` | Redis password (recommended for production) |

### Authentication Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_JWT_SECRET_KEY` | `change-me-in-production...` | Secret key (min 32 chars, validated in production) |
| `APP_JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token expiration |
| `APP_JWT_REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token expiration |
| `APP_JWT_REFRESH_TOKEN_HTTP_ONLY` | `true` | HTTP-only cookie flag |
| `APP_JWT_REFRESH_TOKEN_SECURE` | `false` | Secure cookie flag (HTTPS only) |
| `APP_PASSWORD_MIN_LENGTH` | `8` | Minimum password length |
| `APP_BCRYPT_ROUNDS` | `12` | Bcrypt hashing rounds |

### Security Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_RATE_LIMIT_ENABLED` | `true` | Enable rate limiting |
| `APP_RATE_LIMIT_DEFAULT` | `100/minute` | Default rate limit |
| `APP_RATE_LIMIT_STORAGE_URI` | `None` | Redis URI for rate limiting (optional) |
| `APP_SECURITY_HEADERS_ENABLED` | `true` | Enable security headers middleware |
| `APP_CORS_ALLOW_ORIGINS` | `["*"]` | Allowed CORS origins (validated in production) |
| `APP_CORS_ALLOW_CREDENTIALS` | `false` | Allow CORS credentials |
| `APP_TRUSTED_HOSTS_ENABLED` | `false` | Enable trusted hosts validation |
| `APP_MAX_REQUEST_BODY_SIZE` | `10485760` | Max request body size (10MB) |

### Logging Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_LOG_LEVEL` | `INFO` | Logging level |
| `APP_LOG_FORMAT` | `json` | Log format: `json` or `text` |
| `APP_LOG_INCLUDE_REQUEST_ID` | `true` | Include request ID in logs |

**Note**: For production, ensure all secrets are changed from defaults and use a secret management service (AWS Secrets Manager, HashiCorp Vault, etc.).

## 📚 API Documentation

### Authentication Endpoints

#### Register
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "username": "johndoe"
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword123
```

Returns:
- `access_token` - JWT access token (expires in 30 minutes by default)
- `refresh_token` - Set as HTTP-only cookie (expires in 7 days by default)
- `user` - User information

#### Refresh Token
```http
POST /api/v1/auth/refresh
```

Refresh token is automatically read from cookie. Alternatively, can be provided in request body:
```json
{
  "refresh_token": "your-refresh-token"
}
```

#### Logout
```http
POST /api/v1/auth/logout
Authorization: Bearer <access_token>
```

Blacklists the refresh token and clears the cookie.

#### Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

#### Change Password
```http
POST /api/v1/auth/change-password
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "current_password": "oldpassword",
  "new_password": "newpassword123"
}
```

### Health Check Endpoints

#### Liveness
```http
GET /api/v1/health/liveness
```

Returns 200 if the application process is running.

#### Readiness
```http
GET /api/v1/health/readiness
```

Returns 200 if the service is ready to accept traffic (checks database and cache connections).

### Rate Limiting

Rate limits are applied per endpoint:
- **Auth endpoints** (login, register, change-password): `5/minute`
- **Refresh token**: `10/minute`
- **Logout**: `20/minute`
- **Get current user**: `60/minute`
- **Default**: `100/minute`

Rate limit headers are included in responses:
- `X-RateLimit-Limit` - Maximum requests allowed
- `X-RateLimit-Remaining` - Remaining requests
- `X-RateLimit-Reset` - Reset time (Unix timestamp)

### Authorization

Use dependency injection for protected routes:

```python
from src.auth.dependencies import get_current_user, require_role
from src.models.user import User

@router.get("/protected")
async def protected_route(
    current_user: User = Depends(get_current_user)
):
    return {"message": f"Hello, {current_user.email}"}

@router.get("/admin-only")
async def admin_route(
    current_user: User = Depends(require_role("admin"))
):
    return {"message": "Admin access granted"}
```

Available authorization dependencies:
- `get_current_user` - Get authenticated user
- `require_role(role)` - Require specific role
- `require_any_role(*roles)` - Require any of the specified roles
- `require_all_roles(*roles)` - Require all specified roles

## 🛠️ Development

### Code Quality

Run all checks:
```bash
make ci
```

Format code:
```bash
make format
```

Lint code:
```bash
make lint
```

Fix linting issues:
```bash
make fix
```

Security checks:
```bash
make security
```

### Database Migrations

Create a new migration:
```bash
make create-migrations
# Or manually:
docker exec --user root fastapi-blueprint-api alembic --config src/alembic.ini revision --autogenerate --message "description"
```

Apply migrations:
```bash
make migrate
# Or manually:
docker exec fastapi-blueprint-api bash -c 'cd src && alembic upgrade head'
```

Rollback migration:
```bash
docker exec fastapi-blueprint-api bash -c 'cd src && alembic downgrade -1'
```

## 🧪 Testing

### Run Tests

All tests:
```bash
make test
```

Unit tests only:
```bash
make test-unit
```

Integration tests only:
```bash
make test-integration
```

Fast tests (stops on first failure, failed tests first):
```bash
make test-fast
```

### Test Markers

Tests are organized with pytest markers:
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.slow` - Slow-running tests

## 🚢 Production Deployment

This blueprint provides a solid foundation, but you'll need to add additional components for production deployment.

### What's Included

✅ Security features (JWT auth, rate limiting, security headers)  
✅ Health checks and graceful shutdown  
✅ Database migrations and connection pooling  
✅ Structured logging  
✅ CI/CD pipeline  
✅ Docker support  

### What You Need to Add

**Monitoring & Observability** (recommended before production):
- Application metrics (Prometheus)
- APM integration (Sentry, Datadog, New Relic)
- Log aggregation (ELK, CloudWatch, etc.)
- Database query monitoring

**Operational Requirements**:
- Database backup strategy
- Connection pool monitoring/alerting
- Load testing
- Security audits

### Pre-Deployment Checklist

Before deploying to production, ensure the following:

#### Environment & Configuration
- [ ] `APP_ENVIRONMENT=production` set
- [ ] `APP_DEBUG=false` (validated automatically)
- [ ] CORS configured for specific origins (not `["*"]`)
- [ ] Trusted hosts configured (if `TRUSTED_HOSTS_ENABLED=true`)

#### Secrets & Security
- [ ] All secrets changed from defaults
- [ ] Database password changed and secure (min 8 chars, validated)
- [ ] Redis password set (if cache enabled)
- [ ] JWT secret key changed (min 32 chars, validated)
- [ ] Rate limiting enabled
- [ ] Security headers enabled

#### Application Health
- [ ] Liveness and readiness checks working (`/api/v1/health/readiness`)
- [ ] Database migrations applied
- [ ] All tests passing

#### Operations & Monitoring
- [ ] Monitoring and alerting configured
- [ ] Log aggregation set up
- [ ] Database backups configured

### Production Recommendations

1. **Secrets Management**: Use a secret management service (AWS Secrets Manager, HashiCorp Vault, etc.)
2. **HTTPS**: Always use HTTPS in production. Set `APP_JWT_REFRESH_TOKEN_SECURE=true`
3. **CORS**: Configure specific origins, not wildcards
4. **Rate Limiting**: Use Redis storage for multi-worker deployments
5. **Monitoring**: Add APM (Sentry, Datadog, New Relic) and metrics (Prometheus)
6. **Logging**: Send logs to external service (ELK, CloudWatch, etc.)
7. **Database**: Use connection pooling and monitor pool usage
8. **Backups**: Set up automated database backups
9. **Scaling**: Use multiple workers behind a load balancer
10. **Security Scanning**: Run regular security audits

### Environment Variables for Production

```bash
APP_ENVIRONMENT=production
APP_DEBUG=false
APP_CORS_ALLOW_ORIGINS=["https://yourdomain.com"]
APP_CORS_ALLOW_CREDENTIALS=true
APP_TRUSTED_HOSTS_ENABLED=true
APP_TRUSTED_HOSTS=["yourdomain.com","*.yourdomain.com"]
APP_JWT_REFRESH_TOKEN_SECURE=true
APP_DB_PASSWORD=<secure-password>
APP_CACHE_PASSWORD=<secure-password>
APP_JWT_SECRET_KEY=<secure-32-char-minimum-key>
```


## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Make your changes
4. Run tests and ensure all checks pass (`make ci`)
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feat/amazing-feature`)
7. Open a Pull Request

### Development Guidelines

- Follow existing code style (enforced by Ruff)
- Add tests for new features
- Update documentation as needed
- Ensure type hints are correct (MyPy checks)
- Keep commits atomic and well-described

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL toolkit
- [Alembic](https://alembic.sqlalchemy.org/) - Database migration tool
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [slowapi](https://github.com/laurentS/slowapi) - Rate limiting
- [python-jose](https://github.com/mpdavis/python-jose) - JWT handling

## 📞 Support

For questions, issues, or contributions, please open an issue on GitHub.

---

**Note**: This blueprint includes many production-ready features. For production deployment, consider adding monitoring, observability, and operational tooling based on your specific requirements.
