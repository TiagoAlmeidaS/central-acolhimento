#!/bin/bash
# Central de Acolhimento - Monitoring and Alerting Script
# Production monitoring script with health checks and alerts

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="central-acolhimento"
CHECK_INTERVAL=${CHECK_INTERVAL:-30}
ALERT_EMAIL=${ALERT_EMAIL:-"admin@central-acolhimento.com"}
ALERT_WEBHOOK_URL=${ALERT_WEBHOOK_URL:-""}
LOG_FILE="/var/log/central-acolhimento/monitoring.log"

# Service endpoints
API_ENDPOINT="http://localhost:8000"
LLM_ENDPOINT="http://localhost:8001"
GRAFANA_ENDPOINT="http://localhost:3000"
PROMETHEUS_ENDPOINT="http://localhost:9090"

# Thresholds
CPU_THRESHOLD=80
MEMORY_THRESHOLD=85
DISK_THRESHOLD=90
RESPONSE_TIME_THRESHOLD=5

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] $1" >> "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [SUCCESS] $1" >> "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [WARNING] $1" >> "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] $1" >> "$LOG_FILE"
}

# Send alert
send_alert() {
    local severity=$1
    local service=$2
    local message=$3
    
    local alert_message="[${severity}] ${service}: ${message}"
    
    # Send email alert
    if [ -n "$ALERT_EMAIL" ]; then
        echo "$alert_message" | mail -s "Central de Acolhimento Alert - $severity" "$ALERT_EMAIL" 2>/dev/null || true
    fi
    
    # Send webhook alert
    if [ -n "$ALERT_WEBHOOK_URL" ]; then
        curl -X POST "$ALERT_WEBHOOK_URL" \
            -H "Content-Type: application/json" \
            -d "{\"text\":\"$alert_message\"}" 2>/dev/null || true
    fi
    
    log_error "$alert_message"
}

# Check service health
check_service_health() {
    local service_name=$1
    local endpoint=$2
    local expected_status=${3:-200}
    
    local start_time=$(date +%s.%N)
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$endpoint/health" 2>/dev/null || echo "000")
    local end_time=$(date +%s.%N)
    local response_time=$(echo "$end_time - $start_time" | bc)
    
    if [ "$response" = "$expected_status" ]; then
        log_success "$service_name is healthy (${response_time}s)"
        return 0
    else
        send_alert "CRITICAL" "$service_name" "Health check failed (HTTP $response)"
        return 1
    fi
}

# Check API service
check_api_service() {
    log_info "Checking API service..."
    
    # Health check
    if ! check_service_health "API" "$API_ENDPOINT"; then
        return 1
    fi
    
    # Check specific endpoints
    local endpoints=("/contatos/" "/health" "/docs")
    for endpoint in "${endpoints[@]}"; do
        local response=$(curl -s -o /dev/null -w "%{http_code}" "$API_ENDPOINT$endpoint" 2>/dev/null || echo "000")
        if [ "$response" != "200" ] && [ "$response" != "405" ]; then
            send_alert "WARNING" "API" "Endpoint $endpoint returned HTTP $response"
        fi
    done
    
    return 0
}

# Check LLM service
check_llm_service() {
    log_info "Checking LLM service..."
    
    # Health check
    if ! check_service_health "LLM" "$LLM_ENDPOINT"; then
        return 1
    fi
    
    # Check MCP endpoints
    local endpoints=("/mcp/health" "/mcp/models")
    for endpoint in "${endpoints[@]}"; do
        local response=$(curl -s -o /dev/null -w "%{http_code}" "$LLM_ENDPOINT$endpoint" 2>/dev/null || echo "000")
        if [ "$response" != "200" ]; then
            send_alert "WARNING" "LLM" "Endpoint $endpoint returned HTTP $response"
        fi
    done
    
    return 0
}

# Check monitoring services
check_monitoring_services() {
    log_info "Checking monitoring services..."
    
    # Check Grafana
    local grafana_response=$(curl -s -o /dev/null -w "%{http_code}" "$GRAFANA_ENDPOINT/api/health" 2>/dev/null || echo "000")
    if [ "$grafana_response" != "200" ]; then
        send_alert "WARNING" "Grafana" "Health check failed (HTTP $grafana_response)"
    else
        log_success "Grafana is healthy"
    fi
    
    # Check Prometheus
    local prometheus_response=$(curl -s -o /dev/null -w "%{http_code}" "$PROMETHEUS_ENDPOINT/-/healthy" 2>/dev/null || echo "000")
    if [ "$prometheus_response" != "200" ]; then
        send_alert "WARNING" "Prometheus" "Health check failed (HTTP $prometheus_response)"
    else
        log_success "Prometheus is healthy"
    fi
}

# Check database connectivity
check_database() {
    log_info "Checking database connectivity..."
    
    local db_response=$(docker exec central-acolhimento-postgres-prod pg_isready -U postgres 2>/dev/null || echo "not ready")
    if [ "$db_response" != "accepting connections" ]; then
        send_alert "CRITICAL" "Database" "PostgreSQL is not accepting connections"
        return 1
    fi
    
    log_success "Database is healthy"
    return 0
}

# Check Redis connectivity
check_redis() {
    log_info "Checking Redis connectivity..."
    
    local redis_response=$(docker exec central-acolhimento-redis-prod redis-cli ping 2>/dev/null || echo "PONG")
    if [ "$redis_response" != "PONG" ]; then
        send_alert "CRITICAL" "Redis" "Redis is not responding"
        return 1
    fi
    
    log_success "Redis is healthy"
    return 0
}

