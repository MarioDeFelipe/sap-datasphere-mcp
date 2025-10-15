#!/usr/bin/env python3
"""
Upload SAP Datasphere MCP Server v2.0 to PyPI
Simple script to upload the built package
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Upload to PyPI with proper instructions"""
    print("🚀 SAP Datasphere MCP Server v2.0 - PyPI Upload")
    print("=" * 60)
    
    # Change to package directory
    package_dir = Path(__file__).parent
    os.chdir(package_dir)
    
    # Check if dist files exist
    dist_dir = Path('dist')
    if not dist_dir.exists():
        print("❌ No dist/ directory found. Run deploy_v2.py first!")
        return False
    
    wheel_files = list(dist_dir.glob('*.whl'))
    tar_files = list(dist_dir.glob('*.tar.gz'))
    
    if not wheel_files or not tar_files:
        print("❌ No package files found in dist/. Run deploy_v2.py first!")
        return False
    
    print(f"📦 Found package files:")
    for file in wheel_files + tar_files:
        print(f"   • {file}")
    
    print(f"\n🔑 PyPI Authentication Instructions:")
    print(f"   1. Go to: https://pypi.org/manage/account/token/")
    print(f"   2. Create a new API token")
    print(f"   3. When prompted:")
    print(f"      • Username: __token__")
    print(f"      • Password: [your-api-token]")
    
    print(f"\n🚀 Uploading to PyPI...")
    
    try:
        # Upload to PyPI
        cmd = [sys.executable, '-m', 'twine', 'upload', 'dist/*']
        result = subprocess.run(cmd, check=True)
        
        print(f"\n🎉 SUCCESS: SAP Datasphere MCP Server v2.0 uploaded to PyPI!")
        print(f"📦 Install with: pip install sap-datasphere-mcp==2.0.0")
        print(f"🔗 View at: https://pypi.org/project/sap-datasphere-mcp/")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Upload failed!")
        print(f"   Error code: {e.returncode}")
        print(f"\n💡 Common solutions:")
        print(f"   • Make sure you're using the correct API token")
        print(f"   • Check that the package name isn't already taken")
        print(f"   • Verify your PyPI account has upload permissions")
        
        return False
    except KeyboardInterrupt:
        print(f"\n⚠️ Upload cancelled by user")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print(f"\n🏆 DEPLOYMENT TO PYPI SUCCESSFUL! 🚀")
    else:
        print(f"\n🔧 Try again after checking the instructions above")