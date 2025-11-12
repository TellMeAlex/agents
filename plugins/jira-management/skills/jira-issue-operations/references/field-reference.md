# Jira Field Reference - PPLWEBMYST

## Standard Fields

### Core Issue Fields
- **summary**: Issue title (1-200 chars, required)
- **description**: Detailed description (max 5000 chars)
- **type**: Issue type (Épica, Historia, Task, Bug, Sub-task, Initiative, Spike, Strategic Theme, Design)
- **priority**: Priority level (A++, A+, A, B, C, D)
- **status**: Current workflow state
- **assignee**: User assigned to issue
- **reporter**: User who created issue
- **created**: Creation timestamp (read-only)
- **updated**: Last update timestamp (read-only)
- **duedate**: Expected completion date (YYYY-MM-DD)
- **labels**: Issue tags (multiple)
- **components**: Affected components (multiple)

### Issue Hierarchy
- **parent**: Parent issue key (for subtasks)
- **issuetype**: Machine-readable type
- **project**: Project key (always PPLWEBMYST)

### Issue Links
- **issuelinks**: Relationships to other issues
  - Blocks / Blocked by
  - Duplicates / Duplicated by
  - Relates to
  - Clones / Cloned by

## Custom Fields

### Epic Management (customfield_11762)
- **Field name**: Epic Name
- **Type**: Text
- **Used in**: Épica issues only
- **Rule**: MUST exactly match summary field
- **Example**: If summary="Mobile Payment Flow", then customfield_11762="Mobile Payment Flow"

### Bug Tracking (customfield_10824)
- **Field name**: Bug Environment
- **Type**: Select
- **Used in**: Bug issues
- **Valid options**: "Produccion", "Pre-produccion", "Testing", "Desarrollo"
- **Required**: Yes, cannot create Bug without this

### Sprint Management (customfield_10009)
- **Field name**: Sprint
- **Type**: Sprint
- **Used in**: Can be on any issue
- **Format**: Sprint ID or name

### Product & Portfolio

#### customfield_43462
- **Field name**: Principal Product
- **Type**: Select/Multi-select
- **Used in**: Initiative type

#### customfield_43463
- **Field name**: Affected Products
- **Type**: Select/Multi-select
- **Used in**: Initiative type

#### customfield_45761
- **Field name**: Portfolio Priority
- **Type**: Select
- **Used in**: Initiative type

### Organization (customfield_42960)
- **Field name**: Vertical Owner
- **Type**: User/Select
- **Used in**: All issues (recommended)
- **Purpose**: Classification and responsibility

### Legacy Epic Link (customfield_10100)
- **Field name**: Epic Link
- **Type**: Link
- **Used in**: Non-epic issues
- **Note**: Typically uses parent field instead in modern Jira

## Field Validation Rules

### Summary Field
```
Pattern: 1-200 characters
Requirements: 
- Non-empty
- No leading/trailing whitespace
- Should be descriptive and unique
```

### Description Field
```
Pattern: 0-5000 characters
Format: Supports markdown/rich text
Requirements:
- Maximum 5000 characters
- Should follow formatting standards
```

### Date Field (duedate)
```
Format: YYYY-MM-DD (ISO 8601)
Example: 2025-12-31
Notes: For corrective actions, this is required
```

### Select Fields (priority, environment)
```
Format: Exact value from predefined list
Note: Values are case-sensitive
Use: Get available options via Jira API first
```

### User Fields (assignee, reporter)
```
Format: User account ID or email
Validation: User must exist in Jira
Note: Verify project access before assigning
```

## Field Mapping Guide

When creating issues programmatically:

```python
# Minimal fields
{
    "summary": str,          # Required
    "issuetype": {"name": str},  # Required (Épica, Historia, etc.)
    "project": {"key": "PPLWEBMYST"}  # Always PPLWEBMYST
}

# Standard fields
{
    "summary": str,
    "description": str,
    "priority": {"name": str},
    "assignee": {"accountId": str},
    "duedate": "YYYY-MM-DD",
    "components": [{"name": str}],
    "labels": [str],
}

# Custom fields (customfield_*)
{
    "customfield_11762": str,      # Epic Name
    "customfield_10824": str,      # Bug Environment
    "customfield_10009": int,      # Sprint ID
    "customfield_42960": str,      # Vertical Owner
}

# Relationships
{
    "parent": {"key": str},        # For subtasks
    "customfield_10100": {"key": str}  # Legacy epic link
}
```
