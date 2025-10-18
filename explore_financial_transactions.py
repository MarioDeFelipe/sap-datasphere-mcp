#!/usr/bin/env python3
"""
Explore SAP Financial Transactions Model
Explore the SAP_SC_FI_AM_FINTRANSACTIONS analytical model in Wolf environment
"""

import requests
import base64
import json
import xml.etree.ElementTree as ET
from datetime import datetime

class FinancialTransactionsExplorer:
    """Explorer for SAP Financial Transactions analytical model"""
    
    def __init__(self):
        self.config = {
            "base_url": "https://ailien-test.eu20.hcs.cloud.sap",
            "oauth_client_id": "sb-60cb266e-ad9d-49f7-9967-b53b8286a259!b130936|client!b3944",
            "oauth_client_secret": "caaea1b9-b09b-4d28-83fe-09966d525243$LOFW4h5LpLvB3Z2FE0P7FiH4-C7qexeQPi22DBiHbz8=",
            "token_url": "https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/token"
        }
        
        # Financial Transactions model endpoints
        self.model_name = "SAP_SC_FI_AM_FINTRANSACTIONS"
        self.base_endpoint = f"/api/v1/datasphere/consumption/analytical/SAP_CONTENT/{self.model_name}"
        
        self.endpoints = {
            "service": self.base_endpoint,
            "data": f"{self.base_endpoint}/{self.model_name}",
            "metadata": f"{self.base_endpoint}/$metadata"
        }
        
        self.access_token = None
        self.get_access_token()
    
    def get_access_token(self):
        """Get OAuth access token"""
        
        client_id = self.config["oauth_client_id"]
        client_secret = self.config["oauth_client_secret"]
        token_url = self.config["token_url"]
        
        auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        
        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {'grant_type': 'client_credentials'}
        
        response = requests.post(token_url, headers=headers, data=data, timeout=30)
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            print(f"✅ OAuth token obtained for Financial Transactions exploration")
        else:
            raise Exception(f"OAuth failed: HTTP {response.status_code}")
    
    def make_request(self, endpoint, params=None, accept_header='application/json'):
        """Make authenticated request"""
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': accept_header,
            'User-Agent': 'Financial-Transactions-Explorer/1.0'
        }
        
        url = f"{self.config['base_url']}{endpoint}"
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content": response.content,
            "text": response.text,
            "json": response.json() if response.status_code == 200 and 'json' in response.headers.get('content-type', '') else None
        }
    
    def explore_service_info(self):
        """Explore the service information"""
        
        print(f"📊 Exploring Financial Transactions Service")
        print("=" * 42)
        
        result = self.make_request(self.endpoints["service"])
        
        if result["status_code"] == 200:
            print(f"✅ Service endpoint accessible")
            
            if result["json"]:
                data = result["json"]
                
                print(f"🔗 OData Context: {data.get('@odata.context', 'N/A')}")
                print(f"📋 Metadata ETag: {data.get('@odata.metadataEtag', 'N/A')}")
                
                if 'value' in data:
                    entities = data['value']
                    print(f"📊 Available entities: {len(entities)}")
                    
                    for entity in entities:
                        name = entity.get('name', 'Unknown')
                        url = entity.get('url', 'N/A')
                        print(f"  • {name}: {url}")
                
                return data
            else:
                print(f"📄 Non-JSON response received")
                print(f"Content preview: {result['text'][:200]}...")
        
        else:
            print(f"❌ Service endpoint failed: HTTP {result['status_code']}")
            print(f"Error: {result['text'][:200]}")
        
        return None
    
    def explore_data_sample(self, limit=5):
        """Explore sample data from the model"""
        
        print(f"\n📊 Exploring Financial Transactions Data (Sample)")
        print("=" * 48)
        
        params = {'$top': limit}
        result = self.make_request(self.endpoints["data"], params=params)
        
        if result["status_code"] == 200:
            print(f"✅ Data endpoint accessible")
            
            if result["json"]:
                data = result["json"]
                
                print(f"🔗 OData Context: {data.get('@odata.context', 'N/A')}")
                
                if 'value' in data:
                    records = data['value']
                    print(f"📊 Sample records retrieved: {len(records)}")
                    
                    if records:
                        # Analyze first record structure
                        sample_record = records[0]
                        print(f"\n📋 Record Structure ({len(sample_record)} fields):")
                        
                        for field_name, field_value in sample_record.items():
                            field_type = type(field_value).__name__
                            value_preview = str(field_value)[:50] if field_value is not None else "null"
                            print(f"  • {field_name}: {field_type} = {value_preview}")
                        
                        # Show all records
                        print(f"\n📊 Sample Financial Transaction Records:")
                        for i, record in enumerate(records, 1):
                            print(f"\n  Record {i}:")
                            # Show key fields that are likely to be interesting
                            key_fields = ['TransactionID', 'Amount', 'Currency', 'Date', 'Account', 'Description', 'CompanyCode']
                            
                            for field in key_fields:
                                if field in record:
                                    print(f"    {field}: {record[field]}")
                            
                            # Show first few fields if key fields not found
                            if not any(field in record for field in key_fields):
                                for field_name, field_value in list(record.items())[:5]:
                                    print(f"    {field_name}: {field_value}")
                
                return data
            else:
                print(f"📄 Non-JSON response received")
                print(f"Content preview: {result['text'][:200]}...")
        
        else:
            print(f"❌ Data endpoint failed: HTTP {result['status_code']}")
            print(f"Error: {result['text'][:200]}")
        
        return None
    
    def explore_metadata(self):
        """Explore the metadata/schema"""
        
        print(f"\n📋 Exploring Financial Transactions Metadata")
        print("=" * 44)
        
        # Try XML metadata first
        result = self.make_request(self.endpoints["metadata"], accept_header='application/xml')
        
        if result["status_code"] == 200:
            content_type = result["headers"].get('content-type', '').lower()
            
            if 'xml' in content_type:
                print(f"✅ XML metadata retrieved")
                print(f"📄 Content size: {len(result['content'])} bytes")
                
                try:
                    # Parse XML metadata
                    root = ET.fromstring(result["text"])
                    
                    # Define namespaces
                    namespaces = {
                        'edmx': 'http://docs.oasis-open.org/odata/ns/edmx',
                        'edm': 'http://docs.oasis-open.org/odata/ns/edm'
                    }
                    
                    # Find EntityType elements
                    entity_types = root.findall('.//edm:EntityType', namespaces)
                    print(f"📊 Entity types found: {len(entity_types)}")
                    
                    for entity_type in entity_types:
                        entity_name = entity_type.get('Name', 'Unknown')
                        print(f"\n🏗️ Entity: {entity_name}")
                        
                        # Find properties
                        properties = entity_type.findall('edm:Property', namespaces)
                        print(f"   Properties: {len(properties)}")
                        
                        for prop in properties[:10]:  # Show first 10 properties
                            prop_name = prop.get('Name', 'Unknown')
                            prop_type = prop.get('Type', 'Unknown')
                            nullable = prop.get('Nullable', 'true')
                            max_length = prop.get('MaxLength', '')
                            
                            type_info = prop_type
                            if max_length:
                                type_info += f"({max_length})"
                            if nullable.lower() == 'false':
                                type_info += " NOT NULL"
                            
                            print(f"     • {prop_name}: {type_info}")
                        
                        if len(properties) > 10:
                            print(f"     ... and {len(properties) - 10} more properties")
                
                except ET.ParseError as e:
                    print(f"❌ XML parsing failed: {e}")
                    print(f"📄 Raw content preview: {result['text'][:500]}...")
            
            else:
                print(f"✅ Metadata retrieved (format: {content_type})")
                print(f"📄 Content preview: {result['text'][:300]}...")
        
        else:
            print(f"❌ Metadata endpoint failed: HTTP {result['status_code']}")
            print(f"Error: {result['text'][:200]}")
        
        return result if result["status_code"] == 200 else None
    
    def test_odata_queries(self):
        """Test various OData query capabilities"""
        
        print(f"\n🔍 Testing OData Query Capabilities")
        print("=" * 35)
        
        # Test different OData query parameters
        test_queries = [
            ({'$top': 3}, "Limit to 3 records"),
            ({'$top': 1, '$select': '*'}, "Select all fields, limit 1"),
            ({'$count': 'true'}, "Include count"),
            ({'$orderby': 'CreatedDate desc'}, "Order by date (if exists)"),
            ({'$filter': "Amount gt 1000"}, "Filter by amount (if exists)"),
        ]
        
        successful_queries = []
        
        for params, description in test_queries:
            print(f"\n🔍 Testing: {description}")
            print(f"   Parameters: {params}")
            
            result = self.make_request(self.endpoints["data"], params=params)
            
            if result["status_code"] == 200:
                print(f"✅ Query successful")
                
                if result["json"]:
                    data = result["json"]
                    
                    if 'value' in data:
                        record_count = len(data['value'])
                        print(f"   📊 Records returned: {record_count}")
                    
                    if '@odata.count' in data:
                        total_count = data['@odata.count']
                        print(f"   📈 Total count: {total_count}")
                
                successful_queries.append((params, description))
            
            else:
                print(f"❌ Query failed: HTTP {result['status_code']}")
        
        print(f"\n📊 Query Test Summary:")
        print(f"✅ Successful queries: {len(successful_queries)}")
        
        return successful_queries
    
    def generate_metadata_extraction_config(self):
        """Generate configuration for metadata extraction"""
        
        print(f"\n🔧 Generating Metadata Extraction Configuration")
        print("=" * 48)
        
        config = {
            "model_name": self.model_name,
            "model_type": "Financial Transactions (SAP Smart Controls)",
            "base_url": self.config["base_url"],
            "endpoints": self.endpoints,
            "extraction_ready": True,
            "recommended_queries": [
                {"params": {"$top": 100}, "purpose": "Sample data extraction"},
                {"params": {"$count": "true"}, "purpose": "Get total record count"},
                {"params": {"$top": 1, "$select": "*"}, "purpose": "Schema discovery"}
            ],
            "aws_glue_table_name": "sap_financial_transactions",
            "aws_glue_database": "datasphere_wolf_staging"
        }
        
        # Save configuration
        config_file = f'financial_transactions_config_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Configuration saved to: {config_file}")
        print(f"🚀 Ready for metadata extraction to AWS Glue!")
        
        return config

