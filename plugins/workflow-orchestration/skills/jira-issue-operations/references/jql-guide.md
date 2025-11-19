# JQL Query Guide - PPLWEBMYST

## Basic JQL Syntax

```
field = value
field != value
field > value
field <= value
field IN (value1, value2)
field NOT IN (value1, value2)
field ~ "text"          # Contains
field !~ "text"         # Does not contain
field IS EMPTY
field IS NOT EMPTY
```

Combine with: `AND`, `OR`, `NOT`, `()`

## Common PPLWEBMYST Queries

### By Project
```jql
project = PPLWEBMYST
```

### By Issue Type
```jql
project = PPLWEBMYST AND type = Historia
project = PPLWEBMYST AND type IN (Bug, Task)
```

### By Status/Workflow State
```jql
project = PPLWEBMYST AND status = "In Progress"
project = PPLWEBMYST AND status != Closed
project = PPLWEBMYST AND status IN (Open, Backlog)
```

### By Assignment
```jql
project = PPLWEBMYST AND assignee = currentUser()
project = PPLWEBMYST AND assignee = "user@example.com"
project = PPLWEBMYST AND assignee IS EMPTY
```

### By Priority
```jql
project = PPLWEBMYST AND priority = "A (Muy Importante)"
project = PPLWEBMYST AND priority IN ("A++", "A+", "A")
```

### By Sprint
```jql
project = PPLWEBMYST AND sprint = "Sprint 42"
project = PPLWEBMYST AND sprint IS NOT EMPTY
```

### By Labels/Components
```jql
project = PPLWEBMYST AND labels = urgent
project = PPLWEBMYST AND components = "Mobile App"
```

### By Dates
```jql
project = PPLWEBMYST AND duedate >= 2025-01-01
project = PPLWEBMYST AND duedate <= 2025-12-31
project = PPLWEBMYST AND updated >= -7d  # Last 7 days
```

### By Custom Fields

#### Bug Environment
```jql
project = PPLWEBMYST AND customfield_10824 = "Produccion"
project = PPLWEBMYST AND customfield_10824 IN ("Testing", "Desarrollo")
```

#### Vertical Owner
```jql
project = PPLWEBMYST AND customfield_42960 = "MyTeam"
project = PPLWEBMYST AND customfield_42960 IS NOT EMPTY
```

#### Sprint (customfield_10009)
```jql
project = PPLWEBMYST AND customfield_10009 = 42
```

## Complex Queries

### Find Unassigned Bugs
```jql
project = PPLWEBMYST AND type = Bug AND assignee IS EMPTY
```

### Find Overdue Issues
```jql
project = PPLWEBMYST AND duedate < now() AND status != Closed
```

### Find Issues in Progress for Current User
```jql
project = PPLWEBMYST AND assignee = currentUser() AND status = "In Progress"
```

### Find Blocked Issues
```jql
project = PPLWEBMYST AND issuelinks in linkedIssues("PPLWEBMYST-123")
```

### Find Issues without Vertical Owner
```jql
project = PPLWEBMYST AND customfield_42960 IS EMPTY
```

### Find Open Issues by Creation Date
```jql
project = PPLWEBMYST AND status = Open AND created >= -30d ORDER BY created DESC
```

### Find All Unresolved Issues
```jql
project = PPLWEBMYST AND resolution = Unresolved
```

### Find Issues Assigned to QA Team
```jql
project = PPLWEBMYST AND assignee IN ("qa-user1@example.com", "qa-user2@example.com")
```

## Query Best Practices

1. **Always include project filter first**
   ```jql
   project = PPLWEBMYST AND ...
   ```

2. **Use IN for multiple values**
   ```jql
   status IN (Open, Backlog, Prioritized)  # Good
   status = Open OR status = Backlog       # Also works, less efficient
   ```

3. **Order results for clarity**
   ```jql
   ... ORDER BY created DESC
   ... ORDER BY priority DESC, assignee ASC
   ... ORDER BY duedate ASC
   ```

4. **Limit result sets with pagination**
   - Default: 20 results
   - Max: 100 results per query
   - Use offset for pagination: `... OFFSET 20`

5. **Use relative dates for recurring queries**
   ```jql
   -7d    # Last 7 days
   -30d   # Last 30 days
   -3m    # Last 3 months
   now()  # Current moment
   ```

## Functions Available in Jira

- `currentUser()`: Currently logged-in user
- `now()`: Current timestamp
- `startOfDay()`: Start of today
- `startOfWeek()`: Start of this week
- `startOfMonth()`: Start of this month
- `startOfYear()`: Start of this year
- `linkedIssues("KEY")`: Issues linked to KEY
- `issuesInEpic("EPIC-KEY")`: Issues in epic

## Common Mistake Prevention

### ❌ Don't
```jql
type = Épica          # Missing quotes on Spanish
customfield_10824 = Produccion  # Missing quotes
```

### ✓ Do
```jql
type = "Épica"
customfield_10824 = "Produccion"
```

## Query Validation Tips

1. Test queries in Jira UI first before automation
2. Check if custom field IDs match your instance
3. Validate user emails exist before filtering by assignee
4. Verify sprint names/IDs if querying by sprint
5. Use quotes for values with spaces: `"In Progress"`

## Performance Considerations

- Avoid very broad queries without status filter
- Use sprint filter for active work
- Limit to 50 results for dashboard queries
- Consider indexing frequently-used fields
