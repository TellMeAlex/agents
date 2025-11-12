# Sprint Operations - PPLWEBMYST

## Sprint Workflow States

### Sprint Lifecycle

```
CREATED → STARTED → ACTIVE → CLOSED
         (not started)      (completed)
```

### State Descriptions

**CREATED** (Future Sprint)
- Sprint exists but hasn't started
- Can add/remove issues freely
- Can edit sprint details (name, dates, goals)
- Cannot move issues between sprints until started

**STARTED** (Active Sprint)
- Sprint is currently in progress
- Team is working on issues
- Burndown chart is updating
- Still can move issues, but not recommended mid-sprint

**CLOSED** (Completed Sprint)
- Sprint is finished
- All issues resolved or moved to next sprint
- Sprint report available
- Cannot add/move issues to closed sprint

## Sprint Properties

### Core Fields

- **name**: Sprint identifier (e.g., "Sprint 42")
- **state**: FUTURE, ACTIVE, or CLOSED
- **startDate**: ISO format (YYYY-MM-DDTHH:mm:ss.sssZ)
- **endDate**: ISO format
- **completeDate**: When sprint was closed (read-only)
- **goal**: Sprint objective (optional)

### Agile Board Configuration

- **board**: Associated Agile board
- **velocity**: Historical average story points/issues completed
- **capacity**: Team capacity for sprint

## Managing Issues in Sprints

### Moving Issues Between Sprints

```
Current Sprint ←→ Backlog ←→ Future Sprint
```

Valid transitions:
- Backlog → Future Sprint (when sprint created)
- Future Sprint → Backlog (before sprint starts)
- Backlog → Active Sprint (not recommended during sprint)
- Active Sprint → Backlog (emergency only)
- Any Sprint → Next Sprint (at sprint end)

### Issue Eligibility

An issue can be added to a sprint if:
- Issue exists (valid key format)
- Sprint exists (valid state)
- Issue not already in active/closed sprint (for some configurations)
- User has permission to move issue

### Sprint Readiness Checklist

Before starting sprint, verify:
- ✓ All issues have acceptance criteria
- ✓ All issues have story points or complexity
- ✓ Critical issues have assignees
- ✓ No blockers preventing work
- ✓ Team capacity matches commitment

## Sprint Metrics

### Burndown Tracking

Tracked during active sprint:
- Issues completed vs planned
- Story points completed
- Velocity trending
- Days remaining

### Capacity Planning

- **Velocity**: Average issues/points completed per sprint
- **Team size**: Number of active team members
- **Sprint length**: Duration in days
- **Planned capacity**: Total points/issues team can complete

### Planning Formula

```
Sprint Capacity = Team Velocity × Sprint Length Adjustment
Example: 30 points/sprint × 1.0 factor = 30 points commitment
```

## Sprint Management Operations

### Create Sprint

```json
{
  "name": "Sprint 43",
  "goal": "Mobile payment integration",
  "board": 42
}
```

Creates new future sprint ready for issue assignment.

### Update Sprint

Change sprint properties:
```json
{
  "name": "Sprint 43 - Updated",
  "goal": "Enhanced mobile payment integration"
}
```

Can update:
- name
- goal
- startDate (before started)
- endDate (before ended)

Cannot update:
- state (use start/complete operations)
- board
- completeDate (set automatically)

### Start Sprint

Transitions sprint from FUTURE to ACTIVE:
```json
{
  "action": "start",
  "sprint": 43
}
```

Effects:
- Sprint becomes active
- Burndown tracking begins
- Cannot add new issues during sprint (depends on configuration)

### Complete Sprint

Transitions sprint from ACTIVE to CLOSED:
```json
{
  "action": "complete",
  "sprint": 43,
  "incompleteIssuesDestination": 44  # Next sprint
}
```

Required:
- Specify destination sprint for incomplete issues
- Usually next sprint

### Delete Sprint

Remove a future sprint:
```json
{
  "action": "delete",
  "sprint": 43,
  "issueDestination": 44
}
```

Restrictions:
- Can only delete FUTURE sprints
- Must specify where issues go
- Active/closed sprints cannot be deleted

