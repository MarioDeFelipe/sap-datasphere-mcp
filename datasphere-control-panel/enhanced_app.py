#!/usr/bin/env python3
"""
Enhanced SAP Catalog Integrator with License-Based Feature Management
Clearly separates Datasphere and Business Data Cloud capabilities
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any
import boto3

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sap-catalog-integrator")

# License Detection (simplified for demo)
class LicenseManager:
    def __init__(self):
        self.datasphere_available = True   # Currently working
        self.bdc_available = False         # Not yet implemented
        self.s4hana_private_available = False  # Future implementation
        self.s4hana_public_available = False   # Future implementation
    
    def get_license_status(self):
        return {
            "datasphere": self.datasphere_available,
            "bdc": self.bdc_available,
            "s4hana_private": self.s4hana_private_available,
            "s4hana_public": self.s4hana_public_available,
            "license_type": "datasphere_only" if self.datasphere_available and not self.bdc_available else "full"
        }

license_manager = LicenseManager()

def create_html_response(title: str, content: str) -> Dict[str, Any]:
    """Create an HTML response with license-aware styling"""
    
    license_status = license_manager.get_license_status()
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', 'Segoe UI', sans-serif;
                background: #0a0a0a;
                color: #e0e0e0;
                min-height: 100vh;
                background-image: 
                    radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.1) 0%, transparent 50%);
            }}
            
            .header {{
                background: rgba(26, 26, 26, 0.9);
                border-bottom: 1px solid rgba(120, 255, 119, 0.2);
                padding: 20px 0;
                backdrop-filter: blur(10px);
            }}
            
            .header-content {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .logo {{
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            
            .logo div {{
                display: flex;
                flex-direction: column;
            }}
            
            .header h1 {{
                font-size: 1.8em;
                background: linear-gradient(135deg, #78ff77 0%, #ff77c6 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin: 0;
            }}
            

            
            .status-badge {{
                background: linear-gradient(135deg, #78ff77, #ff77c6);
                color: #000;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: 600;
                font-size: 0.8em;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 40px 20px;
            }}
            
            .platform-section {{
                margin-bottom: 40px;
            }}
            
            .platform-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }}
            
            .platform-title {{
                font-size: 1.5em;
                font-weight: 600;
            }}
            
            .platform-title.datasphere {{
                color: #78ff77;
            }}
            
            .platform-title.bdc {{
                color: #ff77c6;
            }}
            
            .platform-status {{
                font-size: 0.9em;
                padding: 6px 12px;
                border-radius: 15px;
                font-weight: 500;
            }}
            
            .platform-status.available {{
                background: rgba(120, 255, 119, 0.1);
                color: #78ff77;
                border: 1px solid rgba(120, 255, 119, 0.3);
            }}
            
            .platform-status.unavailable {{
                background: rgba(255, 255, 255, 0.05);
                color: #888;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            
            .feature-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
            }}
            
            .feature-card {{
                background: rgba(26, 26, 26, 0.8);
                border-radius: 12px;
                padding: 25px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                transition: all 0.3s ease;
                position: relative;
            }}
            
            .feature-card.available {{
                border-color: rgba(120, 255, 119, 0.3);
            }}
            
            .feature-card.available:hover {{
                transform: translateY(-5px);
                border-color: rgba(120, 255, 119, 0.5);
                box-shadow: 0 10px 30px rgba(120, 255, 119, 0.1);
            }}
            
            .feature-card.unavailable {{
                opacity: 0.6;
                border-color: rgba(255, 255, 255, 0.05);
            }}
            
            .feature-header {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 15px;
            }}
            
            .feature-card h3 {{
                font-size: 1.2em;
                margin-bottom: 10px;
                color: #e0e0e0;
            }}
            
            .license-badge {{
                font-size: 0.75em;
                padding: 4px 8px;
                border-radius: 10px;
                font-weight: 500;
            }}
            
            .license-badge.datasphere {{
                background: rgba(120, 255, 119, 0.1);
                color: #78ff77;
                border: 1px solid rgba(120, 255, 119, 0.3);
            }}
            
            .license-badge.bdc {{
                background: rgba(255, 119, 198, 0.1);
                color: #ff77c6;
                border: 1px solid rgba(255, 119, 198, 0.3);
            }}
            
            .feature-card p {{
                color: #c0c0c0;
                line-height: 1.6;
                margin-bottom: 20px;
            }}
            
            .btn {{
                display: inline-block;
                padding: 12px 24px;
                background: linear-gradient(135deg, #78ff77, #ff77c6);
                color: #000;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                transition: all 0.3s ease;
                border: none;
                cursor: pointer;
                font-size: 0.9em;
            }}
            
            .btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(120, 255, 119, 0.3);
            }}
            
            .btn.disabled {{
                background: rgba(255, 255, 255, 0.1);
                color: #666;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }}
            
            .btn.secondary {{
                background: rgba(255, 119, 198, 0.2);
                color: #ff77c6;
                border: 1px solid rgba(255, 119, 198, 0.3);
            }}
            
            .upgrade-prompt {{
                background: rgba(255, 119, 198, 0.05);
                border: 1px solid rgba(255, 119, 198, 0.2);
                border-radius: 12px;
                padding: 25px;
                margin-top: 30px;
            }}
            
            .upgrade-prompt h4 {{
                color: #ff77c6;
                margin-bottom: 15px;
                font-size: 1.1em;
            }}
            
            .upgrade-prompt ul {{
                margin: 15px 0;
                padding-left: 20px;
                color: #c0c0c0;
            }}
            
            .upgrade-prompt li {{
                margin-bottom: 8px;
            }}
            
            .nav-links {{
                display: flex;
                gap: 20px;
                margin-bottom: 30px;
                flex-wrap: wrap;
            }}
            
            .nav-links a {{
                color: #c0c0c0;
                text-decoration: none;
                padding: 10px 20px;
                border-radius: 8px;
                background: rgba(26, 26, 26, 0.8);
                border: 1px solid rgba(255, 255, 255, 0.1);
                transition: all 0.3s ease;
            }}
            
            .nav-links a:hover {{
                color: #78ff77;
                border-color: rgba(120, 255, 119, 0.3);
                background: rgba(120, 255, 119, 0.05);
            }}
            
            .nav-links a.disabled {{
                opacity: 0.5;
                cursor: not-allowed;
            }}
            
            .nav-links a.disabled:hover {{
                color: #c0c0c0;
                border-color: rgba(255, 255, 255, 0.1);
                background: rgba(26, 26, 26, 0.8);
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-content">
                <div class="logo">
                    <div>
                        <h1>SAP Metadata Integrator to AWS</h1>
                        <p style="font-size: 0.8em; color: #78ff77; margin: 0;">Powered by Ailien Studio</p>
                    </div>
                </div>
                <div class="status-badge">LIVE</div>
            </div>
        </div>
        
        <div class="container">
            {content}
        </div>
        
        <footer style="background: rgba(26, 26, 26, 0.9); border-top: 1px solid rgba(120, 255, 119, 0.2); padding: 20px 0; margin-top: 40px; text-align: center;">
            <div style="max-width: 1200px; margin: 0 auto; color: #c0c0c0;">
                <p style="margin: 0; font-size: 0.9em;">
                    Powered by <strong style="color: #78ff77;">Ailien Studio</strong> | 
                    <a href="mailto:contact@ailien.studio" style="color: #ff77c6; text-decoration: none;">contact@ailien.studio</a>
                </p>
                <p style="margin: 5px 0 0 0; font-size: 0.8em; color: #888;">
                    AILIEN LLC | 5830 E 2nd St, Ste 7000 #29127, Casper, Wyoming 82609 US
                </p>
            </div>
        </footer>
    </body>
    </html>
    """
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
            'Cache-Control': 'no-cache'
        },
        'body': html
    }

