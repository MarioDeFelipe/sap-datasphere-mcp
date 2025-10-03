#!/usr/bin/env python3
"""
Test SAP HANA database connection for Datasphere
Using the database user credentials provided
"""
import json
import sys

# Database connection details
HANA_CONFIG = {
    "user": "GE230769#AWSUSER",
    "password": "D^1(52u37Y)hfMUZ+YC[5)Wq<eh_T@.n",
    "schema": "GE230769",
    "tags": ["hana"],
    "type": "procedure",
    "procedure_schema": "GE230769$TEC",
    "procedure": "HDI_GRANTOR_FOR_CUPS"
}

# Connection details
TENANT_ID = "f45fa9cc-f4b5-4126-ab73-b19b578fb17a"
BASE_URL = f"https://{TENANT_ID}.eu10.hcs.cloud.sap"

def check_hana_driver_availability():
    """Check if SAP HANA database drivers are available"""
    
    print("🔍 Checking SAP HANA driver availability...")
    
    drivers_to_check = [
        ("hdbcli", "SAP HANA Python Driver"),
        ("pyhdb", "Pure Python SAP HANA Client"),
        ("sqlalchemy", "SQLAlchemy (for HANA support)"),
        ("pyodbc", "ODBC Driver (alternative)")
    ]
    
    available_drivers = []
    
    for driver_name, description in drivers_to_check:
        try:
            __import__(driver_name)
            print(f"  ✅ {description} ({driver_name}) - Available")
            available_drivers.append(driver_name)
        except ImportError:
            print(f"  ❌ {description} ({driver_name}) - Not installed")
    
    return available_drivers

def install_hana_driver():
    """Provide instructions for installing SAP HANA driver"""
    
    print("\n📦 SAP HANA Driver Installation Guide")
    print("=" * 50)
    
    print("To connect to SAP HANA database, you need to install the SAP HANA client:")
    print()
    print("Option 1 - SAP HANA Python Driver (Recommended):")
    print("  pip install hdbcli")
    print()
    print("Option 2 - Pure Python Client:")
    print("  pip install pyhdb")
    print()
    print("Option 3 - ODBC Driver:")
    print("  pip install pyodbc")
    print("  (Requires SAP HANA ODBC driver to be installed separately)")
    
    return False

def test_hana_connection_with_hdbcli():
    """Test HANA connection using hdbcli driver"""
    
    try:
        from hdbcli import dbapi
        
        print("🔗 Testing HANA connection with hdbcli...")
        
        # Determine HANA connection details
        # For Datasphere, HANA is typically accessible via the same tenant URL
        # but on different ports or subdomains
        
        possible_hosts = [
            f"{TENANT_ID}.eu10.hcs.cloud.sap",
            f"hana-{TENANT_ID}.eu10.hcs.cloud.sap",
            f"{TENANT_ID}-hana.eu10.hcs.cloud.sap",
            f"db-{TENANT_ID}.eu10.hcs.cloud.sap"
        ]
        
        possible_ports = [443, 30015, 30013, 30041]  # Common HANA ports
        
        for host in possible_hosts:
            for port in possible_ports:
                try:
                    print(f"  Trying: {host}:{port}")
                    
                    connection = dbapi.connect(
                        address=host,
                        port=port,
                        user=HANA_CONFIG["user"],
                        password=HANA_CONFIG["password"],
                        encrypt=True,  # Use SSL
                        sslValidateCertificate=False  # For testing
                    )
                    
                    print(f"  ✅ Connected successfully!")
                    
                    # Test basic query
                    cursor = connection.cursor()
                    cursor.execute("SELECT CURRENT_SCHEMA FROM DUMMY")
                    result = cursor.fetchone()
                    
                    print(f"  📊 Current schema: {result[0] if result else 'Unknown'}")
                    
                    # Test access to user schema
                    cursor.execute(f"SELECT COUNT(*) FROM SYS.SCHEMAS WHERE SCHEMA_NAME = '{HANA_CONFIG['schema']}'")
                    schema_exists = cursor.fetchone()[0]
                    
                    if schema_exists:
                        print(f"  ✅ Schema '{HANA_CONFIG['schema']}' exists")
                        
                        # List tables in schema
                        cursor.execute(f"""
                            SELECT TABLE_NAME, TABLE_TYPE 
                            FROM SYS.TABLES 
                            WHERE SCHEMA_NAME = '{HANA_CONFIG['schema']}' 
                            ORDER BY TABLE_NAME
                        """)
                        
                        tables = cursor.fetchall()
                        print(f"  📋 Found {len(tables)} tables/views in schema")
                        
                        if tables:
                            print(f"  📄 Sample tables:")
                            for table_name, table_type in tables[:5]:
                                print(f"     • {table_name} ({table_type})")
                    else:
                        print(f"  ⚠️ Schema '{HANA_CONFIG['schema']}' not found")
                    
                    cursor.close()
                    connection.close()
                    
                    return {
                        'success': True,
                        'host': host,
                        'port': port,
                        'schema_exists': bool(schema_exists),
                        'table_count': len(tables) if 'tables' in locals() else 0
                    }
                    
                except Exception as e:
                    print(f"  ❌ Failed: {e}")
                    continue
        
        return {'success': False, 'error': 'No working connection found'}
        
    except ImportError:
        print("❌ hdbcli not available")
        return {'success': False, 'error': 'hdbcli not installed'}

