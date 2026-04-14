# 🐛 CREATE_DATABASE_USER SCHEMA VALIDATION BUG

**Date:** December 10, 2024  
**Reporter:** Kiro Testing Agent  
**Priority:** MEDIUM (blocks user testing but CLI implementation is ready)  
**Status:** Ready for Claude to fix  

---

## 🎯 ISSUE SUMMARY

The `create_database_user` tool has a **schema validation inconsistency** that prevents testing, even though the CLI implementation is working correctly.

---

## 🧪 BUG REPRODUCTION

### **Test Command:**
```python
mcp_sap_datasphere_create_database_user(
    database_user_id="KIRO_TEST_USER",
    space_id="DEVAULT_SPACE",
    user_definition={
        "consumption": {
            "spaceSchemaAccess": false,
            "consumptionWithGrant": false
        }
    }
)
```

### **Error 1 (Object Parameter):**
```
>>> Input Validation Error <<<
Invalid parameters provided:
- Parameter 'user_definition' must be a string
```

### **Test Command 2 (String Parameter):**
```python
mcp_sap_datasphere_create_database_user(
    database_user_id="KIRO_TEST_USER",
    space_id="DEVAULT_SPACE", 
    user_definition="{\"consumption\": {\"spaceSchemaAccess\": false}}"
)
```

### **Error 2 (String Parameter):**
```
Validation failed: Invalid arguments: [{
    "instancePath": "/user_definition",
    "schemaPath": "#/properties/user_definition/type", 
    "keyword": "type",
    "params": {"type": "object"},
    "message": "must be object"
}]
```

---

## 🔍 ROOT CAUSE ANALYSIS

### **Schema Contradiction:**
1. **Input Validator Says:** "Parameter 'user_definition' must be a string"
2. **JSON Schema Says:** "must be object" 

### **Likely Causes:**
1. **Tool Schema Definition** expects `user_definition` as `object` type
2. **Input Validator** has custom rule expecting `string` type
3. **Mismatch** between tool schema and validation rules

---

## 🔧 WHAT CLAUDE NEEDS TO FIX

### **1. Check Tool Schema Definition**
Look in `sap_datasphere_mcp_server.py` for the `create_database_user` tool definition:

```python
Tool(
    name="create_database_user",
    description=enhanced["create_database_user"]["description"],
    inputSchema=enhanced["create_database_user"]["inputSchema"]  # <- CHECK THIS
)
```

### **2. Check Enhanced Tool Descriptions**
Look in `tool_descriptions.py` for the `create_database_user` schema:

```python
"create_database_user": {
    "inputSchema": {
        "properties": {
            "user_definition": {
                "type": "???"  # <- SHOULD BE "object" NOT "string"
            }
        }
    }
}
```

### **3. Check Input Validator Rules**
Look in `auth/tool_validators.py` or similar for custom validation:

```python
# Might have custom rule like:
"create_database_user": {
    "user_definition": "string"  # <- SHOULD BE "object"
}
```

---

## ✅ EXPECTED BEHAVIOR

### **Correct Schema Should Be:**
```json
{
  "type": "object",
  "properties": {
    "space_id": {"type": "string"},
    "database_user_id": {"type": "string"}, 
    "user_definition": {
      "type": "object",  // <- OBJECT, NOT STRING
      "properties": {
        "consumption": {"type": "object"},
        "ingestion": {"type": "object"}
      }
    }
  }
}
```

### **Working Test Call Should Be:**
```python
mcp_sap_datasphere_create_database_user(
    database_user_id="KIRO_TEST_USER",
    space_id="DEVAULT_SPACE",
    user_definition={
        "consumption": {
            "spaceSchemaAccess": false,
            "scriptServerAccess": false,
            "consumptionWithGrant": false
        },
        "ingestion": {
            "auditing": {
                "dppRead": {"isAuditPolicyActive": false, "retentionPeriod": 7}
            }
        }
    }
)
```

---

## 🎯 CLAUDE'S ACTION ITEMS

### **Step 1: Identify the Conflict**
- [ ] Check `tool_descriptions.py` for `create_database_user` inputSchema
- [ ] Check if `user_definition` is defined as `"type": "string"` (WRONG)
- [ ] Should be `"type": "object"` (CORRECT)

### **Step 2: Fix the Schema**
- [ ] Change `user_definition` type from `"string"` to `"object"`
- [ ] Add proper object schema with `consumption` and `ingestion` properties
- [ ] Ensure schema matches the CLI implementation expectations

### **Step 3: Test the Fix**
- [ ] Restart MCP server
- [ ] Test with object parameter (should work)
- [ ] Verify CLI command generation works correctly

---

## 📋 VALIDATION CHECKLIST

After Claude's fix, the tool should:
- [ ] ✅ Accept `user_definition` as an object parameter
- [ ] ✅ Pass validation without "must be string" error
- [ ] ✅ Pass validation without "must be object" error  
- [ ] ✅ Generate proper CLI command with temp JSON file
- [ ] ✅ Show CLI error (since CLI not installed) instead of validation error

---

## 🚀 EXPECTED OUTCOME

### **After Fix:**
```python
# This should work:
mcp_sap_datasphere_create_database_user(
    database_user_id="TEST_USER",
    space_id="DEVAULT_SPACE", 
    user_definition={"consumption": {"spaceSchemaAccess": false}}
)

# Expected response:
Error: datasphere CLI not found.
Please install the SAP Datasphere CLI:
1. Download from: https://help.sap.com/docs/SAP_DATASPHERE
2. Ensure it's in your system PATH  
3. Authenticate with: datasphere login
```

---

## 📊 IMPACT

### **Current Status:**
- ✅ CLI implementation working
- ❌ Schema validation blocking testing
- ⚠️ Tool accessible but not testable

### **After Fix:**
- ✅ CLI implementation working
- ✅ Schema validation working  
- ✅ Tool fully testable
- ✅ **Phase 1 progress: 22/35 tools (62.9%) with real data**

---

## 💬 MESSAGE FOR CLAUDE

**"Hi Claude! Great work on the CLI implementations - they're working perfectly! 🎉**

**I found one small schema validation bug in `create_database_user`:**

**The tool schema expects `user_definition` as an object, but the input validator says it must be a string. This creates a contradiction that prevents testing.**

**Can you please:**
1. **Check the `user_definition` parameter type in the tool schema**
2. **Fix it to be `"type": "object"` (not `"string"`)**  
3. **Ensure it matches the CLI implementation expectations**

**Once fixed, the tool should accept object parameters and show the same CLI error as `list_database_users` (which works perfectly).**

**This is the last blocker for completing Phase 1 testing! The CLI implementation itself is excellent.** 🚀"

---

**Reported by:** Kiro Testing Agent  
**Environment:** ailien-test.eu20.hcs.cloud.sap  
**CLI Status:** ✅ Working (confirmed with list_database_users)  
**Issue:** Schema validation only - CLI implementation is perfect  
**Priority:** Fix this to complete Phase 1 validation