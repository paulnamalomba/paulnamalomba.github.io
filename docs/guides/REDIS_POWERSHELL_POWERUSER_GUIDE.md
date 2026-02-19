# REDIS PowerUser Guide (PowerShell)

**Last updated**: December 04, 2025<br>
**Author**: [Paul Namalomba](https://github.com/paulnamalomba)<br>
  - SESKA Computational Engineer<br>
  - SEAT Backend Developer<br>
  - Software Developer<br>
  - PhD Candidate (Civil Engineering Spec. Computational and Applied Mechanics)<br>
**Contact**: [kabwenzenamalomba@gmail.com](kabwenzenamalomba@gmail.com)<br>
**Website**: [paulnamalomba.github.io](https://paulnamalomba.github.io)<br>
<br>
[![Framework](https://img.shields.io/badge/Redis-7.x-red.svg)](https://redis.io/docs/)
[![License: MIT](https://img.shields.io/badge/License-MIT-gray.svg)](https://opensource.org/licenses/MIT)

## Overview

Redis is an in-memory data structure store used as a database, cache, message broker, and streaming engine. This guide covers installation, data structures, persistence, clustering, and performance optimization using PowerShell on Windows. Power users need to understand memory management, eviction policies, replication, and pub/sub patterns for production deployments.

## Contents

- [REDIS PowerUser Guide (PowerShell)](#redis-poweruser-guide-powershell)
  - [Overview](#overview)
  - [Contents](#contents)
  - [Quickstart](#quickstart)
  - [Key Concepts](#key-concepts)
  - [Configuration and Best Practices](#configuration-and-best-practices)
  - [Security Considerations](#security-considerations)
  - [Examples](#examples)
    - [Install and Configure Redis on Windows](#install-and-configure-redis-on-windows)
    - [Basic Data Operations](#basic-data-operations)
    - [Pub/Sub Messaging Pattern](#pubsub-messaging-pattern)
    - [Pipelining and Transactions](#pipelining-and-transactions)
    - [Backup and Persistence](#backup-and-persistence)
    - [Monitoring and Statistics](#monitoring-and-statistics)
  - [Troubleshooting](#troubleshooting)
  - [Performance and Tuning](#performance-and-tuning)
  - [References and Further Reading](#references-and-further-reading)

---

## Quickstart

1. **Install Redis**: Download from [redis.io/download](https://redis.io/download) or use Chocolatey: `choco install redis-64`
2. **Install as Windows service**: `redis-server --service-install redis.windows.conf`
3. **Start service**: `redis-server --service-start`
4. **Verify installation**: `redis-cli ping` (should return PONG)
5. **Set a key**: `redis-cli SET mykey "Hello Redis"`
6. **Get a key**: `redis-cli GET mykey`

## Key Concepts

- **In-Memory Storage**: All data stored in RAM for sub-millisecond latency; optional persistence to disk
- **Data Structures**: Strings, Lists, Sets, Sorted Sets, Hashes, Bitmaps, HyperLogLogs, Streams
- **Persistence**: RDB (point-in-time snapshots) and AOF (append-only file) for durability
- **Replication**: Master-replica architecture with automatic failover via Redis Sentinel
- **Pub/Sub**: Publish/subscribe messaging pattern for real-time event distribution
- **Transactions**: MULTI/EXEC commands for atomic execution of command batches

## Configuration and Best Practices

**redis.windows.conf** (located in installation directory):
```ini
# Network
bind 127.0.0.1
port 6379
timeout 300

# Memory management
maxmemory 2gb
maxmemory-policy allkeys-lru

# Persistence (RDB)
save 900 1
save 300 10
save 60 10000
dir C:/Redis/data
dbfilename dump.rdb

# Append-only file (AOF)
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec

# Slow log
slowlog-log-slower-than 10000
slowlog-max-len 128

# Security
requirepass StrongPassword123!
```

**Best Practices**:
- Set `maxmemory` to 75% of available RAM
- Use `allkeys-lru` eviction policy for caching scenarios
- Enable both RDB and AOF for maximum durability
- Implement connection pooling in applications
- Use pipelining for batch operations
- Monitor memory usage and fragmentation ratio

## Security Considerations

1. **Authentication**: Always set `requirepass` in production; use strong passwords
2. **Network Binding**: Bind to localhost (`127.0.0.1`) or specific interfaces; never `0.0.0.0` without firewall
3. **Disable Dangerous Commands**: Rename or disable commands like FLUSHDB, FLUSHALL, CONFIG, SHUTDOWN
4. **TLS/SSL**: Enable TLS for encrypted connections in Redis 6.0+
5. **ACLs**: Use Access Control Lists (Redis 6.0+) for fine-grained user permissions
6. **Firewall**: Use Windows Firewall to restrict access to port 6379
7. **Regular Updates**: Keep Redis updated to patch security vulnerabilities

**Rename Dangerous Commands**:
```ini
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG "CONFIG_8d7a9f2b"
rename-command SHUTDOWN "SHUTDOWN_5c4e1d3f"
```

## Examples

### Install and Configure Redis on Windows

Download, install, and configure Redis as a Windows service with basic security settings.

```powershell
# Install via Chocolatey
choco install redis-64 -y

# Or download manually
$redisUrl = "https://github.com/microsoftarchive/redis/releases/download/win-3.2.100/Redis-x64-3.2.100.zip"
$downloadPath = "$env:TEMP\redis.zip"
$installPath = "C:\Redis"

Invoke-WebRequest -Uri $redisUrl -OutFile $downloadPath
Expand-Archive -Path $downloadPath -DestinationPath $installPath

# Create data directory
New-Item -ItemType Directory -Path "C:\Redis\data" -Force

# Configure redis.windows.conf
$config = @"
bind 127.0.0.1
port 6379
timeout 300
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
dir C:/Redis/data
dbfilename dump.rdb
requirepass StrongPassword123!
"@
Set-Content -Path "C:\Redis\redis.windows.conf" -Value $config

# Install as Windows service
cd C:\Redis
.\redis-server.exe --service-install redis.windows.conf --service-name Redis

# Start service
Start-Service Redis

# Verify service
Get-Service Redis | Select-Object Name, Status, StartType

# Test connection
redis-cli -a StrongPassword123! ping
```

### Basic Data Operations

Perform CRUD operations with different Redis data structures using redis-cli.

```powershell
# Set password for authentication
$env:REDISCLI_AUTH = "StrongPassword123!"

# String operations
redis-cli SET user:1:name "John Doe"
redis-cli GET user:1:name
redis-cli INCR counter
redis-cli INCRBY counter 5
redis-cli SETEX session:token "3600" "abc123xyz"  # Expire in 1 hour

# List operations
redis-cli LPUSH queue:tasks "task1"
redis-cli RPUSH queue:tasks "task2" "task3"
redis-cli LRANGE queue:tasks 0 -1
redis-cli LPOP queue:tasks
redis-cli LLEN queue:tasks

# Set operations
redis-cli SADD tags:post1 "redis" "database" "nosql"
redis-cli SMEMBERS tags:post1
redis-cli SISMEMBER tags:post1 "redis"
redis-cli SINTER tags:post1 tags:post2

# Hash operations
redis-cli HSET user:1 name "John" email "john@example.com" age 30
redis-cli HGET user:1 name
redis-cli HGETALL user:1
redis-cli HINCRBY user:1 age 1

# Sorted Set operations
redis-cli ZADD leaderboard 100 "player1" 200 "player2" 150 "player3"
redis-cli ZRANGE leaderboard 0 -1 WITHSCORES
redis-cli ZREVRANGE leaderboard 0 2 WITHSCORES
redis-cli ZRANK leaderboard "player1"

# Key management
redis-cli EXISTS user:1:name
redis-cli DEL user:1:name
redis-cli EXPIRE session:token 3600
redis-cli TTL session:token
redis-cli KEYS "user:*"  # Use SCAN in production
```

### Pub/Sub Messaging Pattern

Implement publish/subscribe messaging for real-time event distribution across applications.

```powershell
# Publisher script (publisher.ps1)
$config = @"
`$env:REDISCLI_AUTH = 'StrongPassword123!'
while (`$true) {
    `$message = Read-Host 'Enter message (or quit to exit)'
    if (`$message -eq 'quit') { break }
    redis-cli PUBLISH news `$message
}
"@
Set-Content -Path "publisher.ps1" -Value $config

# Subscriber script (subscriber.ps1)
$config = @"
`$env:REDISCLI_AUTH = 'StrongPassword123!'
Write-Host 'Subscribing to news channel...'
redis-cli SUBSCRIBE news
"@
Set-Content -Path "subscriber.ps1" -Value $config

# Run subscriber in separate window
Start-Process powershell -ArgumentList "-NoExit", "-File", "subscriber.ps1"

# Run publisher
.\publisher.ps1

# Pattern-based subscription
redis-cli PSUBSCRIBE "event:*"

# Unsubscribe
redis-cli UNSUBSCRIBE news
redis-cli PUNSUBSCRIBE "event:*"
```

### Pipelining and Transactions

Use pipelining for batch operations and transactions for atomic command execution.

```powershell
# Pipelining example - execute multiple commands in batch
$commands = @"
SET key1 value1
SET key2 value2
GET key1
GET key2
INCR counter
INCR counter
"@
$commands | redis-cli -a StrongPassword123! --pipe

# Transaction example with MULTI/EXEC
$transaction = @"
MULTI
SET account:1:balance 1000
SET account:2:balance 500
DECRBY account:1:balance 100
INCRBY account:2:balance 100
EXEC
"@
$transaction | redis-cli -a StrongPassword123!

# Watch for optimistic locking
redis-cli -a StrongPassword123! << 'EOF'
WATCH balance
balance=$(redis-cli GET balance)
new_balance=$((balance + 100))
MULTI
SET balance $new_balance
EXEC
EOF
```

### Backup and Persistence

Configure and manage RDB snapshots and AOF files for data durability.

```powershell
# Trigger manual RDB snapshot
redis-cli -a StrongPassword123! SAVE  # Blocking
redis-cli -a StrongPassword123! BGSAVE  # Background

# Check last save time
redis-cli -a StrongPassword123! LASTSAVE

# Get RDB save configuration
redis-cli -a StrongPassword123! CONFIG GET save

# Modify save intervals
redis-cli -a StrongPassword123! CONFIG SET save "900 1 300 10 60 10000"
redis-cli -a StrongPassword123! CONFIG REWRITE

# AOF rewrite (compaction)
redis-cli -a StrongPassword123! BGREWRITEAOF

# Backup RDB file
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item "C:\Redis\data\dump.rdb" -Destination "C:\Backups\redis\dump_$timestamp.rdb"

# Backup AOF file
Copy-Item "C:\Redis\data\appendonly.aof" -Destination "C:\Backups\redis\appendonly_$timestamp.aof"

# Automated backup script
$script = @"
`$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
`$backupDir = 'C:\Backups\redis'
New-Item -ItemType Directory -Path `$backupDir -Force

# Trigger background save
redis-cli -a StrongPassword123! BGSAVE

# Wait for save to complete
Start-Sleep -Seconds 5

# Copy files
Copy-Item 'C:\Redis\data\dump.rdb' -Destination "`$backupDir\dump_`$timestamp.rdb"
Copy-Item 'C:\Redis\data\appendonly.aof' -Destination "`$backupDir\appendonly_`$timestamp.aof"

# Retention: Delete backups older than 7 days
Get-ChildItem `$backupDir -File | Where-Object { `$_.LastWriteTime -lt (Get-Date).AddDays(-7) } | Remove-Item

Write-Host 'Backup completed: `$timestamp'
"@
Set-Content -Path "C:\Scripts\redis-backup.ps1" -Value $script

# Schedule backup (daily at 2 AM)
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File C:\Scripts\redis-backup.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "Redis Daily Backup" -Description "Daily Redis backup"
```

### Monitoring and Statistics

Monitor Redis performance, memory usage, and client connections.

```powershell
# Get server info
redis-cli -a StrongPassword123! INFO

# Get specific info sections
redis-cli -a StrongPassword123! INFO server
redis-cli -a StrongPassword123! INFO memory
redis-cli -a StrongPassword123! INFO stats
redis-cli -a StrongPassword123! INFO replication

# Monitor commands in real-time
redis-cli -a StrongPassword123! MONITOR

# Get slow log entries
redis-cli -a StrongPassword123! SLOWLOG GET 10

# Get client list
redis-cli -a StrongPassword123! CLIENT LIST

# Get memory usage
redis-cli -a StrongPassword123! MEMORY STATS

# Get database key statistics
redis-cli -a StrongPassword123! DBSIZE
redis-cli -a StrongPassword123! INFO keyspace

# Continuous monitoring script
$script = @"
while (`$true) {
    Clear-Host
    Write-Host '=== Redis Monitoring ===' -ForegroundColor Cyan
    Write-Host ''
    
    # Memory usage
    `$memInfo = redis-cli -a StrongPassword123! INFO memory | Select-String 'used_memory_human|maxmemory_human'
    Write-Host 'Memory:' -ForegroundColor Yellow
    `$memInfo
    Write-Host ''
    
    # Connected clients
    `$clients = redis-cli -a StrongPassword123! INFO clients | Select-String 'connected_clients'
    Write-Host 'Clients:' -ForegroundColor Yellow
    `$clients
    Write-Host ''
    
    # Keyspace
    `$keyspace = redis-cli -a StrongPassword123! INFO keyspace
    Write-Host 'Keyspace:' -ForegroundColor Yellow
    `$keyspace
    Write-Host ''
    
    # Stats
    `$stats = redis-cli -a StrongPassword123! INFO stats | Select-String 'total_commands_processed|total_connections_received'
    Write-Host 'Stats:' -ForegroundColor Yellow
    `$stats
    
    Start-Sleep -Seconds 2
}
"@
Set-Content -Path "C:\Scripts\redis-monitor.ps1" -Value $script

# Run monitor
# .\redis-monitor.ps1
```

## Troubleshooting

**Connection Refused**:
- **Error**: "Could not connect to Redis"
  - **Check service**: `Get-Service Redis`
  - **Start service**: `Start-Service Redis`
  - **Check port**: `netstat -an | Select-String "6379"`
  - **Check logs**: `Get-Content "C:\Redis\redis.log" -Tail 50`

**Authentication Errors**:
- **Error**: "NOAUTH Authentication required"
  - **Set password env var**: `$env:REDISCLI_AUTH = "YourPassword"`
  - **Use -a flag**: `redis-cli -a YourPassword PING`

**Out of Memory**:
- **Error**: "OOM command not allowed when used memory > 'maxmemory'"
  - **Check memory**: `redis-cli INFO memory`
  - **Increase maxmemory**: `redis-cli CONFIG SET maxmemory 4gb`
  - **Change eviction policy**: `redis-cli CONFIG SET maxmemory-policy allkeys-lru`

**Slow Commands**:
- **Check slow log**: `redis-cli SLOWLOG GET 10`
- **Identify O(N) commands**: Avoid KEYS, use SCAN instead
- **Optimize data structures**: Use appropriate data types for use case

**Common Logs**:
- Redis log file: `C:\Redis\redis.log` (if configured)
- Windows Event Viewer: Application logs
- Monitor commands: Use `redis-cli MONITOR` sparingly (impacts performance)

## Performance and Tuning

**Memory Optimization**:
```ini
# redis.windows.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
maxmemory-samples 5

# Use efficient data structures
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64
```

**Persistence Tuning**:
```ini
# RDB - less frequent saves for better performance
save 900 1
save 300 10
save 60 10000

# AOF - balance between durability and performance
appendonly yes
appendfsync everysec  # Options: always, everysec, no
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
```

**Connection Pooling**:
Use StackExchange.Redis or similar libraries with connection pooling in applications.

**Pipelining**:
Batch multiple commands to reduce network round trips:
```powershell
# Instead of multiple individual commands
$commands = 1..1000 | ForEach-Object { "SET key:$_ value$_" }
$commands -join "`n" | redis-cli --pipe
```

**Monitoring Commands**:
```powershell
# Get latency statistics
redis-cli -a StrongPassword123! --latency
redis-cli -a StrongPassword123! --latency-history

# Get intrinsic latency
redis-cli -a StrongPassword123! --intrinsic-latency 100

# Benchmark Redis performance
redis-benchmark -a StrongPassword123! -t set,get -n 100000 -q

# Monitor hit rate
redis-cli -a StrongPassword123! INFO stats | Select-String "keyspace_hits|keyspace_misses"
```

## References and Further Reading

- [Redis Documentation](https://redis.io/docs/) - Official comprehensive Redis documentation
- [Redis Commands Reference](https://redis.io/commands) - Complete command reference with examples
- [Redis Best Practices](https://redis.io/topics/best-practices) - Official best practices guide
- [StackExchange.Redis](https://stackexchange.github.io/StackExchange.Redis/) - Popular .NET Redis client
- [Redis Persistence](https://redis.io/topics/persistence) - Deep dive into RDB and AOF persistence