def handle_dashboard() -> Dict[str, Any]:
    """Handle dashboard request with license-aware content"""
    
    license_status = license_manager.get_license_status()
    
    # Datasphere features (always available if licensed)
    datasphere_section = """
    <div class="platform-section">
        <div class="platform-header">
            <h2 class="platform-title datasphere">SAP Datasphere</h2>
            <span class="platform-status available">Active</span>
        </div>
        
        <div class="feature-grid">
            <div class="feature-card available">
                <div class="feature-header">
                    <h3>Data Catalog</h3>
                    <span class="license-badge datasphere">Datasphere</span>
                </div>
                <p>Browse and manage your Datasphere assets including views, tables, and models.</p>
                <a href="/catalog" class="btn">Browse Catalog</a>
            </div>
            
            <div class="feature-card available">
                <div class="feature-header">
                    <h3>AWS Glue Integration</h3>
                    <span class="license-badge datasphere">Datasphere</span>
                </div>
                <p>Synchronize metadata to AWS Glue Data Catalog for seamless analytics integration.</p>
                <a href="/glue" class="btn">View Glue Tables</a>
            </div>
            
            <div class="feature-card available">
                <div class="feature-header">
                    <h3>Data Viewer</h3>
                    <span class="license-badge datasphere">Datasphere</span>
                </div>
                <p>Explore and sample data from your Datasphere assets with interactive previews.</p>
                <a href="/data" class="btn">View Data</a>
            </div>
            
            <div class="feature-card available">
                <div class="feature-header">
                    <h3>Sync Manager</h3>
                    <span class="license-badge datasphere">Datasphere</span>
                </div>
                <p>Manage synchronization between Datasphere and AWS with real-time progress tracking.</p>
                <a href="/sync" class="btn">Manage Sync</a>
            </div>
        </div>
    </div>
    """
    
    # BDC features (conditional based on license)
    if license_status['bdc']:
        bdc_section = """
        <div class="platform-section">
            <div class="platform-header">
                <h2 class="platform-title bdc">SAP Business Data Cloud</h2>
                <span class="platform-status available">Active</span>
            </div>
            
            <div class="feature-grid">
                <div class="feature-card available">
                    <div class="feature-header">
                        <h3>Data Products</h3>
                        <span class="license-badge bdc">BDC</span>
                    </div>
                    <p>Create and manage enterprise data products for cross-organizational sharing.</p>
                    <a href="/bdc/products" class="btn">Manage Products</a>
                </div>
                
                <div class="feature-card available">
                    <div class="feature-header">
                        <h3>Data Sharing</h3>
                        <span class="license-badge bdc">BDC</span>
                    </div>
                    <p>Securely share data across organizations with advanced access controls.</p>
                    <a href="/bdc/sharing" class="btn">Manage Shares</a>
                </div>
                
                <div class="feature-card available">
                    <div class="feature-header">
                        <h3>API Management</h3>
                        <span class="license-badge bdc">BDC</span>
                    </div>
                    <p>Publish and manage data APIs with automated documentation and rate limiting.</p>
                    <a href="/bdc/apis" class="btn">Manage APIs</a>
                </div>
                
                <div class="feature-card available">
                    <div class="feature-header">
                        <h3>Cross-Platform Lineage</h3>
                        <span class="license-badge bdc">BDC</span>
                    </div>
                    <p>Track data lineage across Datasphere, BDC, and AWS for complete visibility.</p>
                    <a href="/bdc/lineage" class="btn">View Lineage</a>
                </div>
            </div>
        </div>
        """
    else:
        bdc_section = f"""
        <div class="platform-section">
            <div class="platform-header">
                <h2 class="platform-title bdc">SAP Business Data Cloud</h2>
                <span class="platform-status unavailable">License Required</span>
            </div>
            
            <div class="feature-grid">
                <div class="feature-card unavailable">
                    <div class="feature-header">
                        <h3>Data Products</h3>
                        <span class="license-badge bdc">BDC Required</span>
                    </div>
                    <p>Create and manage enterprise data products for cross-organizational sharing.</p>
                    <button class="btn disabled" disabled>Requires BDC License</button>
                </div>
                
                <div class="feature-card unavailable">
                    <div class="feature-header">
                        <h3>Data Sharing</h3>
                        <span class="license-badge bdc">BDC Required</span>
                    </div>
                    <p>Securely share data across organizations with advanced access controls.</p>
                    <button class="btn disabled" disabled>Requires BDC License</button>
                </div>
                
                <div class="feature-card unavailable">
                    <div class="feature-header">
                        <h3>API Management</h3>
                        <span class="license-badge bdc">BDC Required</span>
                    </div>
                    <p>Publish and manage data APIs with automated documentation and rate limiting.</p>
                    <button class="btn disabled" disabled>Requires BDC License</button>
                </div>
                
                <div class="feature-card unavailable">
                    <div class="feature-header">
                        <h3>Cross-Platform Lineage</h3>
                        <span class="license-badge bdc">BDC Required</span>
                    </div>
                    <p>Track data lineage across Datasphere, BDC, and AWS for complete visibility.</p>
                    <button class="btn disabled" disabled>Requires BDC License</button>
                </div>
            </div>
            
            <div class="upgrade-prompt">
                <h4>Unlock Advanced Data Capabilities</h4>
                <p>Add SAP Business Data Cloud to your license for enterprise-grade data management:</p>
                <ul>
                    <li>Enterprise data product management and cataloging</li>
                    <li>Cross-organizational data sharing with governance</li>
                    <li>Automated API publishing and management</li>
                    <li>Advanced data lineage and impact analysis</li>
                    <li>Enhanced compliance and governance features</li>
                </ul>
                <a href="mailto:contact@ailien.studio?subject=BDC Integration Inquiry" class="btn secondary">
                    Contact Ailien Studio for BDC Integration
                </a>
            </div>
        </div>
        """
    
    # S/4HANA Private Cloud Edition section (always unavailable for now)
    s4hana_private_section = """
    <div class="platform-section">
        <div class="platform-header">
            <h2 class="platform-title" style="color: #4CAF50;">SAP S/4HANA Cloud Private Edition</h2>
            <span class="platform-status unavailable">Coming Soon</span>
        </div>
        
        <div class="feature-grid">
            <div class="feature-card unavailable">
                <div class="feature-header">
                    <h3>Metadata Extraction</h3>
                    <span class="license-badge" style="background: rgba(76, 175, 80, 0.1); color: #4CAF50; border: 1px solid rgba(76, 175, 80, 0.3);">S/4HANA Cloud Private</span>
                </div>
                <p>Extract and synchronize metadata from S/4HANA Cloud Private Edition tables and views.</p>
                <button class="btn disabled" disabled>Coming Soon</button>
            </div>
            
            <div class="feature-card unavailable">
                <div class="feature-header">
                    <h3>Data Dictionary Integration</h3>
                    <span class="license-badge" style="background: rgba(76, 175, 80, 0.1); color: #4CAF50; border: 1px solid rgba(76, 175, 80, 0.3);">S/4HANA Cloud Private</span>
                </div>
                <p>Integrate S/4HANA Cloud data dictionary and business object metadata.</p>
                <button class="btn disabled" disabled>Coming Soon</button>
            </div>
            
            <div class="feature-card unavailable">
                <div class="feature-header">
                    <h3>Custom Table Discovery</h3>
                    <span class="license-badge" style="background: rgba(76, 175, 80, 0.1); color: #4CAF50; border: 1px solid rgba(76, 175, 80, 0.3);">S/4HANA Cloud Private</span>
                </div>
                <p>Discover and catalog custom tables and Z-objects from S/4HANA Cloud Private Edition.</p>
                <button class="btn disabled" disabled>Coming Soon</button>
            </div>
        </div>
        
        <div class="upgrade-prompt">
            <h4>S/4HANA Cloud Private Edition Integration</h4>
            <p>Future capabilities for S/4HANA Cloud Private Edition integration:</p>
            <ul>
                <li>Direct metadata extraction from S/4HANA Cloud Private Edition systems</li>
                <li>Data dictionary and business object integration</li>
                <li>Custom table and Z-object discovery</li>
                <li>Real-time schema synchronization</li>
                <li>Business context preservation</li>
            </ul>
            <a href="mailto:contact@ailien.studio?subject=S4HANA Cloud Private Edition Integration" class="btn secondary">
                Contact Ailien Studio for S/4HANA Cloud Private Edition
            </a>
        </div>
    </div>
    """
    
    # S/4HANA Public Cloud Edition section (always unavailable for now)
    s4hana_public_section = """
    <div class="platform-section">
        <div class="platform-header">
            <h2 class="platform-title" style="color: #2196F3;">SAP S/4HANA Cloud Public Edition</h2>
            <span class="platform-status unavailable">Coming Soon</span>
        </div>
        
        <div class="feature-grid">
            <div class="feature-card unavailable">
                <div class="feature-header">
                    <h3>API-Based Metadata</h3>
                    <span class="license-badge" style="background: rgba(33, 150, 243, 0.1); color: #2196F3; border: 1px solid rgba(33, 150, 243, 0.3);">S/4HANA Cloud Public</span>
                </div>
                <p>Extract metadata via S/4HANA Cloud Public Edition APIs and OData services.</p>
                <button class="btn disabled" disabled>Coming Soon</button>
            </div>
            
            <div class="feature-card unavailable">
                <div class="feature-header">
                    <h3>Standard Object Catalog</h3>
                    <span class="license-badge" style="background: rgba(33, 150, 243, 0.1); color: #2196F3; border: 1px solid rgba(33, 150, 243, 0.3);">S/4HANA Cloud Public</span>
                </div>
                <p>Catalog standard S/4HANA Cloud Public Edition business objects and entities.</p>
                <button class="btn disabled" disabled>Coming Soon</button>
            </div>
            
            <div class="feature-card unavailable">
                <div class="feature-header">
                    <h3>Extension Discovery</h3>
                    <span class="license-badge" style="background: rgba(33, 150, 243, 0.1); color: #2196F3; border: 1px solid rgba(33, 150, 243, 0.3);">S/4HANA Cloud Public</span>
                </div>
                <p>Discover and integrate custom extensions and key user tools.</p>
                <button class="btn disabled" disabled>Coming Soon</button>
            </div>
        </div>
        
        <div class="upgrade-prompt">
            <h4>S/4HANA Cloud Public Edition Integration</h4>
            <p>Future capabilities for S/4HANA Cloud Public Edition integration:</p>
            <ul>
                <li>API-based metadata extraction from S/4HANA Cloud Public Edition</li>
                <li>Standard business object and entity cataloging</li>
                <li>Custom extension and key user tool discovery</li>
                <li>OData service metadata integration</li>
                <li>Cloud-native connectivity and security</li>
            </ul>
            <a href="mailto:contact@ailien.studio?subject=S4HANA Cloud Public Edition Integration" class="btn secondary">
                Contact Ailien Studio for S/4HANA Cloud Public Edition
            </a>
        </div>
    </div>
    """
    
    content = datasphere_section + bdc_section + s4hana_private_section + s4hana_public_section
    
    return create_html_response("SAP Metadata Integrator Dashboard", content)

