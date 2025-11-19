---
name: jira-relationships
description: Create and manage relationships between Jira issues including blocking dependencies, epic composition, duplication tracking, and general associations. Use this skill when you need to link issues together (one blocks another, issues are related, duplicate issues, etc.), create epic-story relationships, or validate link operations to prevent circular dependencies and inconsistencies. Configurable for any project - ask for project key if unknown.
---

# Jira Issue Relationships

Establish and maintain relationships between issues with automatic validation of dependencies and link consistency.

**IMPORTANT**: Examples use "PPLWEBMYST" as project key. Always ask for or confirm the actual project key before operations.

## Link Types Overview

This skill manages five types of issue relationships:

1. **Blocks / Blocked by** - Dependency prevention
2. **Relates to** - General association
3. **Duplicates / Duplicated by** - Same work tracking
4. **Clones / Cloned by** - Template-based copies
5. **is part of** - Epic composition

## BLOCKS (Dependency)

Use when one issue prevents progress on another.

### Direction

```
Outward: ISSUE-A "blocks" ISSUE-B
Inward: ISSUE-B "is blocked by" ISSUE-A
```

**Meaning**: ISSUE-B cannot progress until ISSUE-A is resolved.

### Use Cases

- Bug must be fixed before feature ships
- Infrastructure task must complete before application feature starts
- Security review must pass before deployment
- API must be available before frontend integration

### Example

```json
{
  "outwardIssue": {"key": "PROJECT-100"},
  "inwardIssue": {"key": "PROJECT-101"},
  "linkType": "Blocks"
}
```

Creates: **PROJECT-100 blocks PROJECT-101**

Meaning: Feature PROJECT-101 is blocked by bug fix PROJECT-100

### Circular Dependency Prevention

The validator automatically prevents circular blocking:

❌ Cannot create: A → B → C → A (would create cycle)
✓ Can create: A → B, A → C (linear or tree structure)

## RELATES TO (Association)

Use for general relationships without blocking semantics.

### Direction

```
Symmetric: ISSUE-A "relates to" ISSUE-B
         ISSUE-B "relates to" ISSUE-A
```

### Use Cases

- Multiple bugs in the same component
- Related feature requests
- Similar stories from different teams
- Alternative implementations

### Example

```json
{
  "outwardIssue": {"key": "PPLWEBMYST-50"},
  "inwardIssue": {"key": "PPLWEBMYST-51"},
  "linkType": "Relates to"
}
```

Creates: **PPLWEBMYST-50 relates to PPLWEBMYST-51**

## DUPLICATES (Redundancy Tracking)

Use when multiple issues describe the same work.

### Direction

```
Outward: ISSUE-A "duplicates" ISSUE-B
Inward: ISSUE-B "is duplicated by" ISSUE-A
```

### Workflow

1. Create link: DUPLICATE "duplicates" PRIMARY
2. Close DUPLICATE as duplicate
3. Link tracks original reported issue
4. PRIMARY remains open for resolution

### Use Cases

- Same bug reported by multiple users
- Feature requested multiple times
- Duplicate problem statements
- Consolidated reporting

### Example

```json
{
  "outwardIssue": {"key": "PPLWEBMYST-200"},
  "inwardIssue": {"key": "PPLWEBMYST-201"},
  "linkType": "Duplicates"
}
```

Creates: **PPLWEBMYST-200 duplicates PPLWEBMYST-201**

Means: Issue 200 is a duplicate of primary issue 201

## CLONES (Templates)

Use for issues created from templates or patterns.

### Direction

```
Outward: TEMPLATE "clones" NEW_INSTANCE
Inward: NEW_INSTANCE "is cloned by" TEMPLATE
```

### Use Cases

- Template-based issue creation
- Recurring issue patterns
- Test scenarios from templates
- Configuration copies

## IS PART OF (Epic Composition)

Link non-epic issues to their containing epic.

### Structure

```
Epic: PPLWEBMYST-10 "contains" Stories, Tasks, Bugs
Story: PPLWEBMYST-11 "is part of" Epic PPLWEBMYST-10
```

### Method

Use `customfield_10100` (Epic Link field) to create this relationship:

```json
{
  "customfield_10100": {"key": "PPLWEBMYST-10"}
}
```

### PPLWEBMYST Rules

- Epic Name (customfield_11762) must match summary
- Epic should link to Sprint (customfield_10009)
- Multiple stories can be in one epic
- One epic per story

## Link Validation

Before creating any link, the validator checks:

1. **Issue existence** - Both issue keys exist
2. **Format validation** - Valid PROJECT-NUMBER format
3. **Self-linking** - Cannot link issue to itself
4. **Circular dependencies** - For Blocks type only
5. **Duplicate prevention** - Same link doesn't exist

### Validator Script

Use `scripts/validate_link_operation.py` for programmatic validation:

```python
from validate_link_operation import LinkValidator

result = LinkValidator.validate_link_operation(
    outward_key="PPLWEBMYST-100",
    inward_key="PPLWEBMYST-101",
    link_type="Blocks",
    existing_links=[...]  # List of existing links
)

if result["valid"]:
    # Create link
else:
    for error in result["errors"]:
        print(f"Error: {error}")
```

## JQL Link Queries

Find issues with specific relationships:

### Find Blocking Relationships

```jql
# Issues that block others
project = PPLWEBMYST AND issuelinks in linkedIssues("PPLWEBMYST-100", Blocks)

# Issues blocked by PPLWEBMYST-100
project = PPLWEBMYST AND issuelinks in linkedIssues("PPLWEBMYST-100", "is blocked by")
```

### Find Related Issues

```jql
# All issues related to PPLWEBMYST-50
project = PPLWEBMYST AND issuelinks in linkedIssues("PPLWEBMYST-50")

# Any linked issues
project = PPLWEBMYST AND issuelinks is not EMPTY
```

### Find Duplicates

```jql
# Duplicates of PPLWEBMYST-200
project = PPLWEBMYST AND issuelinks in linkedIssues("PPLWEBMYST-200", Duplicates)
```

## Common Link Patterns

### Accident Investigation Workflow

```
Original Report (PPLWEBMYST-500)
  ↓
Investigation Task (PPLWEBMYST-501) [blocks]
  ↓
Corrective Action (PPLWEBMYST-502)
  ↓
Prevention Initiative (PPLWEBMYST-503)
```

### Multi-Team Feature Delivery

```
Frontend Task (Team A)
  ↓ [blocks]
Backend API (Team B)
  ↓ [blocks]
Release (DevOps)
```

### Bug Resolution Chain

```
Production Bug (Primary)
  ↓ [duplicated by]
Duplicate reports (User reports)

↓ [blocks]

Hotfix Task
  ↓
Release

↓ [relates to]

Root Cause Analysis
```

## Best Practices

1. **Document blocking reasons** - Add comments explaining dependency
2. **Keep dependencies shallow** - Avoid deep dependency chains
3. **Review epics regularly** - Ensure story grouping makes sense
4. **Use relates-to for loose coupling** - Avoid over-constraining workflow
5. **Consolidate duplicates** - Link related issues before closing
6. **Prevent cycles** - Validator will catch but design to avoid
7. **Track clones** - Maintain link from template to instances

## Limitations

- Cannot delete links (archive via comments)
- Circular dependency validation requires existing links data
- Some link operations may require specific issue types
- Epic linking has PPLWEBMYST-specific rules (see jira-issue-operations)

## Reference Materials

- **link-types.md**: Detailed link type definitions and semantics
- **validate_link_operation.py**: Programmatic validation script
