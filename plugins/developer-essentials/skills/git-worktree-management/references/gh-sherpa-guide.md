# gh-sherpa Configuration & Usage

## What is gh-sherpa?

`gh-sherpa` is a GitHub CLI extension that automates branch and PR creation with intelligent naming conventions. It's designed to work seamlessly with issues and provides:

- **Automatic branch naming** based on issue type
- **Prefix conventions** (feature/, bugfix/, hotfix/, etc.)
- **Smart issue linking** in commits and PRs
- **Template-based PRs** with proper formatting
- **Integration with git worktrees**

**Repository**: https://github.com/InditexTech/gh-sherpa

## Installation

### Prerequisites
- GitHub CLI (`gh`) installed
- Git configured
- Bash/Zsh shell

### Install Extension

```bash
# Install gh-sherpa
gh extension install InditexTech/gh-sherpa

# Verify installation
gh sherpa --version
```

### Upgrade Existing Installation

```bash
gh extension upgrade gh-sherpa
```

### Uninstall

```bash
gh extension remove gh-sherpa
```

## Configuration

### Basic Setup

Create `.sherparc.yml` in your repository root:

```yaml
# .sherparc.yml
config:
  # GitHub organization
  organization: "InditexTech"
  
  # Default base branch
  baseBranch: "main"
  
  # Jira settings (if using Jira for issues)
  jira:
    enabled: true
    apiUrl: "https://your-jira-instance.atlassian.net"
    projectKey: "PPLWEBMYST"
  
  # GitHub settings
  github:
    # Auto-draft PR
    draft: false
    # Require PR description
    requireDescription: true
    # Auto-link related issues
    linkRelated: true

# Branch naming conventions
branches:
  feature: "feature/{issue-key}-{issue-title}"
  bug: "bugfix/{issue-key}-{issue-title}"
  hotfix: "hotfix/{issue-key}-{issue-title}"
  chore: "chore/{issue-key}-{issue-title}"
  task: "task/{issue-key}-{issue-title}"

# PR template
pr:
  title: "[{issue-key}] {issue-title}"
  description: |
    ## Description
    {issue-description}
    
    ## Changes
    - [ ] Change 1
    - [ ] Change 2
    
    ## Testing
    - [ ] Unit tests passing
    - [ ] Integration tests passing
    
    Closes #{issue-number}
  
  # Automatically assign reviewers
  reviewers:
    - "team-leads"
    - "platform-team"
```

### PPLWEBMYST-Specific Configuration

```yaml
# .sherparc.yml - PPLWEBMYST Setup
config:
  organization: "Inditex"
  baseBranch: "main"
  
  jira:
    enabled: true
    apiUrl: "https://jira.inditex.com"
    projectKey: "PPLWEBMYST"
    # Map issue types to branch prefixes
    issueTypeMapping:
      "Épica": "epic"
      "Historia": "feature"
      "Task": "task"
      "Bug": "bugfix"
      "Sub-task": "task"
      "Initiative": "initiative"
      "Spike": "spike"
      "Strategic Theme": "theme"
      "Design": "design"
  
  github:
    draft: false
    requireDescription: true
    
branches:
  epic: "epic/{issue-key}-{issue-title}"
  feature: "feature/{issue-key}-{issue-title}"
  bugfix: "bugfix/{issue-key}-{issue-title}"
  task: "task/{issue-key}-{issue-title}"
  spike: "spike/{issue-key}-{issue-title}"
  hotfix: "hotfix/{issue-key}-critical"

pr:
  title: "[{issue-key}] {issue-title}"
  description: |
    ## Description
    Resolves #{issue-key}
    {issue-description}
    
    ## Type of Change
    - [ ] Feature
    - [ ] Bugfix
    - [ ] Hotfix
    - [ ] Documentation
    
    ## Changes Made
    - [ ] Implementation of {issue-title}
    
    ## Testing
    - [ ] Unit tests added/updated
    - [ ] Integration tests passing
    - [ ] Manual testing completed
    
    ## Checklist
    - [ ] Code follows project style
    - [ ] Self-review completed
    - [ ] Comments added for complex logic
    - [ ] Jira ticket linked properly
    
    Closes PPLWEBMYST-{issue-number}
```

