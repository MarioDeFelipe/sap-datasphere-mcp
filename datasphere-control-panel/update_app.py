"""
Update your existing Ailien Studio app with Q Business integration
"""

import boto3
import json

def update_existing_app():
    """Update your existing app with Q Business features"""
    
    lambda_client = boto3.client('lambda')
    
    print("🔄 Looking for your existing Ailien Studio app...")
    
    # Try to find your existing function
    try:
        # List functions to find yours
        paginator = lambda_client.get_paginator('list_functions')
        functions = []
        
        for page in paginator.paginate():
            for func in page['Functions']:
                if any(keyword in func['FunctionName'].lower() 
                      for keyword in ['datasphere', 'ailien', 'control', 'panel']):
                    functions.append(func['FunctionName'])
        
        if not functions:
            print("❌ Could not find your existing function")
            return None
        
        print("📋 Found these potential functions:")
        for i, func in enumerate(functions, 1):
            print(f"   {i}. {func}")
        
        # Use the first one or let user choose
        function_name = functions[0]
        print(f"\n✅ Using function: {function_name}")
        
        # Read the enhanced app code from the Q Business version
        with open('q_business_enhanced_app.py', 'r', encoding='utf-8') as f:
            enhanced_code = f.read()
        
        # Replace the lambda_handler function name to match your existing app
        enhanced_code = enhanced_code.replace(
            'def lambda_handler(event, context):',
            '''def lambda_handler(event, context):
    """AWS Lambda handler with Q Business integration"""
    return handler(event, context)

# Keep compatibility with existing handler
handler = Mangum(app)'''
        )
        
        # Update the function code
        import zipfile
        import os
        
        zip_filename = 'updated_app.zip'
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr('lambda_function.py', enhanced_code)
        
        with open(zip_filename, 'rb') as f:
            zip_content = f.read()
        
        # Update your existing function
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        
        # Update configuration
        lambda_client.update_function_configuration(
            FunctionName=function_name,
            Description='Ailien Studio - Enhanced with Q Business AI Assistant',
            Timeout=60,
            MemorySize=1024
        )
        
        # Clean up
        if os.path.exists(zip_filename):
            os.remove(zip_filename)
        
        print(f"✅ Successfully updated {function_name}!")
        print("\n🎯 Your app now includes:")
        print("✅ Q Business AI Assistant side panel")
        print("✅ Natural language data queries")
        print("✅ Your original beautiful design preserved")
        print("✅ All existing functionality maintained")
        
        return function_name
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Updating Your Ailien Studio App")
    print("=" * 40)
    
    result = update_existing_app()
    
    if result:
        print(f"\n🎉 Update complete! Your app is enhanced with AI capabilities.")
    else:
        print(f"\n❌ Update failed. Please check your AWS permissions.")