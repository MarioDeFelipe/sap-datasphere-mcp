# 🔴 EXACT API FLOW - What Actually Works

## Complete Request Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: AUTHENTICATION                                          │
└─────────────────────────────────────────────────────────────────┘

POST https://ailien-test.authentication.eu20.hana.ondemand.com/oauth/token

Headers:
  Authorization: Basic c2ItNjBjYjI2NmUtYWQ5ZC00OWY3LTk5NjctYjUzYjgyODZhMjU5IWIxMzA5MzZ8Y2xpZW50IWIzOTQ0OltTRUNSRVRd
  Content-Type: application/x-www-form-urlencoded

Body:
  grant_type=client_credentials

Response (200 OK):
  {
    "access_token": "eyJhbGciOiJSUzI1NiIsImprdSI6Imh0dHBzOi8v...",
    "token_type": "Bearer",
    "expires_in": 43199,
    "scope": "uaa.resource"
  }

┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: API REQUEST - SERVICE ROOT                             │
└─────────────────────────────────────────────────────────────────┘

GET https://ailien-test.eu20.hcs.cloud.sap/api/v1/datasphere/consumption/analytical/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS

Headers:
  Authorization: Bearer eyJhbGciOiJSUzI1NiIsImprdSI6Imh0dHBzOi8v...
  Accept: application/json
  User-Agent: Datasphere-Metadata-Sync/2.0

Response (200 OK):
  {
    "@odata.context": "$metadata",
    "value": [
      {
        "name": "SAP_SC_FI_AM_FINTRANSACTIONS",
        "kind": "EntitySet",
        "url": "SAP_SC_FI_AM_FINTRANSACTIONS"
      }
    ]
  }

┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: API REQUEST - METADATA                                 │
└─────────────────────────────────────────────────────────────────┘

GET https://ailien-test.eu20.hcs.cloud.sap/api/v1/datasphere/consumption/analytical/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS/$metadata

Headers:
  Authorization: Bearer eyJhbGciOiJSUzI1NiIsImprdSI6Imh0dHBzOi8v...
  Accept: application/xml  ⚠️ IMPORTANT: Must be XML for metadata!
  User-Agent: Datasphere-Metadata-Sync/2.0

Response (200 OK):
  <?xml version="1.0" encoding="utf-8"?>
  <edmx:Edmx Version="4.0" xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx">
    <edmx:DataServices>
      <Schema Namespace="SAP_CONTENT" xmlns="http://docs.oasis-open.org/odata/ns/edm">
        <EntityType Name="SAP_SC_FI_AM_FINTRANSACTIONSType">
          <Property Name="ACCOUNTID_D1" Type="Edm.String"/>
          <Property Name="COUNTRY" Type="Edm.String"/>
          ...
        </EntityType>
      </Schema>
    </edmx:DataServices>
  </edmx:Edmx>

┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: API REQUEST - DATA                                     │
└─────────────────────────────────────────────────────────────────┘

GET https://ailien-test.eu20.hcs.cloud.sap/api/v1/datasphere/consumption/analytical/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS/SAP_SC_FI_AM_FINTRANSACTIONS?$top=5&$select=ACCOUNTID_D1,COUNTRY

Headers:
  Authorization: Bearer eyJhbGciOiJSUzI1NiIsImprdSI6Imh0dHBzOi8v...
  Accept: application/json
  User-Agent: Datasphere-Metadata-Sync/2.0

Query Parameters:
  $top=5
  $select=ACCOUNTID_D1,COUNTRY

Response (200 OK):
  {
    "@odata.context": "$metadata#SAP_SC_FI_AM_FINTRANSACTIONS(ACCOUNTID_D1,COUNTRY)",
    "value": [
      {
        "ACCOUNTID_D1": "1000",
        "COUNTRY": "US"
      },
      {
        "ACCOUNTID_D1": "2000",
        "COUNTRY": "DE"
      }
    ]
  }