## Command Reference

### Create Branch

```bash
# Create branch from issue
gh sherpa create-branch --issue JIRA-123

# Specify base branch
gh sherpa create-branch --issue JIRA-123 --base develop

# Skip confirmation prompts
gh sherpa create-branch --issue JIRA-123 --yes

# Don't fetch remotes first
gh sherpa create-branch --issue JIRA-123 --no-fetch

# Prefer hotfix naming for bugs
gh sherpa create-branch --issue JIRA-789 --prefer-hotfix

# Multiple issues
gh sherpa create-branch --issues JIRA-100,JIRA-101 --yes
```

### Create PR

```bash
# Create PR from current branch
gh sherpa create-pr --issue JIRA-123

# Skip confirmation prompts
gh sherpa create-pr --issue JIRA-123 --yes

# Create as draft
gh sherpa create-pr --issue JIRA-123 --draft

# Create as ready (not draft)
gh sherpa create-pr --issue JIRA-123 --no-draft

# Assign reviewers
gh sherpa create-pr --issue JIRA-123 --reviewers "user1,user2"

# Add labels
gh sherpa create-pr --issue JIRA-123 --labels "ready-for-review,backend"

# Set milestone
gh sherpa create-pr --issue JIRA-123 --milestone "v1.0.0"
```

### Validation

```bash
# Validate sherpa configuration
gh sherpa validate

# Check issue exists
gh sherpa check-issue JIRA-123

# Get issue details
gh sherpa get-issue JIRA-123
```

### Other Operations

```bash
# Show help
gh sherpa --help

# Show version
gh sherpa --version

# List recent branches
gh sherpa list-branches

# Show sherpa configuration
gh sherpa config show
```

## Common Workflows

### Workflow 1: Create Feature from Issue

```bash
# Step 1: Create branch with sherpa
gh sherpa create-branch --issue PPLWEBMYST-123 --base main

# Step 2: Check branch was created
git branch -a | grep feature/pplwebmyst-123

# Step 3: Create worktree
git worktree add .worktrees/feature/pplwebmyst-123 feature/pplwebmyst-123-description

# Step 4: Enter worktree
cd .worktrees/feature/pplwebmyst-123

# Step 5: Make changes...
# Step 6: Commit and push
git add .
git commit -m "Implement PPLWEBMYST-123"
git push

# Step 7: Create PR
gh sherpa create-pr --issue PPLWEBMYST-123 --yes
```

### Workflow 2: Hotfix from Production Bug

```bash
# Step 1: Create hotfix branch
gh sherpa create-branch --issue PPLWEBMYST-456 --base production --prefer-hotfix

# Step 2: Create worktree
git worktree add .worktrees/hotfix/pplwebmyst-456 hotfix/pplwebmyst-456-critical

# Step 3: Fix the bug
cd .worktrees/hotfix/pplwebmyst-456
# ... make changes ...

# Step 4: Push and create PR
git add .
git commit -m "Hotfix: PPLWEBMYST-456"
git push
gh sherpa create-pr --issue PPLWEBMYST-456 --yes

# Step 5: Merge and backport
# (via GitHub UI)

# Step 6: Clean up
cd ../..
git worktree remove .worktrees/hotfix/pplwebmyst-456
```

### Workflow 3: Multiple Related Issues

```bash
# Step 1: Create branches for all
gh sherpa create-branch --issues PPLWEBMYST-100,PPLWEBMYST-101,PPLWEBMYST-102 --yes

# Step 2: Create worktrees
git worktree add .worktrees/feature/pplwebmyst-100
git worktree add .worktrees/feature/pplwebmyst-101
git worktree add .worktrees/feature/pplwebmyst-102

# Step 3: Work in parallel
cd .worktrees/feature/pplwebmyst-100
# ... work ...

# In another terminal
cd ../pplwebmyst-101
# ... work ...

# Step 4: Create PRs
cd ..
cd ../..
gh sherpa create-pr --issue PPLWEBMYST-100 --yes
gh sherpa create-pr --issue PPLWEBMYST-101 --yes
gh sherpa create-pr --issue PPLWEBMYST-102 --yes
```

