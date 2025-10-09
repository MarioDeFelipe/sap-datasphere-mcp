# SAP Datasphere Control Panel - Docker Development Environment

## 🚀 Quick Start

### Prerequisites
- Docker installed on your system
- Docker Compose installed

### 1. Build and Run
```bash
# Navigate to the docker development directory
cd docker-dev-environment

# Build and start the containers
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

### 2. Access the Application
- **Web Interface**: http://localhost:8000
- **API Endpoint**: http://localhost:8000/api/hello
- **Health Check**: http://localhost:8000/health
- **Status**: http://localhost:8000/api/status

### 3. Development Workflow

#### Hot Reload Development
The application supports hot reload - any changes you make to the code will automatically restart the server.

#### View Logs
```bash
# View application logs
docker-compose logs -f sap-datasphere-app

# View all logs
docker-compose logs -f
```

#### Access Container Shell
```bash
# Access the application container
docker-compose exec sap-datasphere-app bash

# Or using docker directly
docker exec -it sap-datasphere-dev bash
```

### 4. Available Services

#### Main Application
- **Container**: `sap-datasphere-dev`
- **Port**: 8000
- **Environment**: Development with debug enabled

#### PostgreSQL Database (Optional)
- **Container**: `sap-datasphere-db`
- **Port**: 5432
- **Database**: `datasphere_dev`
- **User**: `developer`
- **Password**: `devpass123`

### 5. API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Hello World homepage with Datasphere integration |
| `/api/hello` | GET | Hello World API response |
| `/api/status` | GET | System status information |
| `/api/datasphere/connect` | POST | Connect to SAP Datasphere and retrieve data products |
| `/api/datasphere/products` | GET | Get available data products from SAP Datasphere |
| `/health` | GET | Health check endpoint |

### 5.1. New SAP Datasphere Features

#### 🔗 Datasphere Connection
The application now includes integrated SAP Datasphere connectivity:

- **Connect Button**: Establishes connection to SAP Datasphere tenant
- **Data Products Explorer**: Browse available analytical datasets, views, and tables
- **Schema Discovery**: View column definitions, data types, and metadata
- **Real-time Status**: Check data product availability and ownership information

#### 📊 Data Products Interface
- View comprehensive data product information including:
  - Product name, description, and type
  - Row counts and column schemas
  - Creation and update timestamps
  - Owner information and tags
  - Status indicators (active, development, etc.)

#### 🧪 Testing Suite
Run the integration test suite:
```bash
# Test the Datasphere integration
python test_datasphere_integration.py
```

### 6. Development Commands

```bash
# Stop containers
docker-compose down

# Rebuild containers
docker-compose build --no-cache

# View running containers
docker-compose ps

# Remove all containers and volumes
docker-compose down -v

# Follow logs
docker-compose logs -f
```

### 7. Next Steps for SAP Datasphere Integration

1. **Add SAP Datasphere API Client**
   - Implement authentication
   - Add API endpoints for catalog access
   - Handle SAP-specific data formats

2. **Enhance the Control Panel**
   - Add asset discovery features
   - Implement data visualization
   - Add user management

3. **Database Integration**
   - Connect to PostgreSQL for caching
   - Store user preferences
   - Cache SAP Datasphere responses

4. **Production Deployment**
   - Create production Dockerfile
   - Add environment-specific configurations
   - Implement proper logging and monitoring

### 8. Environment Variables

Create a `.env` file for local development:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1

# SAP Datasphere Configuration
SAP_DATASPHERE_URL=https://your-tenant.eu10.hcs.cloud.sap
SAP_DATASPHERE_USERNAME=your-username
SAP_DATASPHERE_PASSWORD=your-password
SAP_DATASPHERE_SPACE=your-space

# Database Configuration
DATABASE_URL=postgresql://developer:devpass123@postgres:5432/datasphere_dev
```

### 9. Troubleshooting

#### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

#### Container Won't Start
```bash
# Check container logs
docker-compose logs sap-datasphere-app

# Rebuild without cache
docker-compose build --no-cache
```

#### Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
```

## 🎯 Ready for Development!

Your Docker development environment is now ready. You can start building your SAP Datasphere Control Panel with:

- ✅ Hot reload development
- ✅ Containerized environment
- ✅ Database ready for integration
- ✅ API structure in place
- ✅ Modern web interface

Happy coding! 🚀