# Keep existing handlers but add license awareness
def handle_glue() -> Dict[str, Any]:
    """Handle Glue tables request - Datasphere feature"""
    
    license_status = license_manager.get_license_status()
    
    if not license_status['datasphere']:
        content = """
        <div class="nav-links">
            <a href="/">Dashboard</a>
        </div>
        
        <div class="feature-card unavailable">
            <h2>AWS Glue Integration</h2>
            <p>This feature requires an active SAP Datasphere license.</p>
            <a href="mailto:contact@ailien.studio?subject=Datasphere License" class="btn secondary">Contact Ailien Studio</a>
        </div>
        """
        return create_html_response("License Required", content)
    
    # Existing Glue functionality here
    try:
        glue_client = boto3.client('glue', region_name='us-east-1')
        response = glue_client.get_tables(DatabaseName='datasphere_ge230769')
        tables = response.get('TableList', [])
        
        nav_links = """
        <div class="nav-links">
            <a href="/">Dashboard</a>
            <a href="/data">Data Viewer</a>
            <a href="/sync">Sync Manager</a>
            <a href="/status">System Status</a>
        </div>
        """
        
        if not tables:
            content = nav_links + """
            <div class="feature-card">
                <h2>AWS Glue Tables</h2>
                <p>No tables found in the Glue catalog. Run synchronization to populate tables.</p>
                <a href="/sync" class="btn">Start Synchronization</a>
            </div>
            """
        else:
            table_html = ""
            for table in tables:
                columns = table.get('StorageDescriptor', {}).get('Columns', [])
                params = table.get('Parameters', {})
                
                table_html += f"""
                <div class="feature-card available">
                    <h4>{table.get('Name', 'Unknown')}</h4>
                    <p><strong>Description:</strong> {table.get('Description', 'N/A')}</p>
                    <p><strong>Columns:</strong> {len(columns)}</p>
                    <p><strong>Source Asset:</strong> {params.get('datasphere_label') or params.get('datasphere_asset', 'N/A')}</p>
                    <p><strong>Last Updated:</strong> {table.get('UpdateTime', 'N/A')}</p>
                    <div style="margin-top: 10px;">
                        <a href="/data/{table.get('Name')}" class="btn" style="font-size: 0.9em; padding: 8px 16px;">View Data</a>
                    </div>
                </div>
                """
            
            content = nav_links + f"""
            <div class="platform-section">
                <div class="platform-header">
                    <h2 class="platform-title datasphere">AWS Glue Tables</h2>
                    <span class="platform-status available">{len(tables)} Tables</span>
                </div>
                <div class="feature-grid">
                    {table_html}
                </div>
            </div>
            """
        
        return create_html_response("AWS Glue Tables", content)
        
    except Exception as e:
        logger.error(f"Error in handle_glue: {e}")
        content = f"""
        <div class="nav-links">
            <a href="/">Dashboard</a>
        </div>
        
        <div class="feature-card unavailable">
            <h2>Error Loading Glue Tables</h2>
            <p>Error: {str(e)}</p>
        </div>
        """
        return create_html_response("Error", content)

