# Jira Link Types - PPLWEBMYST

## Supported Link Relationships

### Directional Links (Blocks / Blocked by)
Use when one issue prevents progress on another.

```
PPLWEBMYST-100 blocks PPLWEBMYST-101
PPLWEBMYST-101 is blocked by PPLWEBMYST-100
```

**Use cases**:
- Bug must be fixed before feature can ship
- API must be completed before frontend integration
- Security review must pass before deployment

### Relates To (Bidirectional)
Use for general related issues without directional dependency.

```
PPLWEBMYST-50 relates to PPLWEBMYST-51
PPLWEBMYST-51 relates to PPLWEBMYST-50
```

**Use cases**:
- Multiple bugs in same component
- Related feature requests
- Similar user stories from different workflows

### Duplicates / Duplicated by
Use when issues describe the same work.

```
PPLWEBMYST-200 duplicates PPLWEBMYST-201
PPLWEBMYST-201 is duplicated by PPLWEBMYST-200
```

**Use cases**:
- Same bug reported by different users
- Feature requested multiple times
- Duplicate issue should be closed and linked to primary

### Clones / Cloned by
Use for copied issues (like template-based creation).

```
PPLWEBMYST-300 clones PPLWEBMYST-301
PPLWEBMYST-301 is cloned by PPLWEBMYST-300
```

### Parent / Child (Hierarchy)
Use for structural hierarchy (only for sub-tasks).

```
PPLWEBMYST-400 (parent) contains PPLWEBMYST-401 (sub-task)
```

**Rules**:
- Only for Sub-task issue type
- One parent per sub-task
- Set via `parent` field, not link

### Epic Linking
Use to associate non-epic issues with epic goals.

```
Epic: PPLWEBMYST-10 (Mobile Payment)
Story: PPLWEBMYST-11 links to Epic PPLWEBMYST-10
```

**Methods**:
- Set via `customfield_10100` (Epic Link field)
- Automatically manages epic composition

## Link Type Matrix

| From Type | To Type | Link Type | Use Case |
|-----------|---------|-----------|----------|
| Any | Any | Blocks/Blocked by | Dependency prevention |
| Any | Any | Relates to | General association |
| Any | Any | Duplicates | Same work |
| Historia | Épica | Epic Link | Story in epic |
| Task | Épica | Epic Link | Technical task in epic |
| Bug | Épica | Epic Link | Bug in epic |
| Any | Sub-task | Parent | Hierarchy |
| Épica | Épica | Relates to | Epic composition |

## Creating Links Programmatically

### Link Direction

Always specify direction in link creation:

```python
{
    "outwardIssue": {"key": "PPLWEBMYST-100"},
    "inwardIssue": {"key": "PPLWEBMYST-101"},
    "linkType": "Blocks"
}
```

This creates: PPLWEBMYST-100 **blocks** PPLWEBMYST-101

### Common Link Patterns

**Blocking relationship**:
```json
{
    "outwardIssue": {"key": "BUGFIX-1"},
    "inwardIssue": {"key": "FEATURE-2"},
    "linkType": "Blocks"
}
```
Means: BUGFIX-1 blocks FEATURE-2

**Related issues**:
```json
{
    "outwardIssue": {"key": "BUG-1"},
    "inwardIssue": {"key": "BUG-2"},
    "linkType": "Relates to"
}
```

**Epic composition**:
```json
{
    "outwardIssue": {"key": "STORY-1"},
    "inwardIssue": {"key": "EPIC-1"},
    "linkType": "is part of"
}
```

## Validation Rules

Before creating links:

1. **Both issues must exist**
   - Validate issue key format: `PROJECT-NUMBER`
   - Verify issue exists in Jira

2. **Issue types must be compatible**
   - Sub-tasks can only have parent to any type
   - Other types can link to other types
   - Epic links have specific type restrictions

3. **Prevent circular dependencies**
   - Cannot create: A blocks B, B blocks C, C blocks A
   - Validate dependency chain before creating

4. **Prevent duplicate links**
   - Cannot create same link twice
   - Check existing links before creation

5. **Link type must be supported**
   - Valid types: Blocks, Relates to, Duplicates, Clones, Parent/Child, Epic Link
   - Verify link type exists in Jira instance

## Link Type Definitions

### Blocks
- **Outward**: "blocks"
- **Inward**: "is blocked by"
- **Direction**: Asymmetric
- **Semantic**: Prevention of progress

### Relates to
- **Outward**: "relates to"
- **Inward**: "relates to"
- **Direction**: Symmetric
- **Semantic**: General association

### Duplicates
- **Outward**: "duplicates"
- **Inward**: "is duplicated by"
- **Direction**: Asymmetric
- **Semantic**: Same work/issue

### Clones
- **Outward**: "clones"
- **Inward**: "is cloned by"
- **Direction**: Asymmetric
- **Semantic**: Copied from

### is part of (Epic Link)
- **Outward**: "is part of"
- **Inward**: "contains"
- **Direction**: Asymmetric
- **Semantic**: Hierarchy/composition

## Query Links in JQL

Find issues with specific links:

```jql
# Issues that block others
project = PPLWEBMYST AND issuelinks in linkedIssues("PPLWEBMYST-100", Blocks)

# Issues related to a specific issue
project = PPLWEBMYST AND issuelinks in linkedIssues("PPLWEBMYST-50")

# All linked issues (any link type)
project = PPLWEBMYST AND issuelinks is not EMPTY

# Duplicates of a specific issue
project = PPLWEBMYST AND issuelinks in linkedIssues("PPLWEBMYST-200", Duplicates)
```

## Best Practices

1. **Use descriptive link reasons** when available in Jira
2. **Prevent link chains** - keep dependency depth shallow
3. **Document blocking reasons** in comments
4. **Review epic composition** regularly
5. **Link related fixes** for traceability
6. **Use duplicates** to consolidate reporting
7. **Document clones** for template tracking

## PPLWEBMYST-Specific Patterns

### Accident Investigation Workflow
```
Original Accident Report → Investigation Task (blocks) → Corrective Action
Corrective Action → Prevention Initiative
```

### Multi-Team Coordination
```
Feature A (Team 1) relates to → Feature B (Team 2)
Infrastructure Task (blocks) → Feature Development
```

### Bug Resolution
```
Production Bug → Investigation Task (blocks) → Release
Related Bug 1 (duplicates) → Related Bug 2 (primary issue)
```
