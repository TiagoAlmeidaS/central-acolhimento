#!/bin/bash
# Central de Acolhimento - Production Deployment Script
# Automated deployment script for production environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="central-acolhimento"
ENVIRONMENT="production"
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.prod"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if environment file exists
    if [ ! -f "$ENV_FILE" ]; then
        log_error "Environment file $ENV_FILE not found. Please create it from env.prod.example"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."
    
    mkdir -p nginx/ssl
    mkdir -p nginx/logs
    mkdir -p monitoring/grafana/dashboards
    mkdir -p monitoring/grafana/datasources
    mkdir -p backups
    mkdir -p logs
    
    log_success "Directories created"
}

# Generate SSL certificates (self-signed for demo)
generate_ssl_certificates() {
    log_info "Generating SSL certificates..."
    
    # Generate self-signed certificates for demo purposes
    # In production, use Let's Encrypt or your CA
    
    if [ ! -f "nginx/ssl/api.central-acolhimento.com.crt" ]; then
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/ssl/api.central-acolhimento.com.key \
            -out nginx/ssl/api.central-acolhimento.com.crt \
            -subj "/C=BR/ST=SP/L=SaoPaulo/O=CentralAcolhimento/CN=api.central-acolhimento.com"
    fi
    
    if [ ! -f "nginx/ssl/llm.central-acolhimento.com.crt" ]; then
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/ssl/llm.central-acolhimento.com.key \
            -out nginx/ssl/llm.central-acolhimento.com.crt \
            -subj "/C=BR/ST=SP/L=SaoPaulo/O=CentralAcolhimento/CN=llm.central-acolhimento.com"
    fi
    
    if [ ! -f "nginx/ssl/grafana.central-acolhimento.com.crt" ]; then
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/ssl/grafana.central-acolhimento.com.key \
            -out nginx/ssl/grafana.central-acolhimento.com.crt \
            -subj "/C=BR/ST=SP/L=SaoPaulo/O=CentralAcolhimento/CN=grafana.central-acolhimento.com"
    fi
    
    if [ ! -f "nginx/ssl/prometheus.central-acolhimento.com.crt" ]; then
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/ssl/prometheus.central-acolhimento.com.key \
            -out nginx/ssl/prometheus.central-acolhimento.com.crt \
            -subj "/C=BR/ST=SP/L=SaoPaulo/O=CentralAcolhimento/CN=prometheus.central-acolhimento.com"
    fi
    
    log_success "SSL certificates generated"
}

# Create basic auth file for monitoring
create_basic_auth() {
    log_info "Creating basic auth file for monitoring..."
    
    # Create basic auth file (username: admin, password: admin123)
    echo "admin:\$2y\$10\$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi" > nginx/.htpasswd
    
    log_success "Basic auth file created"
}

# Build Docker images
build_images() {
    log_info "Building Docker images..."
    
    # Build API image
    log_info "Building API image..."
    docker build -t central-acolhimento-api:latest ./api-repo/
    
    # Build LLM image
    log_info "Building LLM image..."
    docker build -t central-acolhimento-llm:latest ./llm-repo/
    
    log_success "Docker images built"
}

# Deploy services
deploy_services() {
    log_info "Deploying services..."
    
    # Stop existing services
    log_info "Stopping existing services..."
    docker-compose -f $DOCKER_COMPOSE_FILE --env-file $ENV_FILE down || true
    
    # Start services
    log_info "Starting services..."
    docker-compose -f $DOCKER_COMPOSE_FILE --env-file $ENV_FILE up -d
    
    log_success "Services deployed"
}