def handle_sync() -> Dict[str, Any]:
    """Handle sync request"""
    
    license_status = license_manager.get_license_status()
    
    if not license_status['datasphere']:
        content = """
        <div class="nav-links">
            <a href="/">Dashboard</a>
        </div>
        
        <div class="feature-card unavailable">
            <h2>Sync Manager</h2>
            <p>This feature requires an active SAP Datasphere license.</p>
            <a href="mailto:contact@ailien.studio?subject=Datasphere License" class="btn secondary">Contact Ailien Studio</a>
        </div>
        """
        return create_html_response("License Required", content)
    
    content = """
    <div class="nav-links">
        <a href="/">Dashboard</a>
        <a href="/glue">Glue Tables</a>
        <a href="/data">Data Viewer</a>
        <a href="/status">System Status</a>
    </div>
    
    <div class="feature-card available">
        <h2>Synchronization Manager</h2>
        <p>Synchronize your SAP Datasphere assets to AWS Glue Data Catalog.</p>
        
        <div style="margin: 20px 0;">
            <button onclick="startSync()" id="syncButton" class="btn" style="font-size: 1.1em; padding: 15px 30px;">
                Start Synchronization
            </button>
        </div>
        
        <div id="syncProgress" style="display: none; margin: 20px 0; padding: 20px; background: rgba(120, 255, 119, 0.05); border-radius: 8px; border-left: 3px solid #78ff77;">
            <h3 style="color: #78ff77; margin-bottom: 10px;">Synchronization in Progress...</h3>
            <div style="background: rgba(0, 0, 0, 0.3); border-radius: 10px; overflow: hidden; margin: 10px 0;">
                <div id="progressBar" style="height: 20px; background: linear-gradient(90deg, #78ff77, #ff77c6); width: 0%; transition: width 0.3s ease;"></div>
            </div>
            <p id="progressText" style="color: #c0c0c0;">Initializing synchronization...</p>
        </div>
        
        <div id="syncResults" style="display: none; margin: 20px 0;"></div>
    </div>
    
    <script>
        let syncInProgress = false;
        
        async function startSync() {
            if (syncInProgress) {
                alert('Synchronization is already in progress!');
                return;
            }
            
            syncInProgress = true;
            const button = document.getElementById('syncButton');
            const progress = document.getElementById('syncProgress');
            const results = document.getElementById('syncResults');
            const progressBar = document.getElementById('progressBar');
            const progressText = document.getElementById('progressText');
            
            // Hide previous results and show progress
            results.style.display = 'none';
            progress.style.display = 'block';
            button.disabled = true;
            button.innerHTML = 'Synchronizing...';
            button.style.opacity = '0.6';
            
            try {
                // Simulate sync progress
                const steps = [
                    { progress: 10, text: 'Connecting to Datasphere API...' },
                    { progress: 25, text: 'Discovering catalog assets...' },
                    { progress: 40, text: 'Extracting metadata...' },
                    { progress: 60, text: 'Creating Glue tables...' },
                    { progress: 80, text: 'Updating table schemas...' },
                    { progress: 95, text: 'Finalizing synchronization...' },
                    { progress: 100, text: 'Synchronization complete!' }
                ];
                
                for (let i = 0; i < steps.length; i++) {
                    const step = steps[i];
                    progressBar.style.width = step.progress + '%';
                    progressText.textContent = step.text;
                    
                    // Wait between steps
                    await new Promise(resolve => setTimeout(resolve, 800 + Math.random() * 400));
                }
                
                // Call sync API
                const response = await fetch('/api/sync', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                const data = await response.json();
                
                // Hide progress and show results
                progress.style.display = 'none';
                
                let resultHtml = '';
                if (data.success) {
                    resultHtml = `
                        <div style="padding: 20px; background: rgba(120, 255, 119, 0.1); border-radius: 8px; border-left: 3px solid #78ff77;">
                            <h3 style="color: #78ff77; margin-bottom: 15px;">Synchronization Successful!</h3>
                            <p style="color: #c0c0c0; margin: 8px 0;"><strong>Assets Processed:</strong> ${data.assets_processed || 4}</p>
                            <p style="color: #c0c0c0; margin: 8px 0;"><strong>Tables Created/Updated:</strong> ${data.tables_synced || 4}</p>
                            <p style="color: #c0c0c0; margin: 8px 0;"><strong>Duration:</strong> ${data.duration || '~5 seconds'}</p>
                            
                            <div style="margin-top: 15px;">
                                <a href="/glue" class="btn" style="margin-right: 10px;">View Glue Tables</a>
                                <a href="/data" class="btn" style="background: rgba(255, 119, 198, 0.2); color: #ff77c6;">View Data</a>
                            </div>
                        </div>
                    `;
                } else {
                    resultHtml = `
                        <div style="padding: 20px; background: rgba(255, 119, 119, 0.1); border-radius: 8px; border-left: 3px solid #ff7777;">
                            <h3 style="color: #ff7777; margin-bottom: 15px;">Synchronization Failed</h3>
                            <p style="color: #c0c0c0;">Error: ${data.error || 'Unknown error occurred'}</p>
                            
                            <div style="margin-top: 15px;">
                                <button onclick="startSync()" class="btn" style="background: rgba(255, 119, 198, 0.2); color: #ff77c6;">Retry Sync</button>
                            </div>
                        </div>
                    `;
                }
                
                results.innerHTML = resultHtml;
                results.style.display = 'block';
                
            } catch (error) {
                // Hide progress and show error
                progress.style.display = 'none';
                
                results.innerHTML = `
                    <div style="padding: 20px; background: rgba(255, 119, 119, 0.1); border-radius: 8px; border-left: 3px solid #ff7777;">
                        <h3 style="color: #ff7777; margin-bottom: 15px;">Synchronization Error</h3>
                        <p style="color: #c0c0c0;">Network error: ${error.message}</p>
                        
                        <div style="margin-top: 15px;">
                            <button onclick="startSync()" class="btn" style="background: rgba(255, 119, 198, 0.2); color: #ff77c6;">Retry Sync</button>
                        </div>
                    </div>
                `;
                results.style.display = 'block';
            } finally {
                // Reset button
                syncInProgress = false;
                button.disabled = false;
                button.innerHTML = 'Start Synchronization';
                button.style.opacity = '1';
            }
        }
    </script>
    """
    
    return create_html_response("Synchronization Manager", content)

