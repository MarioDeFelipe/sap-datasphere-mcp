#!/usr/bin/env python3
"""
Guide to find OAuth credentials in SAP Datasphere portal
"""
import json

def create_oauth_navigation_guide():
    """Create a detailed guide for finding OAuth credentials in Datasphere"""
    
    guide = {
        "title": "How to Find OAuth Credentials in SAP Datasphere",
        "tenant_url": "https://your-tenant.eu10.hcs.cloud.sap",
        "navigation_paths": [
            {
                "method": "Primary Navigation",
                "steps": [
                    "1. Log into SAP Datasphere with admin credentials",
                    "2. Click on the 'System' menu (usually in top navigation or sidebar)",
                    "3. Navigate to 'Administration'",
                    "4. Look for 'App Integration' or 'Integration'", 
                    "5. Click on 'OAuth Clients' or 'OAuth2 Clients'"
                ],
                "expected_location": "System > Administration > App Integration > OAuth Clients"
            },
            {
                "method": "Alternative Navigation 1",
                "steps": [
                    "1. Look for a 'Settings' or 'Configuration' menu",
                    "2. Navigate to 'Security' or 'Authentication'",
                    "3. Find 'OAuth Clients' or 'API Access'"
                ],
                "expected_location": "Settings > Security > OAuth Clients"
            },
            {
                "method": "Alternative Navigation 2", 
                "steps": [
                    "1. Check the main menu for 'Space Management'",
                    "2. Look for 'System Configuration'",
                    "3. Find 'OAuth' or 'API Configuration'"
                ],
                "expected_location": "Space Management > System Configuration > OAuth"
            },
            {
                "method": "Search Method",
                "steps": [
                    "1. Use the search function in Datasphere (if available)",
                    "2. Search for terms like: 'OAuth', 'API', 'Client', 'Integration'",
                    "3. Look for results related to OAuth client management"
                ]
            }
        ],
        "what_to_look_for": {
            "page_titles": [
                "OAuth Clients",
                "OAuth2 Clients", 
                "API Clients",
                "App Integration",
                "Client Applications",
                "Authentication Clients"
            ],
            "buttons_or_links": [
                "Add OAuth Client",
                "Create Client",
                "New OAuth Client",
                "Manage Clients",
                "API Access"
            ]
        },
        "oauth_client_details": {
            "required_fields": [
                "Client ID",
                "Client Secret",
                "Authorization URL",
                "Token URL"
            ],
            "client_configuration": {
                "Purpose": "Technical User (for API access)",
                "Grant Type": "Client Credentials",
                "Scopes": ["API access", "Read", "Write"]
            }
        },
        "troubleshooting": {
            "if_not_found": [
                "Check if you have administrator privileges",
                "Look in user profile/account settings",
                "Check if OAuth clients are managed at tenant level",
                "Contact SAP support for navigation help"
            ],
            "permission_issues": [
                "Ensure you have 'System Administrator' role",
                "Check if 'API Access' permissions are assigned",
                "Verify tenant has API access enabled"
            ]
        }
    }
    
    return guide

def create_oauth_client_creation_guide():
    """Create a guide for creating new OAuth client if none exists"""
    
    creation_guide = {
        "title": "Creating New OAuth Client in SAP Datasphere",
        "prerequisites": [
            "Administrator access to SAP Datasphere tenant",
            "Permission to create OAuth clients",
            "Understanding of OAuth2 client credentials flow"
        ],
        "creation_steps": [
            {
                "step": 1,
                "title": "Access OAuth Client Management",
                "description": "Navigate to the OAuth clients section using the guide above"
            },
            {
                "step": 2,
                "title": "Create New Client",
                "description": "Click 'Add' or 'Create New OAuth Client'",
                "form_fields": {
                    "Name": "API Access Client (or similar descriptive name)",
                    "Description": "OAuth client for API access and MCP server integration",
                    "Purpose": "Technical User",
                    "Grant Type": "Client Credentials",
                    "Redirect URI": "Not required for client credentials flow"
                }
            },
            {
                "step": 3,
                "title": "Configure Permissions",
                "description": "Set appropriate scopes and permissions",
                "recommended_scopes": [
                    "API Access",
                    "Read Data",
                    "Write Data", 
                    "Manage Spaces",
                    "Access Catalog"
                ]
            },
            {
                "step": 4,
                "title": "Generate Credentials",
                "description": "Save the generated credentials",
                "important_note": "Client Secret is only shown once - save it immediately!"
            }
        ],
        "expected_output": {
            "client_id": "Usually starts with 'sb-' followed by UUID",
            "client_secret": "Long random string - save this securely",
            "authorization_url": "https://{tenant}.eu10.hcs.cloud.sap/oauth/authorize",
            "token_url": "https://{tenant}.eu10.hcs.cloud.sap/oauth/token"
        }
    }
    
    return creation_guide