# Wait for services to be ready
wait_for_services() {
    log_info "Waiting for services to be ready..."
    
    # Wait for database
    log_info "Waiting for database..."
    timeout 60 bash -c 'until docker-compose -f '$DOCKER_COMPOSE_FILE' --env-file '$ENV_FILE' exec -T postgres pg_isready -U postgres; do sleep 2; done'
    
    # Wait for Redis
    log_info "Waiting for Redis..."
    timeout 60 bash -c 'until docker-compose -f '$DOCKER_COMPOSE_FILE' --env-file '$ENV_FILE' exec -T redis redis-cli ping; do sleep 2; done'
    
    # Wait for Ollama
    log_info "Waiting for Ollama..."
    timeout 120 bash -c 'until curl -f http://localhost:11434/; do sleep 5; done'
    
    # Wait for LLM service
    log_info "Waiting for LLM service..."
    timeout 60 bash -c 'until curl -f http://localhost:8001/health; do sleep 5; done'
    
    # Wait for API service
    log_info "Waiting for API service..."
    timeout 60 bash -c 'until curl -f http://localhost:8000/health; do sleep 5; done'
    
    log_success "All services are ready"
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    docker-compose -f $DOCKER_COMPOSE_FILE --env-file $ENV_FILE exec -T api-service alembic upgrade head
    
    log_success "Database migrations completed"
}

# Download Ollama model
download_ollama_model() {
    log_info "Downloading Ollama model..."
    
    docker-compose -f $DOCKER_COMPOSE_FILE --env-file $ENV_FILE exec -T ollama ollama pull llama3:8b
    
    log_success "Ollama model downloaded"
}

# Run health checks
run_health_checks() {
    log_info "Running health checks..."
    
    # Check API health
    if curl -f http://localhost:8000/health; then
        log_success "API service is healthy"
    else
        log_error "API service health check failed"
        exit 1
    fi
    
    # Check LLM health
    if curl -f http://localhost:8001/health; then
        log_success "LLM service is healthy"
    else
        log_error "LLM service health check failed"
        exit 1
    fi
    
    # Check Grafana
    if curl -f http://localhost:3000/api/health; then
        log_success "Grafana is healthy"
    else
        log_error "Grafana health check failed"
        exit 1
    fi
    
    # Check Prometheus
    if curl -f http://localhost:9090/-/healthy; then
        log_success "Prometheus is healthy"
    else
        log_error "Prometheus health check failed"
        exit 1
    fi
    
    log_success "All health checks passed"
}

# Display deployment information
display_info() {
    log_success "Deployment completed successfully!"
    echo ""
    echo "=== Central de Acolhimento - Production Environment ==="
    echo ""
    echo "Services:"
    echo "  - API Service:     http://localhost:8000"
    echo "  - LLM Service:     http://localhost:8001"
    echo "  - Grafana:         http://localhost:3000 (admin/admin123)"
    echo "  - Prometheus:      http://localhost:9090"
    echo "  - Nginx:          http://localhost:80 (redirects to HTTPS)"
    echo ""
    echo "SSL Endpoints (self-signed certificates):"
    echo "  - API:            https://api.central-acolhimento.com"
    echo "  - LLM:            https://llm.central-acolhimento.com"
    echo "  - Grafana:        https://grafana.central-acolhimento.com"
    echo "  - Prometheus:     https://prometheus.central-acolhimento.com"
    echo ""
    echo "Health Checks:"
    echo "  - API Health:     http://localhost:8000/health"
    echo "  - LLM Health:     http://localhost:8001/health"
    echo ""
    echo "Monitoring:"
    echo "  - Grafana:        http://localhost:3000"
    echo "  - Prometheus:     http://localhost:9090"
    echo ""
    echo "Logs:"
    echo "  - View logs:      docker-compose -f $DOCKER_COMPOSE_FILE --env-file $ENV_FILE logs -f"
    echo "  - Stop services:  docker-compose -f $DOCKER_COMPOSE_FILE --env-file $ENV_FILE down"
    echo ""
}

# Main deployment function
main() {
    log_info "Starting Central de Acolhimento production deployment..."
    
    check_prerequisites
    create_directories
    generate_ssl_certificates
    create_basic_auth
    build_images
    deploy_services
    wait_for_services
    run_migrations
    download_ollama_model
    run_health_checks
    display_info
    
    log_success "Production deployment completed successfully!"
}

# Run main function
main "$@"