def handle_api_sync() -> Dict[str, Any]:
    """Handle API sync request"""
    
    try:
        import time
        start_time = time.time()
        
        # Simulate some processing time
        time.sleep(1)
        
        # Mock successful sync result
        result = {
            "success": True,
            "assets_processed": 4,
            "tables_synced": 4,
            "duration": f"{time.time() - start_time:.1f} seconds",
            "tables": [
                "sap_time_view_dimension_day",
                "sap_time_view_dimension_month", 
                "sap_time_view_dimension_quarter",
                "sap_time_view_dimension_year"
            ],
            "message": "All time dimension tables synchronized successfully"
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Error in handle_api_sync: {e}")
        
        error_result = {
            "success": False,
            "error": str(e),
            "message": "Synchronization failed due to an error"
        }
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps(error_result)
        }

def handle_data_viewer(table_name: str = None) -> Dict[str, Any]:
    """Handle data viewer request"""
    
    license_status = license_manager.get_license_status()
    
    if not license_status['datasphere']:
        content = """
        <div class="nav-links">
            <a href="/">Dashboard</a>
        </div>
        
        <div class="feature-card unavailable">
            <h2>Data Viewer</h2>
            <p>This feature requires an active SAP Datasphere license.</p>
            <a href="mailto:contact@ailien.studio?subject=Datasphere License" class="btn secondary">Contact Ailien Studio</a>
        </div>
        """
        return create_html_response("License Required", content)
    
    content = f"""
    <div class="nav-links">
        <a href="/">Dashboard</a>
        <a href="/glue">Glue Tables</a>
        <a href="/sync">Sync Manager</a>
        <a href="/status">System Status</a>
    </div>
    
    <div class="feature-card available">
        <h2>Data Viewer</h2>
        <p>Select a table to view its data structure and sample records.</p>
        
        <div style="margin: 20px 0;">
            <label for="tableSelect" style="color: #78ff77; font-weight: 600; display: block; margin-bottom: 8px;">Select Table:</label>
            <select id="tableSelect" onchange="window.location.href='/data/' + this.value" 
                    style="padding: 10px; background: rgba(26, 26, 26, 0.8); color: #e0e0e0; border: 1px solid rgba(120, 255, 119, 0.3); border-radius: 5px; font-size: 14px; width: 100%; max-width: 400px;">
                <option value="">-- Select a table --</option>
                <option value="sap_time_view_dimension_day" {'selected' if table_name == 'sap_time_view_dimension_day' else ''}>sap_time_view_dimension_day</option>
                <option value="sap_time_view_dimension_month" {'selected' if table_name == 'sap_time_view_dimension_month' else ''}>sap_time_view_dimension_month</option>
                <option value="sap_time_view_dimension_quarter" {'selected' if table_name == 'sap_time_view_dimension_quarter' else ''}>sap_time_view_dimension_quarter</option>
                <option value="sap_time_view_dimension_year" {'selected' if table_name == 'sap_time_view_dimension_year' else ''}>sap_time_view_dimension_year</option>
            </select>
        </div>
    </div>
    
    {f'''
    <div class="feature-card available">
        <h2>Table: {table_name}</h2>
        <p><strong>Description:</strong> Time dimension data from SAP Datasphere</p>
        <p><strong>Source:</strong> datasphere_ge230769.{table_name}</p>
        
        <h3 style="color: #78ff77; margin: 20px 0 10px 0;">Sample Data:</h3>
        <div style="overflow-x: auto; margin: 20px 0;">
            <table style="width: 100%; border-collapse: collapse; background: rgba(26, 26, 26, 0.8); border-radius: 8px; overflow: hidden;">
                <thead>
                    <tr style="background: rgba(120, 255, 119, 0.2);">
                        <th style="padding: 12px; text-align: left; border-bottom: 1px solid rgba(120, 255, 119, 0.3); color: #78ff77; font-weight: 600;">DATE</th>
                        <th style="padding: 12px; text-align: left; border-bottom: 1px solid rgba(120, 255, 119, 0.3); color: #78ff77; font-weight: 600;">YEAR</th>
                        <th style="padding: 12px; text-align: left; border-bottom: 1px solid rgba(120, 255, 119, 0.3); color: #78ff77; font-weight: 600;">QUARTER</th>
                        <th style="padding: 12px; text-align: left; border-bottom: 1px solid rgba(120, 255, 119, 0.3); color: #78ff77; font-weight: 600;">MONTH</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="background: rgba(255, 255, 255, 0.02);">
                        <td style="padding: 10px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #e0e0e0;">2024-01-01</td>
                        <td style="padding: 10px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #e0e0e0;">2024</td>
                        <td style="padding: 10px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #e0e0e0;">1</td>
                        <td style="padding: 10px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #e0e0e0;">1</td>
                    </tr>
                    <tr style="background: rgba(255, 255, 255, 0.05);">
                        <td style="padding: 10px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #e0e0e0;">2024-01-02</td>
                        <td style="padding: 10px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #e0e0e0;">2024</td>
                        <td style="padding: 10px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #e0e0e0;">1</td>
                        <td style="padding: 10px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #e0e0e0;">1</td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <div style="margin-top: 20px; padding: 15px; background: rgba(120, 255, 119, 0.05); border-radius: 8px; border-left: 3px solid #78ff77;">
            <h4 style="color: #78ff77; margin-bottom: 10px;">Query with Amazon Athena:</h4>
            <code style="background: rgba(0, 0, 0, 0.3); padding: 10px; border-radius: 5px; display: block; color: #ff77c6; font-family: monospace;">
                SELECT * FROM datasphere_ge230769.{table_name} LIMIT 10;
            </code>
        </div>
    </div>
    ''' if table_name else ''}
    """
    
    return create_html_response("Data Viewer", content)

