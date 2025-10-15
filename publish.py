#!/usr/bin/env python3
"""
Publishing helper script for SAP Datasphere MCP Server
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {cmd}")
        print(f"Error: {e.stderr}")
        return None


def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking prerequisites...")
    
    # Check if git is installed
    if not run_command("git --version"):
        print("❌ Git is not installed")
        return False
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Not in the correct directory (pyproject.toml not found)")
        return False
    
    # Check if build tools are available
    try:
        import build
        import twine
        print("✅ Build tools available")
    except ImportError:
        print("⚠️ Installing build tools...")
        if not run_command("pip install build twine"):
            print("❌ Failed to install build tools")
            return False
    
    print("✅ Prerequisites check passed")
    return True


def update_author_info():
    """Interactive update of author information"""
    print("\n📝 Updating author information...")
    
    author_name = input("Enter your name: ").strip()
    author_email = input("Enter your email: ").strip()
    github_username = input("Enter your GitHub username: ").strip()
    repo_name = input("Enter repository name (sap-datasphere-mcp): ").strip() or "sap-datasphere-mcp"
    
    # Read current pyproject.toml
    with open("pyproject.toml", "r") as f:
        content = f.read()
    
    # Update author information
    content = content.replace('name = "Your Name"', f'name = "{author_name}"')
    content = content.replace('email = "your.email@example.com"', f'email = "{author_email}"')
    
    # Update GitHub URLs
    github_base = f"https://github.com/{github_username}/{repo_name}"
    content = content.replace(
        'Homepage = "https://github.com/yourusername/sap-datasphere-mcp"',
        f'Homepage = "{github_base}"'
    )
    content = content.replace(
        'Repository = "https://github.com/yourusername/sap-datasphere-mcp"',
        f'Repository = "{github_base}"'
    )
    content = content.replace(
        'Issues = "https://github.com/yourusername/sap-datasphere-mcp/issues"',
        f'Issues = "{github_base}/issues"'
    )
    
    # Write updated pyproject.toml
    with open("pyproject.toml", "w") as f:
        f.write(content)
    
    print("✅ Author information updated")
    return github_username, repo_name


def clean_sensitive_data():
    """Remove any sensitive data from the codebase"""
    print("\n🧹 Cleaning sensitive data...")
    
    # Files that might contain sensitive data
    sensitive_files = [
        "test_with_real_credentials.py",
        "quick_test.py"
    ]
    
    for file_path in sensitive_files:
        if Path(file_path).exists():
            print(f"⚠️ Found file with potential credentials: {file_path}")
            response = input(f"Remove credentials from {file_path}? (Y/n): ")
            if response.lower() != 'n':
                # Replace actual credentials with placeholders
                with open(file_path, "r") as f:
                    content = f.read()
                
                # Replace known credential patterns
                content = content.replace(
                    'client_id = "sb-60cb266e-ad9d-49f7-9967-b53b8286a259!b130936|client!b3944"',
                    'client_id = "your-client-id-here"'
                )
                content = content.replace(
                    'client_secret = "caaea1b9-b09b-4d28-83fe-09966d525243$LOFW4h5LpLvB3Z2FE0P7FiH4-C7qexeQPi22DBiHbz8="',
                    'client_secret = "your-client-secret-here"'
                )
                content = content.replace(
                    'tenant_url = "https://f45fa9cc-f4b5-4126-ab73-b19b578fb17a.eu10.hcs.cloud.sap"',
                    'tenant_url = "https://your-tenant.eu10.hcs.cloud.sap"'
                )
                content = content.replace(
                    'token_url = "https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/token"',
                    'token_url = "https://your-auth.authentication.eu20.hana.ondemand.com/oauth/token"'
                )
                
                with open(file_path, "w") as f:
                    f.write(content)
                
                print(f"✅ Cleaned {file_path}")
    
    print("✅ Sensitive data cleanup completed")


def init_git_repo(github_username, repo_name):
    """Initialize git repository"""
    print("\n📦 Initializing Git repository...")
    
    # Check if already a git repo
    if Path(".git").exists():
        print("✅ Git repository already initialized")
        return True
    
    # Initialize git
    if not run_command("git init"):
        return False
    
    # Add all files
    if not run_command("git add ."):
        return False
    
    # Initial commit
    if not run_command('git commit -m "Initial commit: SAP Datasphere MCP Server v0.1.0"'):
        return False
    
    # Set main branch
    if not run_command("git branch -M main"):
        return False
    
    print("✅ Git repository initialized")
    return True


def build_package():
    """Build the Python package"""
    print("\n🔨 Building package...")
    
    # Clean previous builds
    if Path("dist").exists():
        import shutil
        shutil.rmtree("dist")
    
    # Build package
    if not run_command("python -m build"):
        return False
    
    print("✅ Package built successfully")
    return True


def publish_to_github(github_username, repo_name):
    """Instructions for GitHub publishing"""
    print(f"\n🐙 GitHub Publishing Instructions:")
    print("=" * 50)
    print(f"1. Go to https://github.com/new")
    print(f"2. Repository name: {repo_name}")
    print(f"3. Description: SAP Datasphere MCP Server - AI-powered access to SAP Datasphere APIs")
    print(f"4. Make it Public")
    print(f"5. Don't initialize with README (we have our own)")
    print(f"6. Click 'Create repository'")
    print(f"\n7. Then run these commands:")
    print(f"   git remote add origin https://github.com/{github_username}/{repo_name}.git")
    print(f"   git push -u origin main")
    
    input("\nPress Enter when you've created the GitHub repository...")
    
    # Add remote and push
    github_url = f"https://github.com/{github_username}/{repo_name}.git"
    
    if not run_command(f"git remote add origin {github_url}"):
        print("⚠️ Remote might already exist, continuing...")
    
    if run_command("git push -u origin main"):
        print("✅ Code pushed to GitHub!")
        return True
    else:
        print("❌ Failed to push to GitHub")
        return False


def publish_to_pypi():
    """Instructions for PyPI publishing"""
    print(f"\n🐍 PyPI Publishing Instructions:")
    print("=" * 50)
    print("1. Create PyPI account at https://pypi.org/account/register/")
    print("2. Verify your email")
    print("3. Go to https://pypi.org/manage/account/token/")
    print("4. Create API token with scope 'Entire account'")
    print("5. Copy the token (starts with 'pypi-')")
    
    input("\nPress Enter when you have your PyPI API token...")
    
    # Test upload to TestPyPI first
    print("\n🧪 Testing upload to TestPyPI...")
    test_result = run_command("twine upload --repository testpypi dist/*")
    
    if test_result is not None:
        print("✅ Test upload successful!")
        
        # Ask for production upload
        response = input("\nUpload to production PyPI? (Y/n): ")
        if response.lower() != 'n':
            print("\n🚀 Uploading to production PyPI...")
            if run_command("twine upload dist/*"):
                print("✅ Package published to PyPI!")
                return True
            else:
                print("❌ Failed to upload to PyPI")
                return False
    else:
        print("❌ Test upload failed")
        return False


def main():
    """Main publishing workflow"""
    print("🚀 SAP Datasphere MCP Server Publishing Tool")
    print("=" * 60)
    
    if not check_prerequisites():
        sys.exit(1)
    
    github_username, repo_name = update_author_info()
    clean_sensitive_data()
    
    if not init_git_repo(github_username, repo_name):
        print("❌ Git initialization failed")
        sys.exit(1)
    
    if not build_package():
        print("❌ Package build failed")
        sys.exit(1)
    
    # GitHub publishing
    if publish_to_github(github_username, repo_name):
        print(f"✅ GitHub: https://github.com/{github_username}/{repo_name}")
    
    # PyPI publishing
    if publish_to_pypi():
        print(f"✅ PyPI: https://pypi.org/project/sap-datasphere-mcp/")
    
    print(f"\n🎉 Publishing completed!")
    print(f"\n📋 Next steps:")
    print(f"• Test installation: pip install sap-datasphere-mcp")
    print(f"• Create GitHub release")
    print(f"• Add repository topics")
    print(f"• Share with the community!")


if __name__ == "__main__":
    main()