## Tips & Tricks

### Alias for Common Operations

Add to your `.bashrc` or `.zshrc`:

```bash
# Create branch and worktree in one command
alias sherpa-work='gh sherpa create-branch --yes && \
  git checkout $(git rev-parse --abbrev-ref HEAD) && \
  git worktree add .worktrees/$(git rev-parse --abbrev-ref HEAD) && \
  cd .worktrees/$(git rev-parse --abbrev-ref HEAD)'

# Quick PR creation
alias sherpa-pr='gh sherpa create-pr --yes --no-draft'

# List sherpa branches
alias sherpa-branches='git branch -a | grep -E "(feature|bugfix|hotfix|task)/"'
```

### Integration with Shell Functions

```bash
# Function: Create branch and worktree
sherpa_start() {
  if [ -z "$1" ]; then
    echo "Usage: sherpa_start ISSUE_ID"
    return 1
  fi
  
  gh sherpa create-branch --issue "$1" --yes
  BRANCH=$(git rev-parse --abbrev-ref HEAD)
  git worktree add ".worktrees/$BRANCH" "$BRANCH"
  cd ".worktrees/$BRANCH"
}

# Function: Create PR and cleanup
sherpa_finish() {
  if [ -z "$1" ]; then
    echo "Usage: sherpa_finish ISSUE_ID"
    return 1
  fi
  
  gh sherpa create-pr --issue "$1" --yes --no-draft
  cd ../..
  BRANCH=$(git rev-parse --abbrev-ref HEAD)
  git worktree remove ".worktrees/$BRANCH"
}
```

## Troubleshooting

### Issue: "gh-sherpa not found"

```bash
# Solution: Install or check path
gh extension install InditexTech/gh-sherpa

# Or update if already installed
gh extension upgrade gh-sherpa
```

### Issue: "Configuration not found"

```bash
# Sherpa looks for .sherparc.yml in repo root
# Create one or use defaults
gh sherpa config show  # Shows current config
```

### Issue: "Jira connection failed"

```bash
# Check Jira settings in .sherparc.yml
# Verify API URL and authentication
gh sherpa validate
```

### Issue: Branch naming conflicts

```bash
# If branch already exists, sherpa will ask
# Options:
# 1. Use existing branch
# 2. Create new branch with different name
# 3. Force overwrite

# To avoid: Always use --yes for automation
gh sherpa create-branch --issue ISSUE --yes
```

## Best Practices

1. **Always commit before changing branches**
   ```bash
   git add .
   git commit -m "WIP: ISSUE description"
   ```

2. **Keep .sherparc.yml in version control**
   ```bash
   git add .sherparc.yml
   git commit -m "chore: update sherpa config"
   ```

3. **Use consistent issue keys**
   - PPLWEBMYST-123 (not PPLWEBMYST123)
   - Use gh-sherpa to validate

4. **Link issues properly in commits**
   ```bash
   git commit -m "Fix: PPLWEBMYST-123 resolve authentication issue"
   ```

5. **Create PRs with gh-sherpa for automation**
   ```bash
   gh sherpa create-pr --issue PPLWEBMYST-123 --yes --no-draft
   ```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Create PR on Issue Assignment

on:
  issues:
    types: [assigned]

jobs:
  create-branch-pr:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: gh-cli-repo/gh-cli@master
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - run: |
          gh extension install InditexTech/gh-sherpa
          gh sherpa create-branch --issue "${{ github.event.issue.number }}" --yes
          gh sherpa create-pr --issue "${{ github.event.issue.number }}" --yes
```

## Reference Links

- **gh-sherpa GitHub**: https://github.com/InditexTech/gh-sherpa
- **GitHub CLI Docs**: https://cli.github.com
- **GitHub Issues API**: https://docs.github.com/en/rest/issues