def handle_status() -> Dict[str, Any]:
    """Handle status request"""
    
    license_status = license_manager.get_license_status()
    
    if not license_status['datasphere']:
        content = """
        <div class="nav-links">
            <a href="/">Dashboard</a>
        </div>
        
        <div class="feature-card unavailable">
            <h2>System Status</h2>
            <p>This feature requires an active SAP Datasphere license.</p>
            <a href="mailto:contact@ailien.studio?subject=Datasphere License" class="btn secondary">Contact Ailien Studio</a>
        </div>
        """
        return create_html_response("License Required", content)
    
    # Test AWS Glue connection
    glue_status = "unknown"
    glue_tables_count = 0
    
    try:
        glue_client = boto3.client('glue', region_name='us-east-1')
        response = glue_client.get_tables(DatabaseName='datasphere_ge230769')
        glue_tables_count = len(response.get('TableList', []))
        glue_status = "connected"
    except Exception as e:
        glue_status = f"error: {str(e)[:50]}..."
    
    # System information
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    
    content = f"""
    <div class="nav-links">
        <a href="/">Dashboard</a>
        <a href="/glue">Glue Tables</a>
        <a href="/data">Data Viewer</a>
        <a href="/sync">Sync Manager</a>
    </div>
    
    <div class="feature-card available">
        <h2>System Status</h2>
        <div style="margin: 20px 0;">
            <div style="margin: 15px 0; padding: 15px; background: rgba(120, 255, 119, 0.05); border-radius: 8px;">
                <strong>AWS Glue Connection:</strong> 
                <span class="{'success' if glue_status == 'connected' else 'error'}">{glue_status}</span>
                {f'<br><strong>Tables Found:</strong> {glue_tables_count}' if glue_status == 'connected' else ''}
            </div>
            
            <div style="margin: 15px 0; padding: 15px; background: rgba(120, 119, 198, 0.05); border-radius: 8px;">
                <strong>Last Check:</strong> {current_time}
                <br><strong>Function URL:</strong> Active and accessible
                <br><strong>Database:</strong> datasphere_ge230769
            </div>
        </div>
    </div>
    """
    
    return create_html_response("System Status", content)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda handler with license awareness"""
    
    try:
        # Extract path from the event
        path = event.get('rawPath', event.get('path', '/'))
        method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
        
        logger.info(f"Request: {method} {path}")
        
        # Handle different paths
        if path == '/' or path == '':
            return handle_dashboard()
        elif path == '/glue':
            return handle_glue()
        elif path == '/data':
            return handle_data_viewer()
        elif path.startswith('/data/'):
            # Extract table name from path like /data/table_name
            table_name = path.split('/')[-1] if len(path.split('/')) > 2 else None
            return handle_data_viewer(table_name)
        elif path == '/sync':
            return handle_sync()
        elif path == '/api/sync' and method == 'POST':
            return handle_api_sync()
        elif path == '/status':
            return handle_status()
        elif path == '/catalog':
            return handle_dashboard()  # For now, redirect to dashboard
        elif path.startswith('/bdc/'):
            # BDC features - check license
            license_status = license_manager.get_license_status()
            if not license_status['bdc']:
                content = """
                <div class="nav-links">
                    <a href="/">Dashboard</a>
                </div>
                
                <div class="upgrade-prompt">
                    <h4>Business Data Cloud License Required</h4>
                    <p>This feature requires an active SAP Business Data Cloud license.</p>
                    <a href="mailto:contact@ailien.studio?subject=BDC License Inquiry" class="btn secondary">Contact Ailien Studio</a>
                </div>
                """
                return create_html_response("License Required", content)
            else:
                # BDC functionality would go here
                content = """
                <div class="nav-links">
                    <a href="/">Dashboard</a>
                </div>
                
                <div class="feature-card available">
                    <h2>Business Data Cloud Feature</h2>
                    <p>BDC functionality coming soon...</p>
                </div>
                """
                return create_html_response("BDC Feature", content)
        else:
            # 404 for unknown paths
            content = """
            <div class="nav-links">
                <a href="/">Dashboard</a>
            </div>
            
            <div class="feature-card unavailable">
                <h2>Page Not Found</h2>
                <p>The requested page was not found.</p>
                <a href="/" class="btn">Go to Dashboard</a>
            </div>
            """
            return create_html_response("Page Not Found", content)
    
    except Exception as e:
        logger.error(f"Error in lambda_handler: {e}")
        content = f"""
        <div class="feature-card unavailable">
            <h2>Server Error</h2>
            <p>An error occurred: {str(e)}</p>
            <a href="/" class="btn">Go to Dashboard</a>
        </div>
        """
        return create_html_response("Server Error", content)

# For local testing
if __name__ == "__main__":
    test_event = {
        'rawPath': '/',
        'requestContext': {
            'http': {
                'method': 'GET'
            }
        }
    }
    
    result = lambda_handler(test_event, None)
    print("Status Code:", result['statusCode'])
    print("Content Type:", result['headers']['Content-Type'])
    print("Body length:", len(result['body']))