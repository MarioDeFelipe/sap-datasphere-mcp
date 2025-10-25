#!/usr/bin/env python3
"""
Test the Datasphere Control Panel locally
"""

import uvicorn
import asyncio
from app import app, datasphere_client, glue_client

async def test_apis():
    """Test the API endpoints"""
    
    print("🧪 Testing Datasphere Control Panel APIs")
    print("=" * 50)
    
    try:
        # Test Datasphere connection
        print("📡 Testing Datasphere connection...")
        assets = await datasphere_client.get_catalog_assets()
        print(f"✅ Found {len(assets)} assets in Datasphere")
        
        # Test Glue connection
        print("🔧 Testing AWS Glue connection...")
        tables = await glue_client.get_glue_tables()
        print(f"✅ Found {len(tables)} tables in Glue")
        
        # Test data preview
        if assets:
            print("👁️ Testing data preview...")
            asset_name = assets[0].get('name')
            data = await datasphere_client.get_asset_data(asset_name, 3)
            if 'error' not in data:
                print(f"✅ Successfully previewed data from {asset_name}")
                print(f"   Records: {data.get('record_count', 0)}")
            else:
                print(f"⚠️ Data preview warning: {data['error']}")
        
        print("\n🎉 All API tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_local_server():
    """Run the FastAPI server locally"""
    
    print("🚀 Starting Datasphere Control Panel locally...")
    print("🌐 Open http://localhost:8000 in your browser")
    print("📊 API docs available at http://localhost:8000/docs")
    print("⏹️ Press Ctrl+C to stop")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run API tests
        asyncio.run(test_apis())
    else:
        # Run local server
        run_local_server()