def main():
    """Main exploration function"""
    
    print("💰 SAP Financial Transactions Model Explorer")
    print("=" * 45)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    try:
        explorer = FinancialTransactionsExplorer()
        
        # 1. Explore service information
        service_info = explorer.explore_service_info()
        
        # 2. Explore sample data
        sample_data = explorer.explore_data_sample(limit=3)
        
        # 3. Explore metadata/schema
        metadata_info = explorer.explore_metadata()
        
        # 4. Test OData queries
        successful_queries = explorer.test_odata_queries()
        
        # 5. Generate extraction configuration
        extraction_config = explorer.generate_metadata_extraction_config()
        
        # Summary
        print(f"\n🎉 Financial Transactions Exploration Complete!")
        print("=" * 47)
        print(f"✅ Service accessible: {service_info is not None}")
        print(f"✅ Data accessible: {sample_data is not None}")
        print(f"✅ Metadata accessible: {metadata_info is not None}")
        print(f"✅ OData queries working: {len(successful_queries)}")
        
        print(f"\n💡 Next Steps:")
        print("1. Use this model for metadata extraction")
        print("2. Replicate schema to AWS Glue")
        print("3. Set up data pipeline for financial transactions")
        print("4. Build analytics on top of the replicated data")
        
    except Exception as e:
        print(f"❌ Exploration failed: {e}")

if __name__ == "__main__":
    main()