# Check Ollama service
check_ollama() {
    log_info "Checking Ollama service..."
    
    local ollama_response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:11434/" 2>/dev/null || echo "000")
    if [ "$ollama_response" != "200" ]; then
        send_alert "CRITICAL" "Ollama" "Ollama service is not responding (HTTP $ollama_response)"
        return 1
    fi
    
    # Check if llama3:8b model is available
    local model_response=$(curl -s "http://localhost:11434/api/tags" 2>/dev/null | grep -o "llama3:8b" || echo "")
    if [ -z "$model_response" ]; then
        send_alert "WARNING" "Ollama" "llama3:8b model not found"
    else
        log_success "Ollama is healthy with llama3:8b model"
    fi
    
    return 0
}

# Check system resources
check_system_resources() {
    log_info "Checking system resources..."
    
    # Check CPU usage
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')
    if (( $(echo "$cpu_usage > $CPU_THRESHOLD" | bc -l) )); then
        send_alert "WARNING" "System" "High CPU usage: ${cpu_usage}%"
    else
        log_success "CPU usage is normal: ${cpu_usage}%"
    fi
    
    # Check memory usage
    local memory_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    if [ "$memory_usage" -gt "$MEMORY_THRESHOLD" ]; then
        send_alert "WARNING" "System" "High memory usage: ${memory_usage}%"
    else
        log_success "Memory usage is normal: ${memory_usage}%"
    fi
    
    # Check disk usage
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt "$DISK_THRESHOLD" ]; then
        send_alert "WARNING" "System" "High disk usage: ${disk_usage}%"
    else
        log_success "Disk usage is normal: ${disk_usage}%"
    fi
}

# Check Docker containers
check_docker_containers() {
    log_info "Checking Docker containers..."
    
    local containers=(
        "central-acolhimento-postgres-prod"
        "central-acolhimento-redis-prod"
        "central-acolhimento-ollama-prod"
        "central-acolhimento-api-prod"
        "central-acolhimento-llm-prod"
        "central-acolhimento-nginx-prod"
        "central-acolhimento-prometheus-prod"
        "central-acolhimento-grafana-prod"
    )
    
    for container in "${containers[@]}"; do
        local status=$(docker inspect --format='{{.State.Status}}' "$container" 2>/dev/null || echo "not found")
        if [ "$status" != "running" ]; then
            send_alert "CRITICAL" "Docker" "Container $container is not running (status: $status)"
        else
            log_success "Container $container is running"
        fi
    done
}

# Check log files for errors
check_logs() {
    log_info "Checking log files for errors..."
    
    # Check for recent errors in application logs
    local error_count=$(docker logs central-acolhimento-api-prod --since 5m 2>&1 | grep -i "error\|exception\|failed" | wc -l)
    if [ "$error_count" -gt 10 ]; then
        send_alert "WARNING" "API" "High number of errors in logs: $error_count"
    fi
    
    local llm_error_count=$(docker logs central-acolhimento-llm-prod --since 5m 2>&1 | grep -i "error\|exception\|failed" | wc -l)
    if [ "$llm_error_count" -gt 5 ]; then
        send_alert "WARNING" "LLM" "High number of errors in logs: $llm_error_count"
    fi
    
    log_success "Log check completed"
}

# Generate monitoring report
generate_report() {
    log_info "Generating monitoring report..."
    
    local report_file="/var/log/central-acolhimento/monitoring-report-$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "=== Central de Acolhimento Monitoring Report ==="
        echo "Generated: $(date)"
        echo ""
        echo "=== Service Status ==="
        echo "API Service: $(curl -s -o /dev/null -w "%{http_code}" "$API_ENDPOINT/health" 2>/dev/null || echo "DOWN")"
        echo "LLM Service: $(curl -s -o /dev/null -w "%{http_code}" "$LLM_ENDPOINT/health" 2>/dev/null || echo "DOWN")"
        echo "Grafana: $(curl -s -o /dev/null -w "%{http_code}" "$GRAFANA_ENDPOINT/api/health" 2>/dev/null || echo "DOWN")"
        echo "Prometheus: $(curl -s -o /dev/null -w "%{http_code}" "$PROMETHEUS_ENDPOINT/-/healthy" 2>/dev/null || echo "DOWN")"
        echo ""
        echo "=== System Resources ==="
        echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}')"
        echo "Memory Usage: $(free | grep Mem | awk '{printf "%.0f%%", $3/$2 * 100.0}')"
        echo "Disk Usage: $(df / | tail -1 | awk '{print $5}')"
        echo ""
        echo "=== Docker Containers ==="
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        echo ""
        echo "=== Recent Logs ==="
        docker logs central-acolhimento-api-prod --tail 10 2>&1
        echo ""
        docker logs central-acolhimento-llm-prod --tail 10 2>&1
    } > "$report_file"
    
    log_success "Monitoring report generated: $report_file"
}

# Main monitoring function
main() {
    log_info "Starting Central de Acolhimento monitoring..."
    
    # Create log directory
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Run all checks
    check_api_service
    check_llm_service
    check_monitoring_services
    check_database
    check_redis
    check_ollama
    check_system_resources
    check_docker_containers
    check_logs
    
    # Generate report
    generate_report
    
    log_success "Monitoring check completed"
}

# Continuous monitoring function
continuous_monitoring() {
    log_info "Starting continuous monitoring (interval: ${CHECK_INTERVAL}s)..."
    
    while true; do
        main
        sleep "$CHECK_INTERVAL"
    done
}

# Handle command line arguments
case "${1:-}" in
    "continuous")
        continuous_monitoring
        ;;
    "report")
        generate_report
        ;;
    *)
        main
        ;;
esac
