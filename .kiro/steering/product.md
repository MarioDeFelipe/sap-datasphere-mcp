# AWS MCP Servers

AWS MCP Servers is a comprehensive suite of specialized Model Context Protocol (MCP) servers that provide AI applications with seamless access to AWS services, documentation, and best practices.

## What it does

The project provides 40+ MCP servers that enable AI assistants to:
- Access real-time AWS documentation and API references
- Manage AWS infrastructure through CDK, Terraform, and CloudFormation
- Interact with AWS services like Lambda, EKS, RDS, S3, and more
- Query knowledge bases and perform enterprise search
- Generate diagrams and documentation
- Execute serverless workflows and container operations

## Key Value Propositions

- **Enhanced AI Output Quality**: Provides current AWS context to reduce hallucinations and improve accuracy
- **Workflow Automation**: Converts complex AWS operations into simple AI-accessible tools
- **Up-to-date Information**: Bridges the gap between AI training data and latest AWS capabilities
- **Standardized Integration**: Uses the open Model Context Protocol for consistent AI application integration

## Target Users

- Developers using AI coding assistants (Cursor, Cline, VS Code, Amazon Q Developer)
- DevOps engineers managing AWS infrastructure
- Solutions architects designing cloud systems
- Enterprise teams building AI-powered workflows

## Architecture

Each MCP server is a lightweight, standalone program that exposes specific AWS capabilities through the standardized MCP protocol. Servers can run locally or remotely and connect 1:1 with MCP clients.