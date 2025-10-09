"""
Check CloudWatch logs to see what's causing the 500 error
"""

import boto3
import json
from datetime import datetime, timedelta

def check_lambda_logs():
    """Check CloudWatch logs for the Lambda function"""
    
    logs_client = boto3.client('logs')
    lambda_client = boto3.client('lambda')
    
    function_name = 'datasphere-control-panel'
    
    print("🔍 Checking CloudWatch logs for errors...")
    
    try:
        # Get the log group name
        log_group_name = f'/aws/lambda/{function_name}'
        
        # Get recent log events (last 30 minutes)
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=30)
        
        # Convert to milliseconds since epoch
        start_time_ms = int(start_time.timestamp() * 1000)
        end_time_ms = int(end_time.timestamp() * 1000)
        
        print(f"📋 Checking logs from {start_time.strftime('%H:%M:%S')} to {end_time.strftime('%H:%M:%S')}")
        
        # Get log events
        response = logs_client.filter_log_events(
            logGroupName=log_group_name,
            startTime=start_time_ms,
            endTime=end_time_ms,
            filterPattern='ERROR'
        )
        
        events = response.get('events', [])
        
        if events:
            print(f"\n❌ Found {len(events)} error events:")
            print("=" * 50)
            
            for event in events[-5:]:  # Show last 5 errors
                timestamp = datetime.fromtimestamp(event['timestamp'] / 1000)
                message = event['message'].strip()
                print(f"\n🕐 {timestamp.strftime('%H:%M:%S')}")
                print(f"📄 {message}")
                print("-" * 30)
        else:
            print("\n✅ No ERROR events found in recent logs")
            
            # Check for any recent events
            response = logs_client.filter_log_events(
                logGroupName=log_group_name,
                startTime=start_time_ms,
                endTime=end_time_ms
            )
            
            all_events = response.get('events', [])
            
            if all_events:
                print(f"\n📋 Found {len(all_events)} total log events:")
                print("Recent events:")
                
                for event in all_events[-3:]:  # Show last 3 events
                    timestamp = datetime.fromtimestamp(event['timestamp'] / 1000)
                    message = event['message'].strip()
                    print(f"\n🕐 {timestamp.strftime('%H:%M:%S')}")
                    print(f"📄 {message[:200]}...")
            else:
                print("\n⚠️ No recent log events found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking logs: {e}")
        return False

def check_function_config():
    """Check Lambda function configuration"""
    
    lambda_client = boto3.client('lambda')
    function_name = 'datasphere-control-panel'
    
    print("\n🔧 Checking Lambda function configuration...")
    
    try:
        response = lambda_client.get_function(FunctionName=function_name)
        
        config = response['Configuration']
        
        print(f"📋 Function Details:")
        print(f"   Runtime: {config.get('Runtime', 'Unknown')}")
        print(f"   Handler: {config.get('Handler', 'Unknown')}")
        print(f"   Timeout: {config.get('Timeout', 'Unknown')} seconds")
        print(f"   Memory: {config.get('MemorySize', 'Unknown')} MB")
        print(f"   State: {config.get('State', 'Unknown')}")
        print(f"   Last Modified: {config.get('LastModified', 'Unknown')}")
        
        # Check if function is in a failed state
        if config.get('State') == 'Failed':
            print(f"❌ Function is in FAILED state!")
            print(f"   Reason: {config.get('StateReason', 'Unknown')}")
        elif config.get('State') == 'Pending':
            print(f"⏳ Function is in PENDING state")
            print(f"   Reason: {config.get('StateReason', 'Update in progress')}")
        else:
            print(f"✅ Function state: {config.get('State', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking function config: {e}")
        return False

def test_function_directly():
    """Test the Lambda function directly"""
    
    lambda_client = boto3.client('lambda')
    function_name = 'datasphere-control-panel'
    
    print("\n🧪 Testing Lambda function directly...")
    
    try:
        # Create a test event
        test_event = {
            "requestContext": {
                "http": {
                    "method": "GET",
                    "path": "/",
                    "protocol": "HTTP/1.1"
                }
            },
            "headers": {
                "host": "example.com"
            },
            "isBase64Encoded": False
        }
        
        # Invoke the function
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(test_event)
        )
        
        # Read the response
        payload = response['Payload'].read()
        result = json.loads(payload)
        
        print(f"📋 Direct invocation result:")
        print(f"   Status Code: {response.get('StatusCode', 'Unknown')}")
        
        if 'errorMessage' in result:
            print(f"❌ Error Message: {result['errorMessage']}")
            print(f"❌ Error Type: {result.get('errorType', 'Unknown')}")
            if 'stackTrace' in result:
                print(f"📄 Stack Trace:")
                for line in result['stackTrace'][:5]:  # Show first 5 lines
                    print(f"   {line}")
        else:
            print(f"✅ Function executed successfully")
            print(f"   Response: {str(result)[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing function: {e}")
        return False

def main():
    """Main function"""
    
    print("🔍 DIAGNOSING LAMBDA FUNCTION ISSUES")
    print("=" * 45)
    
    # Step 1: Check function configuration
    check_function_config()
    
    # Step 2: Check CloudWatch logs
    check_lambda_logs()
    
    # Step 3: Test function directly
    test_function_directly()
    
    print("\n💡 RECOMMENDATIONS:")
    print("1. If function is in FAILED/PENDING state, wait for it to stabilize")
    print("2. Check the error messages above for specific issues")
    print("3. If there are import errors, we need to fix dependencies")
    print("4. If there are syntax errors, we need to fix the code")

if __name__ == "__main__":
    main()