# SAP Datasphere MCP Server - Docker Container
# Production-ready container for easy deployment

FROM python:3.12-slim

# Metadata
LABEL maintainer="Mario DeFelipe <mariodefe@example.com>"
LABEL description="SAP Datasphere MCP Server - 41 tools, 98% real data coverage"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY sap_datasphere_mcp_server.py .
COPY auth/ ./auth/
COPY .env.example .

# Create directory for logs
RUN mkdir -p /app/logs

# Environment variables (override via docker run -e or docker-compose)
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO
ENV SERVER_PORT=8080
ENV USE_MOCK_DATA=false

# Health check hits the /health endpoint exposed by HTTP mode
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -fsS "http://127.0.0.1:${SERVER_PORT:-8080}/health" || exit 1

EXPOSE 8080

# Run as non-root user for security
RUN useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app
USER mcpuser

# Run the MCP server in HTTP (Streamable HTTP) mode for cloud deployment.
# Override CMD to "python sap_datasphere_mcp_server.py" for stdio mode.
CMD ["sh", "-c", "python sap_datasphere_mcp_server.py http 0.0.0.0 ${SERVER_PORT:-8080}"]
