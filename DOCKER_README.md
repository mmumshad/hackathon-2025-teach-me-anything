# 🐳 Docker Setup Guide

This guide will help you run the entire Teach Me Anything stack using Docker! 🚀

## 📋 Prerequisites

- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)

## 🚀 Quick Start

### 1. **Clone and Setup Environment**
```bash
# Clone the repository
git clone <your-repo-url>
cd hackathon-2025-teach-me-anything

# If you already have a .env file in backend/, it will be used automatically
# OR copy the template and configure it:
cp docker.env.template .env
```

### 2. **Configure Environment Variables**
Edit `.env` file with your API keys:
```bash
# Required API Keys
OPENAI_API_KEY=your_openai_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
MEM0_API_KEY=your_mem0_api_key_here

# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
SUPABASE_MCP_API_KEY=your_supabase_mcp_api_key_here

# Optional Settings
DEMO_MODE=false
```

### 3. **Run the Full Stack**
```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 4. **Access Your Application**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🛠️ Development Commands

### **Start Services**
```bash
# Start all services
docker-compose up

# Start specific service
docker-compose up backend
docker-compose up frontend
```

### **Stop Services**
```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### **View Logs**
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend

# Follow logs in real-time
docker-compose logs -f backend
```

### **Rebuild Services**
```bash
# Rebuild specific service
docker-compose build backend

# Rebuild and restart
docker-compose up --build backend
```

## 🔧 Service Details

### **Backend Service**
- **Port**: 8000
- **Framework**: FastAPI with Python 3.12
- **Health Check**: `/health` endpoint
- **Volumes**: `uploads/` and `downloads/` directories

### **Frontend Service**
- **Port**: 3000
- **Framework**: Next.js with React 19
- **Health Check**: Root endpoint
- **Dependencies**: Waits for backend to be healthy

## 📁 Volume Mounts

The following directories are mounted as volumes:
- `./backend/uploads` → `/app/uploads` (file uploads)
- `./backend/downloads` → `/app/downloads` (generated files)

## 🐛 Troubleshooting

### **Common Issues**

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   lsof -i :3000
   lsof -i :8000
   
   # Kill the process or change ports in docker-compose.yml
   ```

2. **Environment Variables Not Loading**
   ```bash
   # Check if .env file exists
   ls -la .env
   
   # Verify environment variables
   docker-compose config
   ```

3. **Build Failures**
   ```bash
   # Clean Docker cache
   docker system prune -a
   
   # Rebuild without cache
   docker-compose build --no-cache
   ```

4. **Permission Issues**
   ```bash
   # Fix upload directory permissions
   sudo chown -R $USER:$USER backend/uploads
   sudo chown -R $USER:$USER backend/downloads
   ```

### **Health Checks**

Check if services are running properly:
```bash
# Check service status
docker-compose ps

# Check health status
docker-compose exec backend curl http://localhost:8000/health
docker-compose exec frontend curl http://localhost:3000
```

## 🚀 Production Deployment

### **Environment Setup**
```bash
# Set production environment
export ENVIRONMENT=production
export DEBUG=false
export DEMO_MODE=false
```

### **Security Considerations**
- Use strong API keys
- Enable HTTPS in production
- Set up proper CORS origins
- Use Docker secrets for sensitive data

### **Scaling**
```bash
# Scale backend service
docker-compose up --scale backend=3

# Use load balancer (nginx example included)
docker-compose up nginx
```

## 📊 Monitoring

### **Resource Usage**
```bash
# Check resource usage
docker stats

# Check specific service
docker stats teachmeanything-backend
docker stats teachmeanything-frontend
```

### **Logs Analysis**
```bash
# Export logs
docker-compose logs > application.log

# Filter logs
docker-compose logs backend | grep ERROR
```

## 🎯 Best Practices

1. **Always use `.env` files** for configuration
2. **Keep Docker images updated** regularly
3. **Use health checks** for service dependencies
4. **Mount volumes** for persistent data
5. **Clean up unused images** periodically

## 🆘 Need Help?

If you encounter any issues:
1. Check the logs: `docker-compose logs`
2. Verify environment variables: `docker-compose config`
3. Check service health: `docker-compose ps`
4. Review this documentation

Happy coding! 🎉
