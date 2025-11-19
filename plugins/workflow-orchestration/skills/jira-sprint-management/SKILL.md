---
name: jira-sprint-management
description: Manage sprint lifecycle, capacity planning, and issue allocation for PPLWEBMYST project including creating sprints, planning team capacity, moving issues between sprints, starting/closing sprints, and analyzing sprint health. Use this skill when you need to plan sprints, calculate team capacity, manage sprint ceremonies, track burndown, or analyze sprint velocity and team performance.
---

# Jira Sprint Management

Manage sprint planning, execution, and reporting for PPLWEBMYST with capacity planning and health monitoring.

## Sprint Lifecycle

Sprints progress through three states:

```
FUTURE → ACTIVE → CLOSED
(planned)  (in progress)  (completed)
```

- **FUTURE**: Sprint created, issues can be added/removed freely
- **ACTIVE**: Sprint started, team is executing, changes discouraged
- **CLOSED**: Sprint completed, sprint report generated

## Creating Sprints

### Basic Sprint Creation

Create a future sprint ready for issue planning:

```json
{
  "name": "Sprint 43",
  "goal": "Mobile payment integration and testing",
  "board": 42
}
```

### Sprint Naming Convention

Use PPLWEBMYST standard format:

```
Sprint [Number] - [Objective]
Sprint 43 - Incident Response Module
Sprint 44 - Database Migration
Sprint 45 - Compliance Enhancements
```

### Setting Sprint Dates

Generate dates with standard duration:

```python
from sprint_helper import SprintHelper

# Create 2-week sprint starting Monday
dates = SprintHelper.plan_sprint_dates("2-week")
# Returns: start_date, end_date, duration_days, working_days
```

Available durations:
- `1-week`: 5 working days
- `2-week`: 10 working days (recommended)
- `3-week`: 15 working days
- `4-week`: 20 working days

## Sprint Planning Process

### Phase 1: Capacity Planning

Before creating sprint, calculate team capacity:

```python
from sprint_helper import SprintHelper

# Calculate base capacity from historical velocity
capacity = SprintHelper.calculate_capacity(
    velocity=30,           # 30 points per 10-day sprint historically
    sprint_duration=10,    # This sprint duration
    utilization=0.8        # Team is 80% available (20% overhead)
)
# Result: ~24 points capacity

# Add safety buffer
safe_capacity = SprintHelper.calculate_velocity_buffer(capacity, buffer_percent=0.2)
# Result: ~19 points (safer commitment)
```

### Phase 2: Team Allocation

Allocate capacity across team members:

```python
team = [
    {"name": "Alice", "capacity": 1.0},   # Full-time
    {"name": "Bob", "capacity": 0.8},     # 80% available
    {"name": "Charlie", "capacity": 1.0}, # Full-time
]

allocation = SprintHelper.plan_capacity_allocation(team, sprint_capacity=24)
# Returns capacity per team member
```

### Phase 3: Issue Assignment

Add prioritized backlog items until capacity is reached:

1. Select highest priority items from backlog
2. Add to sprint until reaching safe capacity
3. Verify all issues have acceptance criteria
4. Assign issues to team members
5. Review dependencies and blockers

### Phase 4: Sprint Kickoff

1. Start sprint (transition from FUTURE to ACTIVE)
2. Conduct team meeting
3. Review sprint goal
4. Clarify acceptance criteria
5. Identify any last-minute blockers

## Managing Sprint Issues

### Moving Issues Between Sprints

**Before Sprint Starts (FUTURE state)**
```
Backlog ↔ Future Sprint (free movement)
```

**During Sprint (ACTIVE state)**
```
Backlog → Active Sprint (only in emergency)
Active Sprint → Backlog (move incomplete)
```

**After Sprint (CLOSED state)**
```
(No movement - sprint is locked)
Incomplete issues automatically move to next sprint
```

### Adding Issues to Sprint

```json
{
  "sprint": 43,
  "issues": ["PPLWEBMYST-100", "PPLWEBMYST-101", "PPLWEBMYST-102"]
}
```

Verify issues:
- Have clear acceptance criteria
- Are estimated (if using points)
- Have no unresolved blockers
- Fit within sprint capacity

### Removing Issues from Sprint

Move back to backlog if:
- Discovered unresolved dependencies
- Capacity changed due to team member absence
- Priority shifted
- Risk assessment indicates too ambitious

```json
{
  "sprint": null,
  "issues": ["PPLWEBMYST-105"]
}
```

## Sprint Execution

### Sprint Health Monitoring

Track sprint health during execution:

```python
from sprint_helper import SprintHelper

health = SprintHelper.analyze_sprint_health(
    issues_total=20,
    issues_completed=8,
    issues_in_progress=7,
    sprint_days_total=10,
    sprint_days_elapsed=5
)
```

Returns:
- **health**: HEALTHY, AT_RISK, or CRITICAL
- **completion_percent**: Progress against planned
- **blocked_percent**: Issues blocked by dependencies
- **recommendations**: Specific actions needed

### Health Status Meanings

**HEALTHY** (Green)
- On or ahead of planned completion
- <20% blocked issues
- Recommend: Continue execution

