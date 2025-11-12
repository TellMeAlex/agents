---
name: jira-issue-operations
description: Manage Jira issue lifecycle for PPLWEBMYST project including creating new issues with validation, searching issues with JQL, updating issue fields and status transitions. Use this skill when you need to create issues (Épica, Historia, Task, Bug, etc.), search for issues by status/assignee/priority/sprint/custom fields, or modify existing issues while respecting PPLWEBMYST workflow rules and custom field requirements.
---

# Jira Issue Operations

Manage the complete issue lifecycle for PPLWEBMYST (workplace accident management system) with validation against project-specific rules.

## Operations Overview

This skill supports three core operations:

1. **CREATE** - Create new issues with strict field validation
2. **SEARCH** - Find issues using JQL with advanced filtering
3. **UPDATE** - Modify issue fields and status transitions

## CREATE Issues

### Basic Creation

To create an issue, provide:
- **summary** (required): Issue title (1-200 chars)
- **issuetype** (required): One of Épica, Historia, Task, Bug, Sub-task, Initiative, Spike, Strategic Theme, Design
- **description** (optional): Detailed description (max 5000 chars)
- **priority** (optional): One of A++, A+, A, B, C, D

### Issue Type Requirements

See `references/validation-rules.md` for complete requirements by type. Key rules:

**Épica** - Must use "Épica" (not "Epic")
- Requires `customfield_11762` (Epic Name) that EXACTLY matches summary
- Optional description
- Can contain multiple stories

**Historia** - User stories
- Required: summary
- Template: "Como [rol] Quiero [funcionalidad] Para que [beneficio]"
- Delivers user value

**Task** - Technical tasks
- Required: summary
- Does NOT deliver direct user value

**Bug** - Defects
- Required: `customfield_10824` (Bug Environment)
- Valid environments: "Produccion", "Pre-produccion", "Testing", "Desarrollo"
- CRITICAL: Must be assigned to QA team
- Must describe: steps to reproduce, expected vs actual behavior

**Sub-task**
- Required: parent issue key (format: PROJECT-NUMBER)
- Required: summary
- Cannot exist without parent

### Field Validation

Before creating, Claude validates:
1. Issue type exists and is supported
2. All required fields present and formatted correctly
3. Custom field values are valid
4. Bug environment if Bug type
5. Epic name matches summary if Épica type
6. Parent exists if Sub-task type

Use `scripts/validate_issue_fields.py` to validate programmatically.

### PPLWEBMYST-Specific Rules

- **Bug issues**: Must assign to QA team only
- **Corrective Actions**: Subtasks MUST have duedate set
- **Épica linking**: Should link to Sprint (customfield_10009)
- **Summary**: Always required, 1-200 characters
- **Vertical Owner** (customfield_42960): Recommended for classification

### Example Creation

```json
{
  "summary": "Implement single sign-on for accident reporting",
  "description": "Users need to authenticate via enterprise SSO system",
  "issuetype": {"name": "Historia"},
  "priority": {"name": "A (Muy Importante)"},
  "components": [{"name": "Authentication"}],
  "labels": ["security", "urgent"]
}
```

For Épica:
```json
{
  "summary": "Mobile Payment Flow",
  "issuetype": {"name": "Épica"},
  "customfield_11762": "Mobile Payment Flow",
  "description": "Complete payment processing for mobile app"
}
```

For Bug:
```json
{
  "summary": "Report form crashes on invalid date input",
  "issuetype": {"name": "Bug"},
  "customfield_10824": "Testing",
  "description": "Steps: 1. Open report form 2. Enter invalid date 3. Click submit\nExpected: Error message\nActual: App crashes",
  "assignee": {"accountId": "qa-team-id"}
}
```

## SEARCH Issues

Use JQL (Jira Query Language) to find issues. See `references/jql-guide.md` for comprehensive examples.

### Common Search Patterns

**By Status**
```jql
project = PPLWEBMYST AND status = "In Progress"
project = PPLWEBMYST AND status IN (Open, Backlog)
```

**By Assignment**
```jql
project = PPLWEBMYST AND assignee = currentUser()
project = PPLWEBMYST AND assignee IS EMPTY
```

