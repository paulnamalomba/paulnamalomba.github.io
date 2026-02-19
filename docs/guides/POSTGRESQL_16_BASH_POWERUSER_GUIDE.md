# POSTGRESQL 16 PowerUser Guide (Bash)

**Last updated**: December 04, 2025<br>
**Author**: [Paul Namalomba](https://github.com/paulnamalomba)<br>
  - SESKA Computational Engineer<br>
  - SEAT Backend Developer<br>
  - Software Developer<br>
  - PhD Candidate (Civil Engineering Spec. Computational and Applied Mechanics)<br>
**Contact**: [kabwenzenamalomba@gmail.com](kabwenzenamalomba@gmail.com)<br>
**Website**: [paulnamalomba.github.io](https://paulnamalomba.github.io)<br>
<br>

[![Framework](https://img.shields.io/badge/PostgreSQL-16.x-blue.svg)](https://www.postgresql.org/docs/16/)
[![License: MIT](https://img.shields.io/badge/License-MIT-gray.svg)](https://opensource.org/licenses/MIT)

## Overview

PostgreSQL 16 is an advanced open-source relational database with support for ACID transactions, JSON, full-text search, and extensibility. This guide covers installation, configuration, performance tuning, and administration using Bash on Linux systems. Power users need to understand connection pooling, query optimization, backup strategies, and replication for production deployments.

## Contents

- [POSTGRESQL 16 PowerUser Guide (Bash)](#postgresql-16-poweruser-guide-bash)
  - [Overview](#overview)
  - [Contents](#contents)
  - [Quickstart](#quickstart)
  - [Key Concepts](#key-concepts)
  - [Configuration and Best Practices](#configuration-and-best-practices)
  - [Security Considerations](#security-considerations)
  - [Examples](#examples)
    - [Install and Configure PostgreSQL 16](#install-and-configure-postgresql-16)
    - [Database and User Management](#database-and-user-management)
    - [Backup and Restore Operations](#backup-and-restore-operations)
    - [Query Execution and Analysis](#query-execution-and-analysis)
    - [Index Management and Optimization](#index-management-and-optimization)
    - [Maintenance Operations](#maintenance-operations)
  - [Troubleshooting](#troubleshooting)
  - [Performance and Tuning](#performance-and-tuning)
  - [References and Further Reading](#references-and-further-reading)

---

## Quickstart

1. **Install PostgreSQL 16**: `sudo apt-get install postgresql-16` (Ubuntu) or `sudo yum install postgresql16-server` (RHEL)
2. **Initialize cluster** (RHEL only): `sudo postgresql-16-setup initdb`
3. **Start service**: `sudo systemctl start postgresql` or `sudo systemctl start postgresql-16`
4. **Enable auto-start**: `sudo systemctl enable postgresql`
5. **Switch to postgres user**: `sudo -i -u postgres`
6. **Connect**: `psql`

## Key Concepts

- **Cluster**: Collection of databases managed by a single PostgreSQL server instance
- **MVCC (Multi-Version Concurrency Control)**: Allows concurrent reads/writes without locking; each transaction sees a consistent snapshot
- **WAL (Write-Ahead Logging)**: Transaction log used for crash recovery and replication; modifications written to WAL before data files
- **Vacuum**: Process that reclaims storage from dead tuples and prevents transaction ID wraparound
- **Indexes**: B-tree (default), Hash, GiST, GIN, BRIN for optimizing query performance
- **Schemas**: Namespaces within a database for organizing tables and objects; default schema is `public`

## Configuration and Best Practices

**postgresql.conf** (typically `/etc/postgresql/16/main/postgresql.conf` or `/var/lib/pgsql/16/data/postgresql.conf`):
```ini
# Connection settings
max_connections = 100
shared_buffers = 4GB                   # 25% of system RAM
effective_cache_size = 12GB            # 75% of system RAM

# Write-ahead log
wal_level = replica
max_wal_size = 2GB
min_wal_size = 1GB
checkpoint_completion_target = 0.9

# Query planner
random_page_cost = 1.1                 # For SSD storage
effective_io_concurrency = 200         # For SSD storage

# Logging
log_destination = 'stderr'
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_statement = 'all'
log_min_duration_statement = 1000      # Log queries > 1 second
```

**pg_hba.conf** (same directory as postgresql.conf):
```
# TYPE  DATABASE  USER      ADDRESS         METHOD
local   all       all                       scram-sha-256
host    all       all       127.0.0.1/32    scram-sha-256
host    all       all       ::1/128         scram-sha-256
host    all       all       0.0.0.0/0       scram-sha-256
```

**Best Practices**:
- Use connection pooling (PgBouncer) for applications with >100 connections
- Enable query logging for slow queries (>1000ms)
- Implement regular VACUUM ANALYZE for table statistics
- Use prepared statements to prevent SQL injection
- Create indexes on foreign keys and frequently queried columns
- Set appropriate work_mem per connection (start with 4MB)

## Security Considerations

1. **Authentication**: Use `scram-sha-256` password encryption; avoid `trust` and `md5` methods
2. **SSL/TLS**: Enforce encrypted connections in production; generate certificates and set `ssl = on`
3. **Least Privilege**: Create role-based access with minimal permissions; avoid using `postgres` superuser for applications
4. **Network Security**: Bind to localhost only (`listen_addresses = 'localhost'`) or specific IPs; use firewall rules
5. **SQL Injection**: Use parameterized queries exclusively; never concatenate user input into SQL
6. **Audit Logging**: Enable `pgaudit` extension for compliance requirements and track DDL/DML operations
7. **Data Encryption**: Use `pgcrypto` for column-level encryption; enable transparent data encryption (TDE) for data-at-rest

**Create Secure Application User**:
```sql
CREATE ROLE appuser WITH LOGIN PASSWORD 'SecurePassword123!';
CREATE DATABASE appdb OWNER appuser;
GRANT CONNECT ON DATABASE appdb TO appuser;
\c appdb
GRANT USAGE ON SCHEMA public TO appuser;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO appuser;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
```

## Examples

### Install and Configure PostgreSQL 16

Install PostgreSQL 16 on Ubuntu/Debian with repository configuration and initial setup.

```bash
#!/bin/bash

# Add PostgreSQL APT repository
sudo apt-get install -y wget ca-certificates
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" | sudo tee /etc/apt/sources.list.d/pgdg.list

# Update and install PostgreSQL 16
sudo apt-get update
sudo apt-get install -y postgresql-16 postgresql-contrib-16

# Start and enable service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Check status
sudo systemctl status postgresql

# Verify installation
sudo -u postgres psql -c "SELECT version();"

# Set postgres user password
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'StrongPassword123!';"

# Create password file for automation
cat > ~/.pgpass << EOF
localhost:5432:*:postgres:StrongPassword123!
EOF
chmod 600 ~/.pgpass
```

### Database and User Management

Create databases, users, and schemas with proper permission grants and role management.

```bash
#!/bin/bash

# Create database
sudo -u postgres psql -c "CREATE DATABASE production_db WITH ENCODING 'UTF8' LC_COLLATE='en_US.UTF-8' LC_CTYPE='en_US.UTF-8';"

# Create roles
sudo -u postgres psql -c "CREATE ROLE admin_role;"
sudo -u postgres psql -c "CREATE ROLE readonly_role;"
sudo -u postgres psql -c "CREATE ROLE readwrite_role;"

# Create users
sudo -u postgres psql -c "CREATE USER admin_user WITH PASSWORD 'AdminPass123!' IN ROLE admin_role;"
sudo -u postgres psql -c "CREATE USER app_user WITH PASSWORD 'AppPass123!' IN ROLE readwrite_role;"
sudo -u postgres psql -c "CREATE USER report_user WITH PASSWORD 'ReportPass123!' IN ROLE readonly_role;"

# Grant database access
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE production_db TO admin_role;"
sudo -u postgres psql -c "GRANT CONNECT ON DATABASE production_db TO readwrite_role;"
sudo -u postgres psql -c "GRANT CONNECT ON DATABASE production_db TO readonly_role;"

# Grant schema permissions
sudo -u postgres psql -d production_db << 'EOF'
GRANT USAGE ON SCHEMA public TO readwrite_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO readwrite_role;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO readwrite_role;

GRANT USAGE ON SCHEMA public TO readonly_role;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_role;

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO readwrite_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO readonly_role;
EOF

# List users and roles
sudo -u postgres psql -c "\du"
```

### Backup and Restore Operations

Perform full database backups, compressed backups, and point-in-time recovery setup with automated scheduling.

```bash
#!/bin/bash

BACKUP_DIR="/var/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
sudo mkdir -p $BACKUP_DIR
sudo chown postgres:postgres $BACKUP_DIR

# Full database dump (plain SQL)
sudo -u postgres pg_dump -d production_db -F p -f "$BACKUP_DIR/production_db_$DATE.sql"

# Compressed custom format dump (recommended for large databases)
sudo -u postgres pg_dump -d production_db -F c -f "$BACKUP_DIR/production_db_$DATE.dump"

# Dump specific schema
sudo -u postgres pg_dump -d production_db -n public -F c -f "$BACKUP_DIR/public_schema_$DATE.dump"

# Dump specific tables
sudo -u postgres pg_dump -d production_db -t users -t orders -F c -f "$BACKUP_DIR/specific_tables_$DATE.dump"

# Dump all databases
sudo -u postgres pg_dumpall -f "$BACKUP_DIR/all_databases_$DATE.sql"

# Restore from plain SQL dump
sudo -u postgres psql -d production_db -f "$BACKUP_DIR/production_db_20241204_120000.sql"

# Restore from custom format dump
sudo -u postgres pg_restore -d production_db -F c -c --if-exists "$BACKUP_DIR/production_db_20241204_120000.dump"

# Parallel restore (faster for large databases)
sudo -u postgres pg_restore -d production_db -F c -j 4 "$BACKUP_DIR/production_db_20241204_120000.dump"

# Create automated backup script
cat > /usr/local/bin/pg_backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/postgresql"
DATE=$(date +%Y%m%d)
RETENTION_DAYS=7

# Create backup
sudo -u postgres pg_dump -d production_db -F c -f "$BACKUP_DIR/production_db_$DATE.dump"

# Remove old backups
find $BACKUP_DIR -name "production_db_*.dump" -mtime +$RETENTION_DAYS -delete

# Log result
echo "$(date): Backup completed - $BACKUP_DIR/production_db_$DATE.dump" >> /var/log/pg_backup.log
EOF

sudo chmod +x /usr/local/bin/pg_backup.sh

# Add to crontab (run daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/pg_backup.sh") | crontab -
```

### Query Execution and Analysis

Execute queries, analyze query plans, and monitor query performance with explain plans and timing.

```bash
#!/bin/bash

# Execute simple query
sudo -u postgres psql -d production_db -c "SELECT * FROM users LIMIT 10;"

# Execute query from file
sudo -u postgres psql -d production_db -f /path/to/queries.sql

# Get query execution time
sudo -u postgres psql -d production_db << 'EOF'
\timing
SELECT COUNT(*) FROM large_table;
EOF

# Analyze query plan
sudo -u postgres psql -d production_db -c "EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'user@example.com';"

# Get table sizes
sudo -u postgres psql -d production_db << 'EOF'
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_indexes_size(schemaname||'.'||tablename)) AS indexes_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
EOF

# Get index usage statistics
sudo -u postgres psql -d production_db << 'EOF'
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
EOF

# Find slow queries (requires pg_stat_statements extension)
sudo -u postgres psql -d production_db << 'EOF'
SELECT 
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
EOF
```

### Index Management and Optimization

Create, analyze, and maintain indexes for optimal query performance with different index types.

```bash
#!/bin/bash

# Create B-tree index (default)
sudo -u postgres psql -d production_db -c "CREATE INDEX idx_users_email ON users(email);"

# Create unique index
sudo -u postgres psql -d production_db -c "CREATE UNIQUE INDEX idx_users_username ON users(username);"

# Create composite index
sudo -u postgres psql -d production_db -c "CREATE INDEX idx_orders_user_date ON orders(user_id, created_at);"

# Create partial index (conditional)
sudo -u postgres psql -d production_db -c "CREATE INDEX idx_orders_active ON orders(user_id) WHERE status = 'active';"

# Create GIN index for JSON columns
sudo -u postgres psql -d production_db -c "CREATE INDEX idx_products_attributes ON products USING GIN(attributes);"

# Create GiST index for full-text search
sudo -u postgres psql -d production_db -c "CREATE INDEX idx_articles_search ON articles USING GiST(to_tsvector('english', title || ' ' || content));"

# Rebuild index (remove bloat)
sudo -u postgres psql -d production_db -c "REINDEX INDEX CONCURRENTLY idx_users_email;"

# Rebuild all indexes on table
sudo -u postgres psql -d production_db -c "REINDEX TABLE CONCURRENTLY users;"

# Get unused indexes
sudo -u postgres psql -d production_db << 'EOF'
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;
EOF

# Drop unused indexes
sudo -u postgres psql -d production_db -c "DROP INDEX CONCURRENTLY idx_old_unused_index;"
```

### Maintenance Operations

Perform routine maintenance tasks including VACUUM, ANALYZE, and statistics updates for optimal database health.

```bash
#!/bin/bash

# Manual vacuum (non-blocking)
sudo -u postgres psql -d production_db -c "VACUUM;"

# Vacuum specific table
sudo -u postgres psql -d production_db -c "VACUUM VERBOSE ANALYZE users;"

# Full vacuum (locks table, reclaims more space)
sudo -u postgres psql -d production_db -c "VACUUM FULL users;"

# Analyze statistics for query planner
sudo -u postgres psql -d production_db -c "ANALYZE;"

# Reindex database
sudo -u postgres psql -d production_db -c "REINDEX DATABASE production_db;"

# Check for bloat
sudo -u postgres psql -d production_db << 'EOF'
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    n_dead_tup,
    n_live_tup,
    ROUND(100 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_tuple_percent
FROM pg_stat_user_tables
WHERE n_dead_tup > 0
ORDER BY n_dead_tup DESC;
EOF

# Enable autovacuum (should be on by default)
sudo -u postgres psql -c "ALTER SYSTEM SET autovacuum = on;"
sudo -u postgres psql -c "SELECT pg_reload_conf();"

# Configure autovacuum thresholds for specific table
sudo -u postgres psql -d production_db << 'EOF'
ALTER TABLE users SET (
    autovacuum_vacuum_scale_factor = 0.1,
    autovacuum_analyze_scale_factor = 0.05
);
EOF

# Create maintenance script
cat > /usr/local/bin/pg_maintenance.sh << 'SCRIPT'
#!/bin/bash
echo "$(date): Starting maintenance"
sudo -u postgres psql -d production_db -c "VACUUM ANALYZE;"
echo "$(date): Maintenance completed"
SCRIPT

sudo chmod +x /usr/local/bin/pg_maintenance.sh

# Schedule weekly maintenance (Sunday 3 AM)
(crontab -l 2>/dev/null; echo "0 3 * * 0 /usr/local/bin/pg_maintenance.sh >> /var/log/pg_maintenance.log 2>&1") | crontab -
```

## Troubleshooting

**Connection Refused**:
- **Error**: "could not connect to server: Connection refused"
  - **Check service**: `sudo systemctl status postgresql`
  - **Start service**: `sudo systemctl start postgresql`
  - **Check port**: `sudo netstat -tlnp | grep 5432` or `sudo ss -tlnp | grep 5432`
  - **Check logs**: `sudo tail -f /var/log/postgresql/postgresql-16-main.log`

**Authentication Failed**:
- **Error**: "FATAL: password authentication failed"
  - **Check pg_hba.conf**: `sudo cat /etc/postgresql/16/main/pg_hba.conf`
  - **Reset password**: `sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'NewPassword123!';"`
  - **Reload config**: `sudo systemctl reload postgresql`

**Out of Memory**:
- **Error**: "out of memory" or "could not resize shared memory segment"
  - **Check shared_buffers**: Edit `/etc/postgresql/16/main/postgresql.conf`
  - **Increase shared memory**: Edit `/etc/sysctl.conf` and add `kernel.shmmax = 17179869184`
  - **Apply changes**: `sudo sysctl -p`

**Lock Timeouts**:
```bash
# Check blocking queries
sudo -u postgres psql -d production_db << 'EOF'
SELECT 
    pid,
    usename,
    pg_blocking_pids(pid) AS blocked_by,
    query
FROM pg_stat_activity
WHERE cardinality(pg_blocking_pids(pid)) > 0;
EOF

# Kill blocking session
sudo -u postgres psql -c "SELECT pg_terminate_backend(12345);"
```

**Common Logs**:
- PostgreSQL logs: `/var/log/postgresql/postgresql-16-main.log`
- System logs: `sudo journalctl -u postgresql -n 100`
- Authentication errors: `sudo grep "authentication failed" /var/log/postgresql/postgresql-16-main.log`

## Performance and Tuning

**Memory Configuration**:
```ini
# For 16GB RAM system (/etc/postgresql/16/main/postgresql.conf)
shared_buffers = 4GB              # 25% of RAM
effective_cache_size = 12GB       # 75% of RAM
maintenance_work_mem = 1GB        # For VACUUM, CREATE INDEX
work_mem = 16MB                   # Per sort/hash operation
```

**Connection Pooling with PgBouncer**:
```bash
# Install PgBouncer
sudo apt-get install pgbouncer

# Configure /etc/pgbouncer/pgbouncer.ini
sudo tee /etc/pgbouncer/pgbouncer.ini > /dev/null << 'EOF'
[databases]
production_db = host=localhost port=5432 dbname=production_db

[pgbouncer]
listen_addr = 127.0.0.1
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
EOF

# Create user list
echo '"app_user" "AppPass123!"' | sudo tee /etc/pgbouncer/userlist.txt

# Start PgBouncer
sudo systemctl start pgbouncer
sudo systemctl enable pgbouncer
```

**Query Optimization**:
```bash
# Enable pg_stat_statements extension
sudo -u postgres psql -d production_db -c "CREATE EXTENSION IF NOT EXISTS pg_stat_statements;"

# Add to postgresql.conf
sudo tee -a /etc/postgresql/16/main/postgresql.conf > /dev/null << 'EOF'
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.max = 10000
pg_stat_statements.track = all
EOF

# Restart service
sudo systemctl restart postgresql
```

**Monitoring Commands**:
```bash
# Active connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity;"

# Database size
sudo -u postgres psql -c "SELECT pg_database.datname, pg_size_pretty(pg_database_size(pg_database.datname)) AS size FROM pg_database;"

# Cache hit ratio (should be >99%)
sudo -u postgres psql -d production_db << 'EOF'
SELECT 
    sum(heap_blks_read) as heap_read,
    sum(heap_blks_hit) as heap_hit,
    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) AS cache_hit_ratio
FROM pg_statio_user_tables;
EOF

# Transaction rate
sudo -u postgres psql -d production_db -c "SELECT xact_commit + xact_rollback AS total_transactions FROM pg_stat_database WHERE datname = 'production_db';"
```

## References and Further Reading

- [PostgreSQL 16 Documentation](https://www.postgresql.org/docs/16/) - Official comprehensive documentation
- [PostgreSQL Wiki](https://wiki.postgresql.org/wiki/Main_Page) - Community wiki with tutorials and best practices
- [pgAdmin 4](https://www.pgadmin.org/) - Web-based PostgreSQL administration tool
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization) - Performance optimization guide
- [Awesome PostgreSQL](https://github.com/dhamaniasad/awesome-postgres) - Curated list of PostgreSQL resources
