# SAP Datasphere Investigation Guide

## 🎯 Goal: Find the Correct API Endpoints

Your OAuth authentication is working perfectly (✅), but we need to discover the actual API endpoints that SAP Datasphere uses in your tenant.

## 📋 Step-by-Step Investigation

### Step 1: Access SAP Datasphere Admin Console

1. **Open your SAP Datasphere tenant**: https://f45fa9cc-f4b5-4126-ab73-b19b578fb17a.eu10.hcs.cloud.sap
2. **Log in with your administrator credentials**

### Step 2: Look for API Documentation

#### 2.1 Check System Administration
Navigate through these paths and screenshot what you find:

- **System** → **Administration** → **App Integration**
- **System** → **Administration** → **API Access** 
- **System** → **Administration** → **Developer Tools**
- **System** → **Configuration** → **API Settings**

#### 2.2 Check Help/Documentation
Look for:
- **Help** menu → **API Documentation**
- **Help** menu → **Developer Guide**
- **Help** menu → **REST API Reference**
- Any links mentioning "API", "REST", "OData", or "Integration"

#### 2.3 Check Space Management
- Go to **Space Management**
- Look for any API-related options or documentation links
- Note any existing spaces and their IDs

### Step 3: Browser Network Analysis (CRITICAL)

This is the most important step - we'll capture the actual API calls:

#### 3.1 Open Browser Developer Tools
1. **Press F12** to open developer tools
2. **Go to the Network tab**
3. **Clear any existing requests** (click the clear button)

#### 3.2 Perform Actions and Capture API Calls
Do these actions while watching the Network tab:

**Action 1: Navigate to Spaces**
- Click on "Space Management" or "Spaces"
- Look for XHR/Fetch requests in Network tab
- Note the URLs being called

**Action 2: Browse Catalog/Data**
- Navigate to any data catalog or data browser
- Look for API calls related to catalog, tables, or metadata
- Note the endpoint patterns

**Action 3: Check Connections**
- Go to connection management
- Look for API calls related to connections or data sources

#### 3.3 Document the API Calls
For each API call you see, note:
- **Full URL** (e.g., `https://your-tenant.../api/v1/spaces`)
- **HTTP Method** (GET, POST, etc.)
- **Response Status** (200, 404, etc.)
- **Response Content** (JSON structure)

### Step 4: Test Specific Patterns

Based on what you find, we can test specific patterns. Common SAP Datasphere patterns include:

```
# Possible patterns to look for:
/api/v1/spaces
/dwaas-core/api/v1/spaces
/sap/api/v1/spaces
/{tenant-id}/api/v1/spaces
/services/api/v1/spaces
```

### Step 5: Check OAuth Client Permissions

#### 5.1 Review OAuth Client Settings
- Go back to **System** → **Administration** → **App Integration** → **OAuth Clients**
- Click on your OAuth client
- Check the **Scopes** or **Permissions** section
- Look for API-related permissions

#### 5.2 Common Permission Issues
Look for these settings:
- **API Access** - Should be enabled
- **Read Permissions** - For spaces, catalog, connections
- **Scope Settings** - May need specific API scopes

## 📊 What to Document

### Create a simple text file with:

```
=== SAP Datasphere API Investigation Results ===

1. ADMIN CONSOLE FINDINGS:
   - API Documentation location: [URL or "Not found"]
   - Developer section: [URL or "Not found"]
   - API settings: [Description of what you found]

2. NETWORK TRAFFIC ANALYSIS:
   - Spaces API call: [Full URL]
   - Catalog API call: [Full URL]  
   - Connections API call: [Full URL]
   - Other interesting calls: [List URLs]

3. OAUTH CLIENT PERMISSIONS:
   - Current scopes: [List what you see]
   - API access enabled: [Yes/No]
   - Additional permissions available: [List options]

4. EXISTING DATA:
   - Spaces found: [List space names and IDs]
   - Connections found: [List connection names]
   - Sample data available: [Yes/No]
```

## 🚀 Parallel Technical Discovery

While you're doing the manual investigation, I'll run the enhanced discovery script:

```bash
cd improvement-plan
python enhanced_api_discovery.py
```

This will test hundreds of potential endpoint patterns and give us detailed results.

## 🎯 Expected Outcomes

### Best Case Scenario (90% success rate):
- Find working API endpoints in network traffic
- Update MCP server with correct paths
- All tools start working

### Good Case Scenario (80% success rate):
- Find some working endpoints
- Identify permission issues
- Get partial functionality working

### Learning Scenario (70% success rate):
- Understand the API structure
- Identify what permissions are needed
- Create a plan for getting full access

## ⏰ Time Investment

- **Manual investigation**: 30-60 minutes
- **Enhanced discovery script**: 5-10 minutes
- **Analysis and updates**: 30 minutes
- **Total**: 1-2 hours for significant improvement

## 🆘 If You Get Stuck

### Common Issues and Solutions:

**"I can't find any API documentation"**
- This is common - focus on network traffic analysis
- The actual API calls are more important than documentation

**"Network tab shows no API calls"**
- Make sure you're in the Network tab before navigating
- Try refreshing the page and navigating again
- Look for XHR, Fetch, or JS requests specifically

**"I see API calls but they look complex"**
- Just copy the full URLs - we can analyze them
- Even partial information is helpful

**"OAuth client has limited permissions"**
- Note what permissions are available
- We can work with limited access initially

## 📞 Support

If you need help with any step:
1. **Screenshot what you're seeing** - Visual context helps
2. **Copy any URLs or error messages** - Exact text is important
3. **Describe what you tried** - Helps avoid repeating steps

## 🎉 Success Criteria

We'll know we're successful when:
- ✅ Find at least one working API endpoint
- ✅ Understand the URL pattern structure  
- ✅ Identify any permission requirements
- ✅ Can make successful API calls from our MCP server

**Ready to start the investigation? Let me know what you find!**