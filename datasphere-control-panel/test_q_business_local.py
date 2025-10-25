"""
Local testing for Q Business Enhanced Control Panel
Run this to test the enhanced control panel locally before deployment
"""

import json
import os
import webbrowser
from datetime import datetime
import http.server
import socketserver
import threading
import time

# Import the enhanced app
from q_business_enhanced_app import lambda_handler, create_enhanced_control_panel

class LocalTestServer:
    """Local test server for the enhanced control panel"""
    
    def __init__(self, port=8080):
        self.port = port
        self.server = None
        self.thread = None
    
    def start_server(self):
        """Start local test server"""
        
        class CustomHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/' or self.path == '/index.html':
                    # Serve the enhanced control panel
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    
                    # Generate the enhanced control panel HTML
                    html_content = create_enhanced_control_panel()
                    self.wfile.write(html_content.encode('utf-8'))
                    
                elif self.path.startswith('/api/'):
                    # Handle API requests
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    
                    # Mock API response
                    if 'q-business/query' in self.path:
                        response = {
                            'answer': 'Mock Q Business response for local testing',
                            'sources': ['DataProduct1', 'DataProduct2'],
                            'confidence': 0.95
                        }
                    else:
                        response = {'status': 'success', 'message': 'Local test API'}
                    
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                else:
                    super().do_GET()
            
            def do_POST(self):
                # Handle POST requests for API testing
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {
                    'status': 'success',
                    'message': 'Local test POST response',
                    'received_data': post_data.decode('utf-8')
                }
                
                self.wfile.write(json.dumps(response).encode('utf-8'))
        
        # Start server in a separate thread
        def run_server():
            with socketserver.TCPServer(("", self.port), CustomHandler) as httpd:
                self.server = httpd
                print(f"🌐 Local test server running on http://localhost:{self.port}")
                httpd.serve_forever()
        
        self.thread = threading.Thread(target=run_server, daemon=True)
        self.thread.start()
        
        # Give server time to start
        time.sleep(1)
        
        return f"http://localhost:{self.port}"
    
    def stop_server(self):
        """Stop the local test server"""
        if self.server:
            self.server.shutdown()
            print("🛑 Local test server stopped")

def test_lambda_function():
    """Test the Lambda function locally"""
    
    print("🧪 Testing Lambda Function Locally")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            'name': 'Homepage Request',
            'event': {
                'path': '/',
                'httpMethod': 'GET',
                'headers': {},
                'body': None
            }
        },
        {
            'name': 'Q Business Query',
            'event': {
                'path': '/api/q-business/query',
                'httpMethod': 'POST',
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'query': 'Which data products have the highest quality scores?'})
            }
        },
        {
            'name': 'Metadata Collection',
            'event': {
                'path': '/api/metadata/collect',
                'httpMethod': 'POST',
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'table_name': 'customer_data'})
            }
        }
    ]
    
    # Run tests
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print("-" * 30)
        
        try:
            result = lambda_handler(test_case['event'], None)
            
            print(f"✅ Status Code: {result['statusCode']}")
            print(f"📄 Content Type: {result['headers'].get('Content-Type', 'N/A')}")
            
            if result['statusCode'] == 200:
                if 'text/html' in result['headers'].get('Content-Type', ''):
                    print(f"📝 HTML Length: {len(result['body'])} characters")
                    print("🎨 HTML content generated successfully")
                else:
                    print(f"📊 Response: {result['body'][:200]}...")
            else:
                print(f"❌ Error: {result['body']}")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print(f"\n✅ Lambda function testing completed!")

def save_html_for_preview():
    """Save HTML file for local preview"""
    
    print("💾 Saving HTML file for preview...")
    
    try:
        html_content = create_enhanced_control_panel()
        
        filename = 'q_business_enhanced_preview.html'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Saved: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Error saving HTML: {e}")
        return None

def main():
    """Main testing function"""
    
    print("🚀 Ailien Platform Q Business Enhanced - Local Testing")
    print("=" * 70)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Lambda function testing
    test_lambda_function()
    
    print("\n" + "=" * 70)
    
    # Test 2: Save HTML preview
    html_file = save_html_for_preview()
    
    print("\n" + "=" * 70)
    
    # Test 3: Start local server
    print("🌐 Starting Local Test Server...")
    server = LocalTestServer(port=8080)
    
    try:
        server_url = server.start_server()
        
        print(f"✅ Server started successfully!")
        print(f"🔗 Access your enhanced control panel at: {server_url}")
        print()
        print("🎯 Features to Test:")
        print("✅ Enhanced control panel layout")
        print("✅ Amazon Q Business side panel")
        print("✅ Natural language query interface")
        print("✅ Mock data product responses")
        print("✅ Responsive design")
        print("✅ Interactive elements")
        print()
        print("💡 Test Queries to Try:")
        print("• 'Which data products have the highest quality scores?'")
        print("• 'Show me trending data products this month'")
        print("• 'What data products can I access for sales analysis?'")
        print("• 'Which data products need attention?'")
        print()
        
        # Open browser automatically
        try:
            webbrowser.open(server_url)
            print("🌐 Opening browser automatically...")
        except:
            print("⚠️ Could not open browser automatically")
        
        print("Press Ctrl+C to stop the server...")
        
        # Keep server running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
        server.stop_server()
        print("✅ Local testing completed!")
        
    except Exception as e:
        print(f"❌ Server error: {e}")
        server.stop_server()

if __name__ == "__main__":
    main()