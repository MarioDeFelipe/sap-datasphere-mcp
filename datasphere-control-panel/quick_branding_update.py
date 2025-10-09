#!/usr/bin/env python3
"""
Quick Branding Update - Remove rocket, add Ailien logo, change to light green
"""

import boto3
import json
import zipfile
import io
from datetime import datetime

def main():
    print("🎨 QUICK BRANDING UPDATE")
    print("=" * 30)
    
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
            
            # Make branding updates
            print("🎨 Applying branding updates...")
            
            # Change background color
            code = code.replace(
                'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);',
                'background: linear-gradient(135deg, #a8e6cf 0%, #88d8a3 100%);'
            )
            
            # Update button colors
            code = code.replace(
                'background: #667eea;',
                'background: #7cb342;'
            )
            code = code.replace(
                'background: #764ba2;',
                'background: #689f38;'
            )
            code = code.replace(
                'background: linear-gradient(135deg, #667eea, #764ba2);',
                'background: linear-gradient(135deg, #7cb342, #689f38);'
            )
            
            # Update logo section - remove rocket, add alien head
            old_logo = '''<div class="logo">🚀</div>'''
            new_logo = '''<div class="ailien-logo">
                    <div class="alien-head">
                        <div class="alien-eye left"></div>
                        <div class="alien-eye right"></div>
                    </div>
                </div>'''
            code = code.replace(old_logo, new_logo)
            
            # Add ailien branding
            old_title_section = '''<div>
                    <h1>Ailien Platform Control Panel</h1>
                    <div class="header-subtitle">AI-Powered SAP & AWS Data Integration</div>
                </div>'''
            new_title_section = '''<div>
                    <h1>Ailien Platform Control Panel</h1>
                    <div class="header-subtitle">AI-Powered SAP & AWS Data Integration</div>
                    <div class="ailien-brand">Powered by ailien.studio</div>
                </div>'''
            code = code.replace(old_title_section, new_title_section)
            
            # Add CSS for new elements
            css_additions = '''
        .ailien-logo {
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
        .alien-eye.right { right: 8px; }
        
        .ailien-brand {
            font-size: 0.8em;
            color: #7cb342;
            font-weight: 500;
            margin-top: 2px;
        }
        
        .footer .ailien-credit {
            color: #7cb342;
            font-weight: 600;
        }'''
            
            # Insert CSS before closing </style>
            code = code.replace('</style>', css_additions + '\n        </style>')
            
            # Update footer
            old_footer = '''<p>Ailien Platform Control Panel - Q Business Enhanced | Powered by Amazon Q Business & SAP Datasphere</p>'''
            new_footer = '''<p>Ailien Platform Control Panel | Powered by <span class="ailien-credit">ailien.studio</span> & Amazon Q Business</p>'''
            code = code.replace(old_footer, new_footer)
            
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
                        
                        if "ailien.studio" in content and "#a8e6cf" in content:
                            print("✅ Ailien Studio branding applied!")
                            print("\n🎉 BRANDING UPDATE SUCCESSFUL!")
                            print("=" * 40)
                            print("✅ Updated with Ailien Studio branding!")
                            print("🔗 URL: https://krb7735xufadsj233kdnpaabta0eatck.lambda-url.us-east-1.on.aws")
                            print("\n📋 Changes made:")
                            print("  🚫 Removed rocket icon")
                            print("  👽 Added Ailien Studio alien head logo")
                            print("  🟢 Changed to light green background")
                            print("  🎨 Updated all colors to green theme")
                            print("  📝 Added 'Powered by ailien.studio' branding")
                            return True
                        else:
                            print("⚠️ Branding partially applied")
                            return False
                            
            except Exception as e:
                print(f"❌ Error testing: {e}")
                return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    main()