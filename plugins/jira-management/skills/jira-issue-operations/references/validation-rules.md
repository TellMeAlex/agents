# PPLWEBMYST Validation Rules Reference

## Issue Type Requirements

### ÉPICA (NOT "Epic")
- **Required fields**: 
  - `summary` (1-200 chars)
  - `customfield_11762` (Epic Name) - MUST EXACTLY MATCH summary
- **Optional**: description (max 5000 chars)
- **Critical**: Always use "Épica" as issue_type, never "Epic"

### HISTORIA (User Story)
- **Required**: `summary` (1-200 chars, non-empty)
- **Optional**: description, components, assignee
- **Template**: "Como [rol] Quiero [funcionalidad] Para que [beneficio]"
- **Validation**: Must deliver user value

### TASK (Technical Task)
- **Required**: `summary`
- **Optional**: description, assignee, duedate
- **Restriction**: Does NOT deliver direct user value

### BUG (Defect)
- **Required fields**: 
  - `summary`
  - `customfield_10824` (Bug Environment)
- **Valid environments**: "Produccion", "Pre-produccion", "Testing", "Desarrollo"
- **Critical rule**: MUST be assigned to QA team
- **Must include**: Steps to reproduce, expected vs actual behavior

### SUB-TASK
- **Required**: parent issue key (valid format: PROJECT-NUMBER)
- **Required**: `summary`
- **Restriction**: Cannot exist without parent

### INITIATIVE
- **Optional**: `customfield_43462` (Principal Product), `customfield_43463` (Affected Products)
- **Optional**: `customfield_45761` (Portfolio Priority)

### SPIKE
- **Purpose**: POC, research, technical exploration
- **No special requirements**

### STRATEGIC THEME
- **Purpose**: High-level strategic guidance
- **No special requirements**

### DESIGN
- **Purpose**: UX/UI design and experience
- **No special requirements**

## Workflow States

**Valid states**: Open, Analyzing, Backlog, Ready to Start, Prioritized, In Progress, Ready to Verify, Deployed, Closed, Epic Refinement, Discarded, To deploy, Delayed

## Priority Standards

- **A++ (Bloqueo)**: Blocking
- **A+ (Crítico)**: Critical
- **A (Muy Importante)**: Very Important
- **B (Importante)**: Important
- **C (Menor)**: Minor
- **D (Trivial)**: Trivial

## PPLWEBMYST-Specific Rules

1. **Bug assignment**: Must go to QA team only
2. **Corrective Actions**: Subtasks MUST have duedate set
3. **Épica linking**: Must link to Sprint (customfield_10009)
4. **Issue closure**: Cannot close with fewer than 2 comments
5. **Classification**: Vertical Owner (customfield_42960) should be populated

## Common Custom Fields

| Field | customfield_* | Used in | Values |
|-------|---------------|---------|--------|
| Epic Name | 11762 | Épica | String matching summary |
| Bug Environment | 10824 | Bug | Produccion, Pre-produccion, Testing, Desarrollo |
| Sprint | 10009 | All issues | Sprint ID or name |
| Epic Link | 10100 | Non-epics | Epic issue key |
| Principal Product | 43462 | Initiative | Product list |
| Affected Products | 43463 | Initiative | Product list |
| Portfolio Priority | 45761 | Initiative | Priority level |
| Vertical Owner | 42960 | All issues | Team/person name |

## Error Codes

| Error | Remediation |
|-------|------------|
| VALIDATION_ERROR | Missing or invalid required field |
| ISSUE_TYPE_ERROR | Invalid issue type for project |
| CUSTOM_FIELD_ERROR | Invalid custom field value |
| AUTH_ERROR | Authentication failure, retry needed |
| WORKFLOW_ERROR | Illegal state transition |
| NOT_FOUND_ERROR | Issue/user/resource not found |
