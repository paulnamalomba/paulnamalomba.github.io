# Docker PowerUser Guide (PowerShell)

**Last updated**: December 05, 2025<br>
**Author**: [Paul Namalomba](https://github.com/paulnamalomba)<br>

- SESKA Computational Engineer<br>
- SEAT Backend Developer<br>
- Software Developer<br>
- PhD Candidate (Civil Engineering Spec. Computational and Applied Mechanics)<br>
**Contact**: [kabwenzenamalomba@gmail.com](kabwenzenamalomba@gmail.com)<br>
**Website**: [paulnamalomba.github.io](https://paulnamalomba.github.io)<br>
<br>

[![Framework](https://img.shields.io/badge/Docker-27.x-blue.svg)](https://docs.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-gray.svg)](https://opensource.org/licenses/MIT)

## Overview

Docker is a containerization platform enabling consistent application deployment across environments using lightweight, portable containers. This guide covers installation, image management, container orchestration, Docker Compose, networking, volume management, and security using PowerShell 7+ on Windows. Power users need to understand multi-stage builds, resource limits, health checks, and production deployment patterns for Windows container workloads.

## Contents

- [Docker PowerUser Guide (PowerShell)](#docker-poweruser-guide-powershell)
  - [Overview](#overview)
  - [Contents](#contents)
  - [Quickstart](#quickstart)
  - [Key Concepts](#key-concepts)
  - [Configuration and Best Practices](#configuration-and-best-practices)
  - [Security Considerations](#security-considerations)
  - [Examples](#examples)
    - [Container Lifecycle Management](#container-lifecycle-management)
    - [Building and Managing Images](#building-and-managing-images)
    - [Docker Compose Multi-Container Applications](#docker-compose-multi-container-applications)
    - [Volume and Network Management](#volume-and-network-management)
    - [System Monitoring and Cleanup](#system-monitoring-and-cleanup)
  - [Troubleshooting](#troubleshooting)
  - [Performance and Tuning](#performance-and-tuning)
  - [References and Further Reading](#references-and-further-reading)

---

## Quickstart

1. **Install Docker Desktop**: Download from docker.com and enable WSL 2 backend
2. **Verify installation**: `docker --version` and `docker run hello-world`
3. **Pull image**: `docker pull nginx:latest`
4. **Run container**: `docker run -d -p 8080:80 --name webserver nginx`
5. **Stop container**: `docker stop webserver`
6. **Remove container**: `docker rm webserver`

## Key Concepts

- **Image**: Read-only template containing application code, runtime, libraries, and dependencies; built from Dockerfile layers
- **Container**: Running instance of an image with isolated filesystem, networking, and process space; ephemeral by default
- **Volume**: Persistent data storage mechanism that survives container lifecycle; stored outside container union filesystem
- **Network**: Virtual network enabling container-to-container communication; types include bridge, host, overlay, macvlan
- **Registry**: Storage and distribution system for Docker images; Docker Hub is public default, private registries available
- **Dockerfile**: Text file with instructions to build Docker images; supports multi-stage builds for optimized image sizes
- **Docker Compose**: Tool for defining and running multi-container applications using YAML configuration files

## Configuration and Best Practices

**Docker Desktop Settings (Windows)**:

```powershell
# Configure Docker Desktop via settings.json
# Location: %APPDATA%\Docker\settings.json

{
  "memoryMiB": 8192,
  "cpus": 4,
  "diskSizeMiB": 102400,
  "swapMiB": 2048,
  "enableVirtualizationExtensions": true,
  "useWindowsContainers": false,
  "kernelForUDP": true
}
```

**PowerShell Profile Configuration**:

```powershell
# Add to $PROFILE for Docker aliases
Set-Alias -Name d -Value docker
Set-Alias -Name dc -Value docker-compose

function dps { docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Ports}}" }
function dimg { docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" }
function dprune { docker system prune -af --volumes }
function dlogs { param($container) docker logs -f $container }
function dexec { param($container) docker exec -it $container powershell }
```

**Best Practices**:

- Use official base images from verified publishers
- Implement multi-stage builds to reduce final image size
- Run containers as non-root users when possible
- Use specific image tags instead of `latest` for reproducibility
- Implement health checks for production containers
- Use `.dockerignore` to exclude unnecessary files from build context
- Set resource limits (CPU, memory) to prevent resource exhaustion
- Use Docker Compose for multi-container applications

## Security Considerations

1. **Image Security**: Scan images for vulnerabilities with `docker scan <image>` or third-party tools like Trivy
2. **Least Privilege**: Run containers with minimal permissions; avoid `--privileged` flag unless absolutely necessary
3. **Network Isolation**: Use custom bridge networks instead of default bridge; implement network segmentation
4. **Secrets Management**: Never bake secrets into images; use Docker secrets, environment files, or external vaults
5. **Resource Limits**: Set memory and CPU limits to prevent DoS attacks and resource exhaustion
6. **Read-Only Filesystems**: Mount volumes as read-only when possible; use `--read-only` flag
7. **Registry Security**: Use private registries with authentication; enable Docker Content Trust for image signing

**Secure Container Configuration**:

```powershell
# Run container with security constraints
docker run -d `
  --name secure-app `
  --memory="512m" `
  --memory-swap="512m" `
  --cpus="0.5" `
  --read-only `
  --cap-drop ALL `
  --cap-add NET_BIND_SERVICE `
  --security-opt="no-new-privileges:true" `
  --health-cmd="curl -f http://localhost/ || exit 1" `
  --health-interval=30s `
  --health-timeout=3s `
  --health-retries=3 `
  -p 8080:80 `
  nginx:alpine

# Use secrets for sensitive data
echo "mypassword" | docker secret create db_password -
docker service create --name db --secret db_password postgres:15
```

## Examples

### Container Lifecycle Management

Manage container creation, execution, monitoring, and cleanup with comprehensive PowerShell commands.

```powershell
# Pull image from Docker Hub
docker pull nginx:alpine

# Run container in detached mode with port mapping
docker run -d `
  --name webserver `
  -p 8080:80 `
  -v ${PWD}/html:/usr/share/nginx/html:ro `
  --restart unless-stopped `
  nginx:alpine

# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Inspect container details
docker inspect webserver | ConvertFrom-Json | Select-Object -ExpandProperty NetworkSettings

# View container logs
docker logs webserver

# Follow logs in real-time
docker logs -f --tail 100 webserver

# Execute command in running container
docker exec -it webserver sh

# Run PowerShell in Windows container
docker exec -it myapp powershell

# Stop container gracefully (SIGTERM)
docker stop webserver

# Kill container immediately (SIGKILL)
docker kill webserver

# Restart container
docker restart webserver

# Pause and unpause container
docker pause webserver
docker unpause webserver

# Remove stopped container
docker rm webserver

# Force remove running container
docker rm -f webserver

# Get container stats (CPU, memory usage)
docker stats --no-stream

# Monitor specific container
docker stats webserver

# Export container filesystem to tar
docker export webserver | Out-File -FilePath webserver.tar -Encoding byte

# Copy files from container to host
docker cp webserver:/etc/nginx/nginx.conf ./nginx.conf

# Copy files from host to container
docker cp ./index.html webserver:/usr/share/nginx/html/
```

### Building and Managing Images

Create optimized Docker images with multi-stage builds, tagging strategies, and registry operations.

```powershell
# Create Dockerfile for .NET application
@"
# Multi-stage build for .NET 8 app
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy csproj and restore dependencies
COPY ["MyApp/MyApp.csproj", "MyApp/"]
RUN dotnet restore "MyApp/MyApp.csproj"

# Copy source and build
COPY . .
WORKDIR "/src/MyApp"
RUN dotnet build "MyApp.csproj" -c Release -o /app/build
RUN dotnet publish "MyApp.csproj" -c Release -o /app/publish /p:UseAppHost=false

# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
EXPOSE 80
EXPOSE 443

# Create non-root user
RUN useradd -m -s /bin/bash appuser
USER appuser

COPY --from=build /app/publish .
ENTRYPOINT ["dotnet", "MyApp.dll"]
"@ | Out-File -FilePath Dockerfile -Encoding utf8

# Build image with tag
docker build -t myapp:1.0.0 .

# Build with build arguments
docker build `
  --build-arg BUILD_DATE=$(Get-Date -Format "yyyy-MM-dd") `
  --build-arg VERSION="1.0.0" `
  -t myapp:1.0.0 .

# Build without cache (force rebuild)
docker build --no-cache -t myapp:1.0.0 .

# List all images
docker images

# List images with filter
docker images --filter "reference=myapp*"

# Tag image for registry
docker tag myapp:1.0.0 myregistry.azurecr.io/myapp:1.0.0
docker tag myapp:1.0.0 myregistry.azurecr.io/myapp:latest

# Push to Docker Hub (after docker login)
docker login
docker push myusername/myapp:1.0.0

# Push to Azure Container Registry
az acr login --name myregistry
docker push myregistry.azurecr.io/myapp:1.0.0

# Pull image from registry
docker pull myregistry.azurecr.io/myapp:1.0.0

# Remove image
docker rmi myapp:1.0.0

# Remove all unused images
docker image prune -a

# View image history (layers)
docker history myapp:1.0.0

# Save image to tar file
docker save -o myapp.tar myapp:1.0.0

# Load image from tar file
docker load -i myapp.tar

# Scan image for vulnerabilities
docker scan myapp:1.0.0

# Build and tag for multiple platforms (buildx)
docker buildx create --use
docker buildx build --platform linux/amd64,linux/arm64 -t myapp:1.0.0 --push .
```

### Docker Compose Multi-Container Applications

Orchestrate complex multi-container applications with Docker Compose including databases, caching, and web services.

```powershell
# Create docker-compose.yml for full-stack application
@"
version: '3.8'

services:
  # PostgreSQL database
  postgres:
    image: postgres:15-alpine
    container_name: app-postgres
    environment:
      POSTGRES_DB: appdb
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser -d appdb"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # Redis cache
  redis:
    image: redis:7-alpine
    container_name: app-redis
    command: redis-server --requirepass redispassword
    volumes:
      - redis_data:/data
    networks:
      - backend
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
    restart: unless-stopped

  # .NET API backend
  api:
    build:
      context: ./api
      dockerfile: Dockerfile
    container_name: app-api
    environment:
      ASPNETCORE_ENVIRONMENT: Production
      ConnectionStrings__Database: Host=postgres;Database=appdb;Username=appuser;Password_File=/run/secrets/db_password
      ConnectionStrings__Redis: redis:6379,password=redispassword
    secrets:
      - db_password
    ports:
      - "5000:80"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - frontend
      - backend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  # Nginx reverse proxy
  nginx:
    image: nginx:alpine
    container_name: app-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    networks:
      - frontend
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # No external access

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local

secrets:
  db_password:
    file: ./secrets/db_password.txt
"@ | Out-File -FilePath docker-compose.yml -Encoding utf8

# Start all services in detached mode
docker-compose up -d

# View logs from all services
docker-compose logs

# Follow logs from specific service
docker-compose logs -f api

# List running services
docker-compose ps

# Execute command in service container
docker-compose exec api sh

# Scale specific service (if configured)
docker-compose up -d --scale api=3

# Stop all services
docker-compose stop

# Stop and remove containers, networks
docker-compose down

# Stop and remove with volumes (data loss!)
docker-compose down -v

# Rebuild services
docker-compose build

# Rebuild and restart services
docker-compose up -d --build

# View service configuration
docker-compose config

# Validate docker-compose.yml syntax
docker-compose config --quiet

# Pull latest images for all services
docker-compose pull
```

### Volume and Network Management

Manage persistent data storage and container networking with Docker volumes and custom network configurations.

```powershell
# Create named volume
docker volume create app_data

# Create volume with specific driver options
docker volume create --driver local `
  --opt type=none `
  --opt device=${PWD}/data `
  --opt o=bind `
  app_data_bind

# List all volumes
docker volume ls

# Inspect volume details
docker volume inspect app_data

# Mount volume to container
docker run -d `
  --name app `
  -v app_data:/app/data `
  -v ${PWD}/config:/app/config:ro `
  myapp:1.0.0

# Use bind mount for development
docker run -d `
  --name dev-app `
  -v ${PWD}/src:/app/src `
  -v ${PWD}/logs:/app/logs `
  myapp:dev

# Create tmpfs mount (in-memory, non-persistent)
docker run -d `
  --name temp-app `
  --tmpfs /tmp:rw,size=100m `
  myapp:1.0.0

# Copy data from volume
docker run --rm `
  -v app_data:/source `
  -v ${PWD}/backup:/backup `
  alpine tar czf /backup/app_data.tar.gz -C /source .

# Remove unused volumes
docker volume prune

# Remove specific volume
docker volume rm app_data

# Create custom bridge network
docker network create --driver bridge app_network

# Create network with custom subnet
docker network create `
  --driver bridge `
  --subnet=172.20.0.0/16 `
  --gateway=172.20.0.1 `
  custom_network

# List networks
docker network ls

# Inspect network
docker network inspect app_network

# Connect running container to network
docker network connect app_network webserver

# Disconnect container from network
docker network disconnect app_network webserver

# Run container on custom network
docker run -d `
  --name app1 `
  --network app_network `
  --network-alias app1.local `
  myapp:1.0.0

# Run container with custom DNS
docker run -d `
  --name app2 `
  --network app_network `
  --dns 8.8.8.8 `
  --dns-search example.com `
  myapp:1.0.0

# Test network connectivity between containers
docker run --rm `
  --network app_network `
  nicolaka/netshoot `
  curl http://app1.local

# Remove unused networks
docker network prune

# Remove specific network
docker network rm app_network
```

### System Monitoring and Cleanup

Monitor Docker system resources, clean up unused resources, and maintain optimal Docker environment.

```powershell
# View Docker disk usage
docker system df

# Detailed disk usage with container sizes
docker system df -v

# Get real-time system events
docker events

# Filter events by type
docker events --filter "type=container"

# Monitor specific container events
docker events --filter "container=webserver"

# View Docker daemon info
docker info

# Get Docker version details
docker version

# Monitor container resource usage
docker stats

# Get one-time stats snapshot
docker stats --no-stream

# Monitor specific containers
docker stats webserver redis postgres

# Export stats to CSV
docker stats --no-stream --format "table {{.Container}},{{.CPUPerc}},{{.MemUsage}}" | `
  Out-File -FilePath docker-stats.csv

# Remove all stopped containers
docker container prune

# Remove all unused images
docker image prune -a

# Remove all unused volumes
docker volume prune

# Remove all unused networks
docker network prune

# Complete system cleanup (all unused resources)
docker system prune -af --volumes

# Scheduled cleanup task (run weekly)
$action = New-ScheduledTaskAction -Execute "docker" -Argument "system prune -af"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 2am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "DockerCleanup" `
  -Description "Weekly Docker system cleanup"

# Check container health status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# List containers by health status
docker ps --filter "health=healthy"
docker ps --filter "health=unhealthy"

# Get container top processes
docker top webserver

# View container port mappings
docker port webserver

# Export all Docker objects to backup
docker save $(docker images -q) -o docker-images-backup.tar
docker ps -aq | ForEach-Object { docker export $_ | Out-File -FilePath "container-$_.tar" -Encoding byte }

# Get Docker daemon logs (Windows)
Get-EventLog -LogName Application -Source Docker | Select-Object -First 50
```

## Troubleshooting

**Docker Desktop Not Starting**:

- **Error**: "Docker Desktop starting..." indefinitely
  - **Check WSL 2**: `wsl --status` and `wsl --set-default-version 2`
  - **Reset Docker**: Right-click Docker Desktop tray icon → Troubleshoot → Reset to factory defaults
  - **Check Hyper-V**: Ensure Hyper-V and Windows Hypervisor Platform are enabled
  - **View logs**: `Get-Content "$env:LOCALAPPDATA\Docker\log.txt" -Tail 50`

**Port Already in Use**:

- **Error**: "Bind for 0.0.0.0:8080 failed: port is already allocated"
  - **Find process**: `Get-NetTCPConnection -LocalPort 8080 | Select-Object OwningProcess | Get-Process`
  - **Kill process**: `Stop-Process -Id <ProcessId> -Force`
  - **Use different port**: Change port mapping to `-p 8081:80`

**Container Exits Immediately**:

```powershell
# Check container logs
docker logs <container_id>

# View exit code
docker inspect <container_id> --format='{{.State.ExitCode}}'

# Run with interactive terminal for debugging
docker run -it --entrypoint sh myimage

# Override CMD/ENTRYPOINT for troubleshooting
docker run -it --entrypoint /bin/bash myimage
```

**Network Connectivity Issues**:

```powershell
# Test DNS resolution inside container
docker run --rm alpine nslookup google.com

# Test network connectivity
docker run --rm nicolaka/netshoot ping 8.8.8.8

# Check container network settings
docker inspect <container> | ConvertFrom-Json | Select-Object -ExpandProperty NetworkSettings

# Restart Docker network service
Restart-Service docker
```

**Volume Permission Issues**:

```powershell
# Check volume mount permissions
docker run --rm -v myvolume:/data alpine ls -la /data

# Fix Windows file permissions
icacls "C:\path\to\folder" /grant "Everyone:(OI)(CI)F" /T
```

## Performance and Tuning

**Docker Desktop Resource Allocation**:

```powershell
# Optimal settings for development (16GB RAM system)
$settings = @{
    memoryMiB = 8192
    cpus = 4
    diskSizeMiB = 102400
    swapMiB = 2048
}

# Apply via Docker Desktop settings or edit settings.json
$settingsPath = "$env:APPDATA\Docker\settings.json"
$currentSettings = Get-Content $settingsPath | ConvertFrom-Json
$currentSettings.memoryMiB = $settings.memoryMiB
$currentSettings.cpus = $settings.cpus
$currentSettings | ConvertTo-Json | Set-Content $settingsPath
```

**Container Resource Limits**:

```powershell
# Set memory and CPU limits
docker run -d `
  --name limited-app `
  --memory="512m" `
  --memory-swap="512m" `
  --cpus="0.5" `
  --cpu-shares=512 `
  --pids-limit=100 `
  myapp:1.0.0

# Monitor resource usage
docker stats limited-app --no-stream
```

**Build Performance Optimization**:

```powershell
# Use BuildKit for faster builds
$env:DOCKER_BUILDKIT=1
docker build -t myapp:1.0.0 .

# Enable BuildKit permanently in daemon.json
@"
{
  "features": {
    "buildkit": true
  }
}
"@ | Out-File -FilePath "$env:APPDATA\Docker\daemon.json" -Encoding utf8

# Use build cache mount for dependencies
docker build --build-arg BUILDKIT_INLINE_CACHE=1 -t myapp:1.0.0 .

# Parallel builds with docker-compose
docker-compose build --parallel
```

**Image Size Optimization**:

```powershell
# Use multi-stage builds
# Use alpine/slim base images
# Remove build dependencies in same layer
# Minimize layers by combining RUN commands

# Example optimized Dockerfile
@"
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine
WORKDIR /app
COPY --from=build /app/node_modules ./node_modules
COPY . .
USER node
CMD ["node", "index.js"]
"@ | Out-File -FilePath Dockerfile -Encoding utf8
```

**Performance Monitoring**:

```powershell
# Continuous monitoring script
while ($true) {
    Clear-Host
    Write-Host "Docker Performance Monitor - $(Get-Date)" -ForegroundColor Cyan
    Write-Host ""

    # System stats
    docker system df
    Write-Host ""

    # Container stats
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

    Start-Sleep -Seconds 5
}
```

## References and Further Reading

- [Docker Documentation](https://docs.docker.com/) - Official comprehensive Docker documentation
- [Docker Hub](https://hub.docker.com/) - Public registry with official and community images
- [Docker Compose Documentation](https://docs.docker.com/compose/) - Multi-container application orchestration
- [Best Practices for Writing Dockerfiles](https://docs.docker.com/develop/dev-best-practices/) - Official optimization guide
- [Play with Docker](https://labs.play-with-docker.com/) - Free online Docker playground for testing
