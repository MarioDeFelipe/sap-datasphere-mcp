#!/usr/bin/env python3
"""
Remove Icon - Clean text-only branding
"""

import boto3
import json
import zipfile
import io
from datetime import datetime

def main():
    print("🚫 REMOVING ICON - CLEAN BRANDING")
    print("=" * 35)
    
    try:
        # Create Lambda client
        lambda_client = boto3.client('lambda')
        function_name = 'datasphere-control-panel'
        
        # Get current function code
        print("📥 Getting current function code...")
        response = lambda_client.get_function(FunctionName=function_name)
        
        # Download current code
        code_url = response['Code']['Location']
        import urllib.request
        with urllib.request.urlopen(code_url) as response:
            current_zip = response.read()
        
        # Extract and modify
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, 'current.zip')
            with open(zip_path, 'wb') as f:
                f.write(current_zip)
            
            # Extract
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Read lambda_function.py
            lambda_file = os.path.join(temp_dir, 'lambda_function.py')
            with open(lambda_file, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Remove icon completely
            print("🚫 Removing icon...")
            
            # Remove the entire logo section and replace with clean text
            old_logo_section = '''<div class="logo-section">
                <div class="ailien-logo">
                    <div class="alien-head">
                        <div class="alien-eye left"></div>
                        <div class="alien-eye right"></div>
                    </div>
                </div>
                <div>
                    <h1>Ailien Platform Control Panel</h1>
                    <div class="header-subtitle">AI-Powered SAP & AWS Data Integration</div>
                    <div class="ailien-brand">Powered by ailien.studio</div>
                </div>
            </div>'''
            
            new_logo_section = '''<div class="logo-section">
                <div>
                    <h1>Ailien Platform Control Panel</h1>
                    <div class="header-subtitle">AI-Powered SAP & AWS Data Integration</div>
                    <div class="ailien-brand">Powered by ailien.studio</div>
                </div>
            </div>'''
            
            code = code.replace(old_logo_section, new_logo_section)
            
            # Remove all icon-related CSS
            css_to_remove = [
                '''.ailien-logo {
            width: 60px;
            height: 60px;
            background: white;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            position: relative;
        }
        
        .alien-head {
            width: 35px;
            height: 40px;
            background: white;
            border: 3px solid #333;
            border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
            position: relative;
        }
        
        .alien-eye {
            position: absolute;
            width: 8px;
            height: 12px;
            background: #7cb342;
            border-radius: 50%;
            top: 15px;
        }
        
        .alien-eye.left { left: 8px; }
        .alien-eye.right { right: 8px; }''',
            ]
            
            for css_block in css_to_remove:
                code = code.replace(css_block, '')
            
            # Write updated code
            with open(lambda_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Create new zip
            new_zip_path = os.path.join(temp_dir, 'updated.zip')
            with zipfile.ZipFile(new_zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.write(lambda_file, 'lambda_function.py')
            
            # Read new zip
            with open(new_zip_path, 'rb') as f:
                new_zip_data = f.read()
            
            print(f"📦 Updating Lambda function: {function_name}")
            
            # Update Lambda function
            response = lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=new_zip_data
            )
            
            print(f"✅ Lambda function updated successfully!")
            print(f"📋 Version: {response.get('Version', 'Unknown')}")
            
            # Test
            print("🧪 Testing deployment...")
            import time
            time.sleep(3)
            
            function_url = "https://krb7735xufadsj233kdnpaabta0eatck.lambda-url.us-east-1.on.aws"
            
            try:
                req = urllib.request.Request(function_url)
                with urllib.request.urlopen(req, timeout=10) as response:
                    if response.status == 200:
                        content = response.read().decode('utf-8')
                        print(f"✅ Function URL is responding!")
                        
                        if "ailien.studio" in content and "alien-head" not in content:
                            print("✅ Icon removed successfully!")
                            print("\n🎉 ICON REMOVAL SUCCESSFUL!")
                            print("=" * 40)
                            print("✅ Clean text-only branding applied!")
                            print("🔗 URL: https://krb7735xufadsj233kdnpaabta0eatck.lambda-url.us-east-1.on.aws")
                            print("\n📋 Changes made:")
                            print("  🚫 Removed alien head icon completely")
                            print("  📝 Clean text-only header")
                            print("  🟢 Kept light green background")
                            print("  🎨 Maintained green color theme")
                            print("  📝 Kept 'Powered by ailien.studio' branding")
                            return True
                        else:
                            print("⚠️ Icon removal not complete")
                            return False
                            
            except Exception as e:
                print(f"❌ Error testing: {e}")
                return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    main()