**AT_RISK** (Yellow)
- Slightly behind plan (10-25% under expected completion)
- Review and address blockers
- Consider scope reduction

**CRITICAL** (Red)
- Significantly behind plan (>25% under expected)
- Immediate action required
- Escalate blockers
- Likely need scope reduction

### Daily Standup Tracking

Check sprint progress:
- Issues completed since yesterday
- Current blockers
- Expected completions today
- Help needed from team

## Sprint Completion

### Pre-Closure Activities

Before closing sprint:

1. **Complete all work** - Finish or move incomplete items
2. **Review acceptance criteria** - Verify all stories met requirements
3. **Update issue status** - Ensure no "in progress" items
4. **Document blockers** - Record any unresolved issues
5. **Add comments** - Explain any incomplete work

### Closing Sprint

When ready to close (transition ACTIVE → CLOSED):

```json
{
  "action": "complete",
  "sprint": 43,
  "incompleteIssuesDestination": 44
}
```

Required parameters:
- **sprint**: Sprint ID to close
- **incompleteIssuesDestination**: Next sprint for unfinished items

### Post-Sprint Activities

After closing sprint:

1. **Generate sprint report** - Completion metrics
2. **Calculate velocity** - Issues/points completed
3. **Retrospective** - Team reflection meeting
4. **Update capacity model** - Adjust for next sprint
5. **Plan next sprint** - Set priorities and dates

## Sprint Reporting

### Velocity Tracking

Calculate sprint velocity after completion:

```python
completed_issues = 18
sprint_points = 32

velocity_current = completed_issues  # or story points
velocity_trends = [28, 32, 30, 31]  # Last 4 sprints
velocity_average = sum(velocity_trends) / len(velocity_trends)  # 30.25
```

Use velocity for:
- Next sprint capacity planning
- Trend analysis (improving/declining?)
- Team performance benchmarking
- Risk assessment

### Sprint Summary Report

Generate executive summary:

```python
from sprint_helper import SprintHelper

summary = SprintHelper.generate_sprint_summary(
    sprint_id=43,
    sprint_name="Sprint 43 - Incident Response",
    sprint_goal="Deliver core incident response features",
    total_issues=20,
    completed_issues=18,
    velocity=32,
    team_size=3
)
```

Returns:
- Sprint goal and objectives
- Completion rate and metrics
- Team velocity and distribution
- Key achievements

### Burndown Chart Data

Sprint burndown shows:
- **X-axis**: Days in sprint
- **Y-axis**: Issues remaining
- **Red line**: Ideal burndown (linear)
- **Blue line**: Actual progress

Analyze burndown:
- Steady slope: Good pace
- Steep drop: Burst of productivity
- Flat periods: Potential blockers
- Upward trend: Scope creep

## Capacity Planning Templates

### Standard 2-Week Sprint

```python
from sprint_helper import SprintTemplates

sprint = SprintTemplates.create_2week_sprint(sprint_number=43)
# Creates sprint with:
# - 10 working days
# - Monday-Friday schedule
# - Pre-configured dates
```

### Feature-Focused Sprint

```python
sprint = SprintTemplates.create_feature_sprint(
    sprint_number=43,
    feature_name="Mobile Payment Processing"
)
# Creates sprint optimized for single feature delivery
```

## Multi-Sprint Planning (Epics)

### Epic Across Multiple Sprints

```
Epic: "Mobile Payment System" (PPLWEBMYST-10)
├─ Sprint 43: "Authentication & Security" (Stories 11-13)
├─ Sprint 44: "Payment Processing" (Stories 14-16)
└─ Sprint 45: "Reporting & Analytics" (Stories 17-19)
```

Planning approach:
1. Create epic with overall goal
2. Break into stories
3. Sequence stories across sprints
4. Identify inter-sprint dependencies
5. Plan sprints sequentially

## Best Practices

1. **Consistent velocity tracking** - Use historical data for planning
2. **Never exceed capacity** - Leave 20% buffer for unknowns
3. **Front-load risk** - Tackle blockers early in sprint
4. **Communicate changes** - Document scope adjustments
5. **Include buffer days** - Account for team overhead
6. **Regular retrospectives** - Continuous improvement
7. **Maintain sprint cadence** - Predictable rhythm

## Common Challenges

### Over-Commitment

**Problem**: Planned capacity > actual velocity
**Solution**: Reduce sprint scope or adjust velocity model

### Under-Utilization

**Problem**: Team completes less than planned
**Solutions**:
- Improve estimation accuracy
- Reduce technical debt
- Better define acceptance criteria
- Identify team blockers

### Scope Creep

**Problem**: Adding items mid-sprint
**Solution**: Create strict sprint freeze policy
**Exception**: Critical production fixes

### Team Disruption

**Problem**: Absences reduce capacity
**Solution**: Pre-plan around known absences, adjust capacity

## Reference Materials

- **sprint-operations.md**: Detailed sprint workflow and terminology
- **sprint_helper.py**: Capacity calculation and health analysis scripts

## Limitations

- Cannot move closed sprint issues
- Historical velocity requires at least 3-4 sprints
- Capacity model assumes stable team composition
- Burndown assumes consistent issue distribution
