"""
SAP Datasphere MCP Server

A Model Context Protocol server for SAP Datasphere integration.
"""

__version__ = "0.1.0"
__author__ = "Mario de Felipe"
__email__ = "mario@ailien.studio"

from .server import app

__all__ = ["app"]