## Sprint Planning Process

### Phase 1: Backlog Refinement (Pre-Sprint)

1. Review backlog
2. Add story points/complexity
3. Identify blockers
4. Create acceptance criteria
5. Estimate effort
6. Prioritize

### Phase 2: Sprint Planning

1. Create new sprint (or use existing future)
2. Move prioritized items from backlog
3. Calculate team velocity
4. Add items until sprint capacity reached
5. Review for feasibility
6. Set sprint goal

### Phase 3: Sprint Execution

1. Start sprint
2. Assign issues to team members
3. Track burndown
4. Manage blockers
5. Adjust scope if needed

### Phase 4: Sprint Completion

1. Move incomplete issues
2. Complete sprint
3. Generate sprint report
4. Retrospective meeting
5. Calculate velocity
6. Plan next sprint

## Sprint Reports

### Burndown Chart

Shows:
- Planned work (line)
- Completed work (line)
- Ideal progress line
- Current sprint day

Use to:
- Monitor progress
- Identify risks early
- Plan scope adjustments
- Calculate velocity

### Velocity Metrics

Calculated after sprint close:
- Issues completed
- Story points completed
- Average per sprint
- Trend over time

### Sprint Review

Checklist:
- How many issues planned?
- How many completed?
- How many incomplete?
- What was velocity?
- What blockers occurred?
- What went well?
- What to improve?

## Typical Sprint Duration

### Common Patterns

- **1-week sprints**: Fast feedback, for high-change environments
- **2-week sprints**: Standard, balance learning and execution
- **3-week sprints**: For large projects with planning overhead
- **4-week sprints**: Monthly planning rhythm

### PPLWEBMYST Recommendation

2-week sprints (10 working days) for:
- Regular planning rhythm
- Fast feedback cycles
- Manageable sprint scope
- Compliance documentation

## Sprint Issues Best Practices

1. **Estimate consistently** - Use same scale across sprints
2. **Keep epics across sprints** - Don't break mid-epic
3. **Leave capacity buffer** - Don't fill to 100%
4. **Track velocity** - Use data for planning
5. **Move complete issues only** - Keep in-progress in sprint
6. **Document decisions** - In sprint goals/comments
7. **Review scope changes** - Track adjustments
8. **Communicate blockers** - Escalate early

## Common Sprint Problems

### Over-commitment

**Problem**: Planned capacity > team velocity
**Solution**: Reduce scope or extend timeline

### Under-utilization

**Problem**: Incomplete issues due to capacity
**Solution**: Increase planning precision, reduce defects

### Scope Creep

**Problem**: Adding items mid-sprint
**Solution**: Create policy for scope freeze
**Exception**: Blocker emergency fixes only

### Velocity Variance

**Problem**: Unpredictable velocity week-to-week
**Solution**: Identify disruptions, stabilize team

## PPLWEBMYST Sprint Standards

### Sprint Naming Convention

```
Sprint [Number] - [Objective]
Sprint 43 - Incident Response Module
Sprint 44 - Database Migration
```

### Issue Requirements for Sprint Entry

- Summary: Clear and descriptive
- Type: Valid PPLWEBMYST type
- Priority: Assigned
- Assignee: (Usually set during sprint)
- Story Points: If using estimation
- Acceptance Criteria: For features

### Mandatory Sprint Metadata

- Sprint goal: What team will accomplish
- Start date: When team begins
- End date: Expected completion
- Team members: Who's working on it

## Integration with Epics

### Epic-Sprint Relationship

```
Epic: "Mobile Payment System" (PPLWEBMYST-10)
├─ Sprint 43: "Authentication" (Stories 11-13)
├─ Sprint 44: "Payment Processing" (Stories 14-16)
└─ Sprint 45: "Reporting" (Stories 17-19)
```

Benefits:
- Large features broken across sprints
- Clear phasing
- Trackable progress
- Dependency management

### Multi-Sprint Epic Planning

1. Create epic
2. Break into user stories
3. Sequence across sprints
4. Plan dependencies
5. Assign to sprint queue
6. Execute sprints sequentially
