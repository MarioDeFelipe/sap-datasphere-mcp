"""
SAP Datasphere MCP Server
Model Context Protocol server for SAP Datasphere integration
"""

from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sap-datasphere-mcp",
    version="1.0.0",
    author="Mario DeFelipe",
    author_email="mariodefe@example.com",
    description="Model Context Protocol server for SAP Datasphere integration with 41 tools and 98% real data coverage",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MarioDeFelipe/sap-datasphere-mcp",
    project_urls={
        "Bug Reports": "https://github.com/MarioDeFelipe/sap-datasphere-mcp/issues",
        "Source": "https://github.com/MarioDeFelipe/sap-datasphere-mcp",
        "Documentation": "https://github.com/MarioDeFelipe/sap-datasphere-mcp#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sap-datasphere-mcp=sap_datasphere_mcp_server:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", ".env.example"],
    },
    keywords="sap datasphere mcp model-context-protocol ai claude etl data-warehouse",
    license="MIT",
)
