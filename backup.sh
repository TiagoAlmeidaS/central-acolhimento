#!/bin/bash
# Central de Acolhimento - Automated Backup Script
# Production backup script for database and application data

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="central-acolhimento"
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}
S3_BUCKET=${BACKUP_S3_BUCKET:-"central-acolhimento-backups"}
S3_REGION=${BACKUP_S3_REGION:-"us-east-1"}

# Database configuration
DB_HOST="postgres"
DB_PORT="5432"
DB_NAME="central_acolhimento"
DB_USER="postgres"
DB_PASSWORD=${DB_PASSWORD:-"secure_password_123"}

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

# Create backup directory
create_backup_dir() {
    log_info "Creating backup directory..."
    mkdir -p "$BACKUP_DIR/$DATE"
    log_success "Backup directory created: $BACKUP_DIR/$DATE"
}

# Backup PostgreSQL database
backup_database() {
    log_info "Starting database backup..."
    
    local backup_file="$BACKUP_DIR/$DATE/database_backup.sql"
    
    # Create database dump
    PGPASSWORD="$DB_PASSWORD" pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --verbose \
        --no-password \
        --format=plain \
        --file="$backup_file"
    
    # Compress the backup
    gzip "$backup_file"
    
    log_success "Database backup completed: ${backup_file}.gz"
}

# Backup application data
backup_application_data() {
    log_info "Starting application data backup..."
    
    local backup_file="$BACKUP_DIR/$DATE/application_data.tar.gz"
    
    # Create tar archive of important application data
    tar -czf "$backup_file" \
        -C /var/lib/docker/volumes \
        central-acolhimento_postgres_data \
        central-acolhimento_redis_data \
        central-acolhimento_ollama_data \
        central-acolhimento_prometheus_data \
        central-acolhimento_grafana_data 2>/dev/null || true
    
    log_success "Application data backup completed: $backup_file"
}

# Backup configuration files
backup_configuration() {
    log_info "Starting configuration backup..."
    
    local backup_file="$BACKUP_DIR/$DATE/configuration.tar.gz"
    
    # Create tar archive of configuration files
    tar -czf "$backup_file" \
        docker-compose.prod.yml \
        nginx/nginx.conf \
        monitoring/prometheus.yml \
        .env.prod \
        nginx/ssl/ 2>/dev/null || true
    
    log_success "Configuration backup completed: $backup_file"
}

# Backup logs
backup_logs() {
    log_info "Starting logs backup..."
    
    local backup_file="$BACKUP_DIR/$DATE/logs.tar.gz"
    
    # Create tar archive of logs
    tar -czf "$backup_file" \
        -C /var/log \
        nginx/ \
        docker/ 2>/dev/null || true
    
    log_success "Logs backup completed: $backup_file"
}

# Upload to S3 (if configured)
upload_to_s3() {
    if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
        log_info "Uploading backup to S3..."
        
        local s3_path="s3://$S3_BUCKET/$PROJECT_NAME/$DATE/"
        
        # Upload backup files to S3
        aws s3 cp "$BACKUP_DIR/$DATE/" "$s3_path" --recursive --region "$S3_REGION"
        
        log_success "Backup uploaded to S3: $s3_path"
    else
        log_warning "S3 credentials not configured, skipping S3 upload"
    fi
}

# Clean old backups
cleanup_old_backups() {
    log_info "Cleaning up old backups..."
    
    # Remove local backups older than retention period
    find "$BACKUP_DIR" -type d -name "20*" -mtime +$BACKUP_RETENTION_DAYS -exec rm -rf {} \; 2>/dev/null || true
    
    # Remove S3 backups older than retention period (if S3 is configured)
    if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
        aws s3 ls "s3://$S3_BUCKET/$PROJECT_NAME/" --region "$S3_REGION" | \
        awk '{print $2}' | \
        while read -r folder; do
            if [ -n "$folder" ]; then
                folder_date=$(echo "$folder" | cut -d'/' -f1)
                if [ -n "$folder_date" ]; then
                    folder_timestamp=$(date -d "$folder_date" +%s 2>/dev/null || echo "0")
                    current_timestamp=$(date +%s)
                    days_diff=$(( (current_timestamp - folder_timestamp) / 86400 ))
                    
                    if [ $days_diff -gt $BACKUP_RETENTION_DAYS ]; then
                        log_info "Removing old S3 backup: $folder"
                        aws s3 rm "s3://$S3_BUCKET/$PROJECT_NAME/$folder" --recursive --region "$S3_REGION"
                    fi
                fi
            fi
        done
    fi
    
    log_success "Old backups cleaned up"
}

