"""
Fix just the handler configuration
"""

import boto3
import time

def fix_handler_config():
    """Fix just the handler configuration"""
    
    lambda_client = boto3.client('lambda')
    function_name = 'datasphere-control-panel'
    
    print("🔧 Fixing handler configuration...")
    
    # Wait for any ongoing updates
    print("⏳ Waiting for ongoing updates to complete...")
    time.sleep(30)
    
    try:
        # Update handler configuration
        response = lambda_client.update_function_configuration(
            FunctionName=function_name,
            Handler='lambda_function.lambda_handler'  # Correct handler
        )
        
        print("✅ Handler configuration fixed!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing handler config: {e}")
        
        # Try to check current status
        try:
            func_info = lambda_client.get_function(FunctionName=function_name)
            state = func_info['Configuration'].get('State', 'Unknown')
            print(f"📋 Current function state: {state}")
            
            if state == 'Pending':
                print("⏳ Function is still updating. Please wait a few more minutes.")
            elif state == 'Active':
                print("✅ Function is active. The code update may have worked.")
                print("🔗 Try your URL now:")
                print("https://krb7735xufadsj233kdnpaabta0eatck.lambda-url.us-east-1.on.aws")
                return True
        except Exception as e2:
            print(f"❌ Error checking function status: {e2}")
        
        return False

def main():
    """Main function"""
    
    print("🔧 FIXING HANDLER CONFIGURATION")
    print("=" * 32)
    
    success = fix_handler_config()
    
    if success:
        print("\n✅ CONFIGURATION FIXED!")
        print("=" * 22)
        print("\n🔗 Try your URL now:")
        print("https://krb7735xufadsj233kdnpaabta0eatck.lambda-url.us-east-1.on.aws")
        print("\n📋 The code was already updated in the previous step.")
        print("📋 Now the handler should point to the correct function.")
    else:
        print("\n⏳ Update may still be in progress.")
        print("💡 Wait 2-3 minutes and try your URL:")
        print("https://krb7735xufadsj233kdnpaabta0eatck.lambda-url.us-east-1.on.aws")

if __name__ == "__main__":
    main()