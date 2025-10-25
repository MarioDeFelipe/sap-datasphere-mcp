#!/usr/bin/env python3
"""
Basic tests for Ailien Platform Control Panel
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["service"] == "ailien-platform"

def test_dashboard():
    """Test dashboard endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Ailien Platform Control Panel" in response.text
    assert "Containerized Version" in response.text

def test_overview_api():
    """Test overview API endpoint"""
    response = client.get("/api/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["total_products"] == 1247

def test_chat_api():
    """Test chat API endpoint"""
    response = client.post("/api/chat", json={"message": "test message"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "timestamp" in data
    assert "conversation_id" in data

if __name__ == "__main__":
    pytest.main([__file__])