def print_navigation_guide():
    """Print the navigation guide in a readable format"""
    
    guide = create_oauth_navigation_guide()
    
    print("🔍 HOW TO FIND OAUTH CREDENTIALS IN SAP DATASPHERE")
    print("=" * 60)
    
    print(f"\n🌐 Tenant URL: {guide['tenant_url']}")
    
    print(f"\n📍 NAVIGATION METHODS:")
    for i, method in enumerate(guide['navigation_paths'], 1):
        print(f"\n{i}. {method['method']}:")
        for step in method['steps']:
            print(f"   {step}")
        if 'expected_location' in method:
            print(f"   📂 Expected location: {method['expected_location']}")
    
    print(f"\n👀 WHAT TO LOOK FOR:")
    print(f"\nPage Titles:")
    for title in guide['what_to_look_for']['page_titles']:
        print(f"   • {title}")
    
    print(f"\nButtons/Links:")
    for button in guide['what_to_look_for']['buttons_or_links']:
        print(f"   • {button}")
    
    print(f"\n🔧 TROUBLESHOOTING:")
    print(f"\nIf OAuth section not found:")
    for tip in guide['troubleshooting']['if_not_found']:
        print(f"   • {tip}")
    
    print(f"\nPermission issues:")
    for tip in guide['troubleshooting']['permission_issues']:
        print(f"   • {tip}")

def print_creation_guide():
    """Print the OAuth client creation guide"""
    
    creation_guide = create_oauth_client_creation_guide()
    
    print(f"\n" + "=" * 60)
    print("CREATING NEW OAUTH CLIENT")
    print("=" * 60)
    
    print(f"\n📋 Prerequisites:")
    for prereq in creation_guide['prerequisites']:
        print(f"   • {prereq}")
    
    print(f"\n🚀 Creation Steps:")
    for step_info in creation_guide['creation_steps']:
        print(f"\n{step_info['step']}. {step_info['title']}")
        print(f"   {step_info['description']}")
        
        if 'form_fields' in step_info:
            print(f"   Form fields to fill:")
            for field, value in step_info['form_fields'].items():
                print(f"     • {field}: {value}")
        
        if 'recommended_scopes' in step_info:
            print(f"   Recommended scopes:")
            for scope in step_info['recommended_scopes']:
                print(f"     • {scope}")
    
    print(f"\n📄 Expected Output:")
    for field, description in creation_guide['expected_output'].items():
        print(f"   • {field}: {description}")

def save_guides_to_files():
    """Save the guides to JSON files for reference"""
    
    nav_guide = create_oauth_navigation_guide()
    creation_guide = create_oauth_client_creation_guide()
    
    with open('oauth-navigation-guide.json', 'w') as f:
        json.dump(nav_guide, f, indent=2)
    
    with open('oauth-creation-guide.json', 'w') as f:
        json.dump(creation_guide, f, indent=2)
    
    print(f"\n📄 Guides saved to:")
    print(f"   • oauth-navigation-guide.json")
    print(f"   • oauth-creation-guide.json")

def main():
    """Main function to display OAuth credential finding guide"""
    
    print_navigation_guide()
    print_creation_guide()
    save_guides_to_files()
    
    print(f"\n" + "=" * 60)
    print("QUICK ACTION ITEMS")
    print("=" * 60)
    
    print(f"\n1. 🌐 Log into Datasphere:")
    print(f"   https://your-tenant.eu10.hcs.cloud.sap")
    
    print(f"\n2. 🔍 Navigate to OAuth clients using one of the methods above")
    
    print(f"\n3. 📋 Check if any OAuth clients already exist")
    
    print(f"\n4. 🆕 If none exist, create a new OAuth client with:")
    print(f"   • Purpose: Technical User")
    print(f"   • Grant Type: Client Credentials")
    print(f"   • Scopes: API Access")
    
    print(f"\n5. 💾 Save the Client ID and Client Secret")
    
    print(f"\n6. 🧪 Update the OAuth configuration in our connection script")
    
    print(f"\n7. ✅ Test the API connection")

if __name__ == "__main__":
    main()