**By Priority**
```jql
project = PPLWEBMYST AND priority IN ("A++", "A+", "A")
```

**By Sprint**
```jql
project = PPLWEBMYST AND sprint = "Sprint 42"
```

**By Type**
```jql
project = PPLWEBMYST AND type IN (Bug, Task)
```

**By Custom Fields**
```jql
project = PPLWEBMYST AND customfield_10824 = "Produccion"
project = PPLWEBMYST AND customfield_42960 IS EMPTY
```

**Complex Queries**
```jql
project = PPLWEBMYST AND type = Bug AND customfield_10824 = "Produccion" AND assignee IS EMPTY ORDER BY priority DESC
```

### JQL Builder Script

Use `scripts/build_jql_query.py` to construct complex queries programmatically:

```python
from build_jql_query import JQLBuilder, JQLTemplates

# Build custom query
query = (
    JQLBuilder()
    .issue_type("Bug")
    .status("Open")
    .priority("A++ (Bloqueo)")
    .order_by("created", "DESC")
    .build()
)

# Or use templates
query = JQLTemplates.unassigned_bugs()
query = JQLTemplates.my_open_issues("user@example.com")
query = JQLTemplates.overdue_issues()
```

### Search Results

Queries return paginated results (default 20, max 100):
- issue key (PPLWEBMYST-123)
- summary
- status
- assignee
- priority
- all custom fields
- Jira browse URL

## UPDATE Issues

### Modify Fields

Common field updates:
- **summary**: Change title
- **description**: Update details
- **priority**: Change urgency level
- **assignee**: Reassign issue
- **status**: Transition workflow state
- **duedate**: Set deadline (YYYY-MM-DD format)
- **labels**: Add/remove tags
- **components**: Change affected areas

### Status Transitions

Before any status change, validate:
1. Current state exists (valid workflow state)
2. Target state exists
3. Transition is allowed by workflow

**Valid states**: Open, Analyzing, Backlog, Ready to Start, Prioritized, In Progress, Ready to Verify, Deployed, Closed, Epic Refinement, Discarded, To deploy, Delayed

### Workflow Rules

- Cannot close issue with fewer than 2 comments
- Some states may have conditional transitions
- Use `get_transitions()` to see valid next states for an issue

### Example Updates

```json
{
  "fields": {
    "summary": "Updated title",
    "assignee": {"accountId": "user-123"},
    "priority": {"name": "B (Importante)"}
  }
}
```

For status transition:
```json
{
  "transition": {
    "id": "11",
    "name": "Start Progress"
  }
}
```

## Validation & Error Handling

### Error Codes

- **VALIDATION_ERROR**: Missing or invalid field value
- **ISSUE_TYPE_ERROR**: Invalid issue type
- **CUSTOM_FIELD_ERROR**: Invalid custom field value
- **AUTH_ERROR**: Authentication failure
- **WORKFLOW_ERROR**: Illegal state transition
- **NOT_FOUND_ERROR**: Issue/user/resource doesn't exist

### Field Validator Script

Use `scripts/validate_issue_fields.py` to validate before operations:

```python
from validate_issue_fields import JiraFieldValidator

result = JiraFieldValidator.validate_issue_fields({
    "summary": "Test issue",
    "issuetype": {"name": "Historia"},
    "customfield_10824": "Produccion"
})

if result["valid"]:
    print("Valid issue")
else:
    for error in result["errors"]:
        print(f"Error in {error['field']}: {error['error']}")
```

## Reference Materials

- **validation-rules.md**: Complete field requirements by issue type
- **field-reference.md**: Custom field mappings and formats
- **jql-guide.md**: JQL syntax and query examples

## Best Practices

1. **Always validate before creating**: Use the validator script
2. **Use templates for common queries**: See JQL templates
3. **Respect PPLWEBMYST rules**:
   - Épica names must match summary exactly
   - Bugs go to QA team
   - Corrective action subtasks need duedate
4. **Include meaningful descriptions**: Especially for bugs
5. **Set Vertical Owner**: Helps with issue classification
6. **Use labels and components**: Improves discoverability

## Limitations

- Cannot delete issues (only close them)
- Cannot bypass PPLWEBMYST validation rules
- Mass updates require explicit per-issue confirmation
- User must have project access for operations