```

## 🔴 EXACT URL PATTERNS

### Pattern 1: Service Root (OData Service Document)
```
https://ailien-test.eu20.hcs.cloud.sap/api/v1/datasphere/consumption/analytical/{SPACE}/{MODEL}
```

**Example:**
```
https://ailien-test.eu20.hcs.cloud.sap/api/v1/datasphere/consumption/analytical/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS
```

**Returns:** List of available entity sets

---

### Pattern 2: Metadata (OData $metadata)
```
https://ailien-test.eu20.hcs.cloud.sap/api/v1/datasphere/consumption/analytical/{SPACE}/{MODEL}/$metadata
```

**Example:**
```
https://ailien-test.eu20.hcs.cloud.sap/api/v1/datasphere/consumption/analytical/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS/$metadata
```

**Returns:** XML schema with all fields and types

**⚠️ CRITICAL:** Must use `Accept: application/xml` header!

---

### Pattern 3: Data (OData Entity Set)
```
https://ailien-test.eu20.hcs.cloud.sap/api/v1/datasphere/consumption/analytical/{SPACE}/{MODEL}/{MODEL}
```

**Example:**
```
https://ailien-test.eu20.hcs.cloud.sap/api/v1/datasphere/consumption/analytical/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS/SAP_SC_FI_AM_FINTRANSACTIONS
```

**Returns:** JSON data with records

**Note:** The model name appears TWICE in the URL!

---

## 🔴 EXACT HEADERS

### For JSON Requests (Service Root, Data)
```python
{
    'Authorization': 'Bearer {access_token}',
    'Accept': 'application/json',
    'User-Agent': 'Datasphere-Metadata-Sync/2.0'  # Optional but recommended
}
```

### For XML Requests (Metadata)
```python
{
    'Authorization': 'Bearer {access_token}',
    'Accept': 'application/xml',  # MUST be XML!
    'User-Agent': 'Datasphere-Metadata-Sync/2.0'
}
```

---

## 🔴 EXACT QUERY PARAMETERS (OData Standard)

### Pagination
```
$top=10        # Limit number of results
$skip=20       # Skip first N results
```

### Selection (NEW FEATURE!)
```
$select=Field1                    # Single field
$select=Field1,Field2,Field3      # Multiple fields
```

### Filtering
```
$filter=Country eq 'US'
$filter=Amount gt 1000
$filter=Country eq 'US' and Amount gt 1000
```

### Sorting
```
$orderby=Country asc
$orderby=Amount desc
$orderby=Country asc,Amount desc
```

### Counting
```
$count=true    # Include total count in response
```

---

## 🔴 NO SPECIAL INITIALIZATION REQUIRED

Unlike some APIs, Datasphere does NOT require:
- ❌ Session handshake
- ❌ Cookies
- ❌ CSRF tokens
- ❌ Special initialization endpoints
- ❌ Connection pooling setup

Just:
1. Get OAuth token
2. Make request with Bearer token
3. Done!

---

## 🔴 RESPONSE FORMATS

### JSON Response (Data)
```json
{
  "@odata.context": "$metadata#EntitySet",
  "@odata.count": 100,
  "value": [
    {
      "Field1": "value1",
      "Field2": "value2",
      "@odata.id": "EntitySet('key')"
    }
  ],
  "@odata.nextLink": "?$skip=10"
}
```

### XML Response (Metadata)
```xml
<?xml version="1.0" encoding="utf-8"?>
<edmx:Edmx Version="4.0">
  <edmx:DataServices>
    <Schema Namespace="...">
      <EntityType Name="...">
        <Property Name="Field1" Type="Edm.String"/>
      </EntityType>
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>
```

---

## 🔴 COMMON MISTAKES TO AVOID

### ❌ Wrong: Missing model name repetition
```
/analytical/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS
```

### ✅ Correct: Model name appears twice
```
/analytical/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS/SAP_SC_FI_AM_FINTRANSACTIONS
```

---

### ❌ Wrong: JSON accept for metadata
```python
headers = {'Accept': 'application/json'}
response = requests.get(f'{url}/$metadata', headers=headers)
# Returns 406 Not Acceptable
```

### ✅ Correct: XML accept for metadata
```python
headers = {'Accept': 'application/xml'}
response = requests.get(f'{url}/$metadata', headers=headers)
# Returns 200 OK with XML
```

---

### ❌ Wrong: Forgetting Bearer prefix
```python
headers = {'Authorization': access_token}
```

### ✅ Correct: Include Bearer prefix
```python
headers = {'Authorization': f'Bearer {access_token}'}
```

---

## 🔴 WORKING EXAMPLES

### Example 1: Get All Data
```python
import requests

url = "https://ailien-test.eu20.hcs.cloud.sap/api/v1/datasphere/consumption/analytical/SAP_CONTENT/SAP_SC_FI_AM_FINTRANSACTIONS/SAP_SC_FI_AM_FINTRANSACTIONS"

headers = {
    'Authorization': f'Bearer {token}',
    'Accept': 'application/json'
}

response = requests.get(url, headers=headers)
data = response.json()
```

### Example 2: Get Specific Fields
```python
params = {
    '$select': 'COUNTRY,CURRENCY',
    '$top': 100
}

response = requests.get(url, headers=headers, params=params)
```

### Example 3: Filter and Sort
```python
params = {
    '$filter': "COUNTRY eq 'US'",
    '$orderby': 'CURRENCY asc',
    '$top': 50
}

response = requests.get(url, headers=headers, params=params)
```

---

## 🔴 VERIFICATION CHECKLIST

Before making a request, verify:

- [ ] Base URL is `https://ailien-test.eu20.hcs.cloud.sap`
- [ ] Path starts with `/api/v1/datasphere/consumption/analytical/`
- [ ] Space name is correct (e.g., `SAP_CONTENT`)
- [ ] Model name appears TWICE in data URL
- [ ] Authorization header includes `Bearer ` prefix
- [ ] Accept header is `application/json` (or `application/xml` for metadata)
- [ ] OAuth token is not expired (12-hour lifetime)
- [ ] Timeout is set (30 seconds recommended)

---

## 🔴 TESTED AND CONFIRMED WORKING

All patterns above are:
- ✅ Tested in production
- ✅ Currently operational
- ✅ Used by datasphere_connector.py
- ✅ Used by web dashboard (http://localhost:8001)
- ✅ Verified with test scripts

**Last Verified:** 2025-12-05
**Status:** Fully operational
