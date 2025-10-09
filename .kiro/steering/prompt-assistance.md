# Prompt Assistance & Quick Actions

## Predefined Prompts Available

This project includes a comprehensive collection of predefined prompts similar to Amazon Q Business. These prompts are designed to help you quickly accomplish common development tasks with Kiro.

### Quick Access

- **Prompt Library**: `.kiro/prompts/predefined-prompts.md` - Complete collection of curated prompts
- **Quick Selector**: Use the "Quick Prompt Selector" hook in the Agent Hooks panel
- **Categories Available**:
  - 🚀 Quick Start (Code Analysis, Generation, Refactoring)
  - 🏗️ Architecture & Design (System Design, Infrastructure)
  - 🔧 Development Workflow (Testing, Documentation)
  - ☁️ AWS & Cloud (Lambda, Containers, Kubernetes)
  - 🔒 Security & Compliance (Audits, Best Practices)
  - 🐛 Debugging & Troubleshooting (Error Investigation, Monitoring)
  - 📊 Data & Analytics (Processing, ML/AI)
  - 🔄 DevOps & Automation (CI/CD, Deployment)
  - 🎯 Project-Specific (SAP Datasphere, MCP Servers)
  - 💡 Learning & Exploration (Research, Code Learning)
  - 🎨 UI/UX & Frontend (React, Accessibility)

### How to Use

1. **Browse Prompts**: Open `.kiro/prompts/predefined-prompts.md` to see all available prompts
2. **Copy & Paste**: Select the prompt that matches your need and paste it into chat
3. **Customize**: Replace placeholders with your specific requirements
4. **Add Context**: Include relevant files using `#File` or `#Folder` references
5. **Iterate**: Use follow-up prompts to refine results

### Popular Prompts

Here are some of the most commonly used prompts:

**Code Quality**:
- "Analyze this code for potential issues, security vulnerabilities, and performance improvements"
- "Refactor this code to be more readable, maintainable, and follow modern best practices"

**AWS & Cloud**:
- "Design a scalable architecture for [your system] using AWS services"
- "Create Terraform configuration for deploying this application with proper security"

**Testing & Documentation**:
- "Generate comprehensive unit tests for this code including edge cases"
- "Create detailed API documentation with examples and usage guidelines"

**Debugging**:
- "Help me debug this error: [error message]. Analyze and suggest solutions"
- "This code is running slowly. Profile it and suggest optimizations"

### Adding Custom Prompts

You can extend the prompt library by adding your own prompts to the predefined-prompts.md file. Follow the existing format and categories for consistency.

### Integration with Workflows

These prompts work seamlessly with:
- File context (`#File`, `#Folder`)
- Problem detection (`#Problems`)
- Git integration (`#Git Diff`)
- Terminal output (`#Terminal`)
- Codebase scanning (`#Codebase`)

This makes Kiro even more powerful by providing structured, proven prompts for common development scenarios.