# Verify backup integrity
verify_backup() {
    log_info "Verifying backup integrity..."
    
    local backup_dir="$BACKUP_DIR/$DATE"
    
    # Check if backup files exist
    if [ ! -f "${backup_dir}/database_backup.sql.gz" ]; then
        log_error "Database backup file not found"
        return 1
    fi
    
    if [ ! -f "${backup_dir}/application_data.tar.gz" ]; then
        log_error "Application data backup file not found"
        return 1
    fi
    
    if [ ! -f "${backup_dir}/configuration.tar.gz" ]; then
        log_error "Configuration backup file not found"
        return 1
    fi
    
    # Check file sizes
    local db_size=$(stat -c%s "${backup_dir}/database_backup.sql.gz")
    local app_size=$(stat -c%s "${backup_dir}/application_data.tar.gz")
    local config_size=$(stat -c%s "${backup_dir}/configuration.tar.gz")
    
    if [ $db_size -lt 1000 ]; then
        log_error "Database backup file is too small: $db_size bytes"
        return 1
    fi
    
    if [ $app_size -lt 1000 ]; then
        log_warning "Application data backup file is small: $app_size bytes"
    fi
    
    if [ $config_size -lt 100 ]; then
        log_error "Configuration backup file is too small: $config_size bytes"
        return 1
    fi
    
    log_success "Backup integrity verified"
}

# Send notification
send_notification() {
    local status=$1
    local message=$2
    
    if [ -n "$ALERT_EMAIL" ]; then
        echo "$message" | mail -s "Central de Acolhimento Backup - $status" "$ALERT_EMAIL" 2>/dev/null || true
    fi
    
    if [ -n "$ALERT_WEBHOOK_URL" ]; then
        curl -X POST "$ALERT_WEBHOOK_URL" \
            -H "Content-Type: application/json" \
            -d "{\"text\":\"Central de Acolhimento Backup - $status: $message\"}" 2>/dev/null || true
    fi
}

# Main backup function
main() {
    log_info "Starting Central de Acolhimento backup process..."
    
    local start_time=$(date +%s)
    
    # Create backup directory
    create_backup_dir
    
    # Perform backups
    backup_database
    backup_application_data
    backup_configuration
    backup_logs
    
    # Verify backup
    if verify_backup; then
        log_success "Backup verification passed"
    else
        log_error "Backup verification failed"
        send_notification "FAILED" "Backup verification failed"
        exit 1
    fi
    
    # Upload to S3
    upload_to_s3
    
    # Cleanup old backups
    cleanup_old_backups
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log_success "Backup completed successfully in ${duration}s"
    send_notification "SUCCESS" "Backup completed successfully in ${duration}s"
}

# Restore function
restore() {
    local backup_date=$1
    
    if [ -z "$backup_date" ]; then
        log_error "Backup date is required for restore"
        echo "Usage: $0 restore YYYYMMDD_HHMMSS"
        exit 1
    fi
    
    local backup_dir="$BACKUP_DIR/$backup_date"
    
    if [ ! -d "$backup_dir" ]; then
        log_error "Backup directory not found: $backup_dir"
        exit 1
    fi
    
    log_info "Starting restore from backup: $backup_date"
    
    # Restore database
    if [ -f "${backup_dir}/database_backup.sql.gz" ]; then
        log_info "Restoring database..."
        gunzip -c "${backup_dir}/database_backup.sql.gz" | \
        PGPASSWORD="$DB_PASSWORD" psql \
            -h "$DB_HOST" \
            -p "$DB_PORT" \
            -U "$DB_USER" \
            -d "$DB_NAME"
        log_success "Database restored"
    else
        log_error "Database backup file not found"
        exit 1
    fi
    
    # Restore application data
    if [ -f "${backup_dir}/application_data.tar.gz" ]; then
        log_info "Restoring application data..."
        tar -xzf "${backup_dir}/application_data.tar.gz" -C /
        log_success "Application data restored"
    else
        log_warning "Application data backup file not found"
    fi
    
    # Restore configuration
    if [ -f "${backup_dir}/configuration.tar.gz" ]; then
        log_info "Restoring configuration..."
        tar -xzf "${backup_dir}/configuration.tar.gz"
        log_success "Configuration restored"
    else
        log_warning "Configuration backup file not found"
    fi
    
    log_success "Restore completed successfully"
}

# Handle command line arguments
case "${1:-}" in
    "restore")
        restore "$2"
        ;;
    *)
        main
        ;;
esac
