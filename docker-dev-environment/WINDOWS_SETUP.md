# Windows Docker Setup Guide

## 🚀 Quick Setup for Windows

### Step 1: Install Docker Desktop

1. **Download Docker Desktop for Windows**
   - Go to: https://docs.docker.com/desktop/install/windows-install/
   - Download the installer
   - Run the installer as Administrator

2. **System Requirements**
   - Windows 10 64-bit: Pro, Enterprise, or Education (Build 19041 or higher)
   - OR Windows 11 64-bit: Home or Pro version 21H2 or higher
   - WSL 2 feature enabled
   - Virtualization enabled in BIOS

3. **Enable WSL 2 (if not already enabled)**
   ```powershell
   # Run as Administrator in PowerShell
   dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
   
   # Restart your computer, then run:
   wsl --set-default-version 2
   ```

### Step 2: Verify Installation

Open Command Prompt or PowerShell and run:
```cmd
docker --version
docker-compose --version
```

You should see version information for both commands.

### Step 3: Start Your Development Environment

1. **Navigate to the project directory**
   ```cmd
   cd docker-dev-environment
   ```

2. **Start the environment**
   ```cmd
   run.bat start
   ```

3. **Access your application**
   - Open browser: http://localhost:8000
   - You should see the "Hello World" page

### Step 4: Development Workflow

#### Available Commands
```cmd
run.bat start     # Start the environment
run.bat stop      # Stop the environment
run.bat restart   # Restart the environment
run.bat logs      # View application logs
run.bat shell     # Access container shell
run.bat status    # Check container status
run.bat clean     # Clean up everything
run.bat build     # Rebuild containers
```

#### Alternative: Direct Docker Commands
```cmd
# Start services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Access container shell
docker-compose exec sap-datasphere-app bash
```

### Step 5: Verify Everything Works

1. **Check the web interface**: http://localhost:8000
2. **Test the API**: http://localhost:8000/api/hello
3. **Check health**: http://localhost:8000/health

You should see:
- A beautiful "Hello World" page with Docker branding
- Working API endpoints
- System status information

### Troubleshooting

#### Docker Desktop Won't Start
- Make sure Hyper-V is enabled
- Check if WSL 2 is properly installed
- Restart your computer after installation

#### Port 8000 Already in Use
```cmd
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

#### Permission Issues
- Run Command Prompt as Administrator
- Make sure Docker Desktop is running

#### Container Won't Build
```cmd
# Clean everything and rebuild
run.bat clean
run.bat build
run.bat start
```

### Next Steps

Once your Docker environment is running:

1. **Develop your SAP Datasphere integration**
   - Edit `app.py` to add SAP API calls
   - Add authentication logic
   - Implement data processing

2. **Hot Reload Development**
   - Any changes to your code will automatically restart the server
   - No need to rebuild the container for code changes

3. **Add Database Integration**
   - PostgreSQL is already configured in docker-compose.yml
   - Connect to: `postgresql://developer:devpass123@postgres:5432/datasphere_dev`

4. **Scale Your Application**
   - Add more services to docker-compose.yml
   - Implement microservices architecture
   - Add Redis for caching

## 🎯 You're Ready!

Your Docker development environment provides:
- ✅ Containerized Python application
- ✅ Hot reload for development
- ✅ PostgreSQL database ready
- ✅ Modern web interface
- ✅ API structure in place
- ✅ Easy deployment workflow

Happy coding! 🚀