def test_hana_connection_with_pyhdb():
    """Test HANA connection using pyhdb driver"""
    
    try:
        import pyhdb
        
        print("🔗 Testing HANA connection with pyhdb...")
        
        # Similar connection testing logic for pyhdb
        possible_hosts = [
            f"{TENANT_ID}.eu10.hcs.cloud.sap",
            f"hana-{TENANT_ID}.eu10.hcs.cloud.sap"
        ]
        
        for host in possible_hosts:
            try:
                print(f"  Trying: {host}:30015")
                
                connection = pyhdb.connect(
                    host=host,
                    port=30015,
                    user=HANA_CONFIG["user"],
                    password=HANA_CONFIG["password"]
                )
                
                print(f"  ✅ Connected successfully!")
                
                cursor = connection.cursor()
                cursor.execute("SELECT CURRENT_SCHEMA FROM DUMMY")
                result = cursor.fetchone()
                
                print(f"  📊 Current schema: {result[0] if result else 'Unknown'}")
                
                cursor.close()
                connection.close()
                
                return {'success': True, 'host': host, 'port': 30015}
                
            except Exception as e:
                print(f"  ❌ Failed: {e}")
                continue
        
        return {'success': False, 'error': 'No working connection found'}
        
    except ImportError:
        print("❌ pyhdb not available")
        return {'success': False, 'error': 'pyhdb not installed'}

def explore_hana_metadata():
    """Explore HANA database metadata and structure"""
    
    print("\n🔍 Exploring HANA Database Metadata...")
    print("=" * 50)
    
    # This would run after successful connection
    metadata_queries = [
        ("Schemas", "SELECT SCHEMA_NAME FROM SYS.SCHEMAS ORDER BY SCHEMA_NAME"),
        ("User Tables", f"SELECT TABLE_NAME FROM SYS.TABLES WHERE SCHEMA_NAME = '{HANA_CONFIG['schema']}' AND TABLE_TYPE = 'TABLE'"),
        ("Views", f"SELECT VIEW_NAME FROM SYS.VIEWS WHERE SCHEMA_NAME = '{HANA_CONFIG['schema']}'"),
        ("Procedures", f"SELECT PROCEDURE_NAME FROM SYS.PROCEDURES WHERE SCHEMA_NAME = '{HANA_CONFIG['schema']}'")
    ]
    
    print("Metadata queries to run after connection:")
    for name, query in metadata_queries:
        print(f"  📋 {name}:")
        print(f"     {query}")
    print()

def main():
    """Main function to test HANA database connection"""
    
    print("🚀 SAP HANA Database Connection Test")
    print("Testing Datasphere HANA database access")
    print("=" * 60)
    
    print(f"Database User: {HANA_CONFIG['user']}")
    print(f"Schema: {HANA_CONFIG['schema']}")
    print(f"Type: {HANA_CONFIG['type']}")
    print(f"Procedure Schema: {HANA_CONFIG['procedure_schema']}")
    print()
    
    # Step 1: Check driver availability
    available_drivers = check_hana_driver_availability()
    
    if not available_drivers:
        install_hana_driver()
        return
    
    # Step 2: Test connections with available drivers
    connection_results = {}
    
    if 'hdbcli' in available_drivers:
        connection_results['hdbcli'] = test_hana_connection_with_hdbcli()
    
    if 'pyhdb' in available_drivers:
        connection_results['pyhdb'] = test_hana_connection_with_pyhdb()
    
    # Step 3: Explore metadata
    explore_hana_metadata()
    
    # Step 4: Summary
    print("\n" + "=" * 60)
    print("HANA CONNECTION TEST SUMMARY")
    print("=" * 60)
    
    successful_connections = [driver for driver, result in connection_results.items() if result.get('success')]
    
    if successful_connections:
        print(f"🎉 SUCCESS! Connected using: {', '.join(successful_connections)}")
        
        for driver, result in connection_results.items():
            if result.get('success'):
                print(f"\n✅ {driver.upper()} Connection Details:")
                print(f"   Host: {result.get('host', 'Unknown')}")
                print(f"   Port: {result.get('port', 'Unknown')}")
                if 'schema_exists' in result:
                    print(f"   Schema exists: {result['schema_exists']}")
                if 'table_count' in result:
                    print(f"   Tables found: {result['table_count']}")
        
        print(f"\n🚀 NEXT STEPS:")
        print(f"1. 📊 Explore database schema and tables")
        print(f"2. 🔍 Query Datasphere data models")
        print(f"3. 🏗️ Build MCP server with HANA database access")
        print(f"4. 🔗 Integrate with Datasphere APIs (when OAuth2 is set up)")
        
    else:
        print(f"❌ No successful connections")
        print(f"\n🔧 TROUBLESHOOTING:")
        print(f"1. 🌐 Check network connectivity to HANA database")
        print(f"2. 🔐 Verify database user credentials")
        print(f"3. 🚪 Check if HANA ports are accessible")
        print(f"4. 📞 Contact SAP support for HANA connection details")
    
    # Save results
    with open('hana-connection-results.json', 'w') as f:
        json.dump({
            'config': HANA_CONFIG,
            'available_drivers': available_drivers,
            'connection_results': connection_results
        }, f, indent=2)
    
    print(f"\n📄 Results saved to: hana-connection-results.json")

if __name__ == "__main__":
    main()