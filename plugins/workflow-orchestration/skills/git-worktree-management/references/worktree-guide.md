# Git Worktrees Guide

## What are Git Worktrees?

Git worktrees allow you to have multiple branches checked out at the same time in different directories. This is especially useful for:
- Working on multiple features/fixes simultaneously
- Keeping your main worktree clean
- Testing one feature while developing another
- Running builds/tests without switching branches

### Benefits

- **Parallelization**: Work on multiple issues without context switching
- **Clean separation**: Each branch in its own directory
- **Shared repository**: All worktrees share the same git history
- **Independent changes**: Changes in one worktree don't affect others until pushed
- **Efficient**: Uses hard links (minimal disk space overhead)

## Worktree Workflow

```
Main Repository (.git directory)
│
├─ Main Branch (primary worktree - auto-created)
│  └─ .git (shared reference)
│
└─ .worktrees/ (directory for additional worktrees)
   ├─ feature/JIRA-100-...
   ├─ feature/JIRA-101-...
   └─ hotfix/JIRA-102-...
```

Each worktree has its own:
- Working directory files
- Index (staging area)
- HEAD reference
- Local branches (shared refs)

But all share:
- Object database (.git/objects)
- Git configuration
- Remote tracking branches

## Common Worktree Operations

### List Worktrees

```bash
git worktree list
git worktree list --porcelain  # Machine-readable format
```

Shows all active worktrees with their paths and branches.

### Add Worktree

```bash
# Create new worktree with existing branch
git worktree add .worktrees/my-feature-name my-feature-branch

# Create worktree and new branch
git worktree add -b feature/new-thing .worktrees/feature-new

# From commit hash
git worktree add .worktrees/from-commit abc123
```

### Remove Worktree

```bash
# Remove worktree
git worktree remove .worktrees/my-feature

# Force remove (if locked)
git worktree remove --force .worktrees/my-feature

# Prune references to removed worktrees
git worktree prune
```

### Repair Worktrees

```bash
# Fix worktree lock issues
git worktree repair

# Check worktree status
git worktree list --verbose
```

## Worktree Directory Structure

```
project-root/
├─ .git/                     # Main git directory (shared)
├─ .gitignore
├─ src/
├─ package.json
└─ .worktrees/              # Convention for secondary worktrees
   ├─ feature-branch-1/
   │  ├─ src/
   │  ├─ package.json
   │  └─ .git (symbolic link to main .git)
   └─ feature-branch-2/
      ├─ src/
      ├─ package.json
      └─ .git (symbolic link to main .git)
```

## Worktree Best Practices

### 1. Consistent Naming
Use a clear naming convention:
```
.worktrees/feature-jira-123-description
.worktrees/bugfix-jira-456-description
.worktrees/hotfix-critical-issue
```

### 2. Organize by Type
```
.worktrees/
├─ features/
│  └─ jira-123-...
├─ bugfixes/
│  └─ jira-456-...
└─ hotfixes/
   └─ critical-...
```

### 3. Clean Up Regularly
Remove worktrees after merging:
```bash
cd ..
git worktree remove .worktrees/finished-feature
```

### 4. Avoid Uncommitted Changes
Before removing a worktree:
```bash
cd .worktrees/my-branch
git status  # Check for uncommitted changes
git add .
git commit -m "Work in progress"
git push
```

### 5. Switch Between Worktrees
```bash
# From any worktree, navigate to another
cd ../../.worktrees/other-feature
```

## Potential Issues & Solutions

### Issue: Locked Worktree
**Problem**: "worktree is locked"

**Solution**:
```bash
# Remove the lock file
rm .worktrees/branch-name/.git/locked

# Or repair
git worktree repair
```

### Issue: Worktree in Detached State
**Problem**: Git doesn't track which branch the worktree is on

**Solution**:
```bash
cd .worktrees/problem-worktree
git checkout branch-name
```

### Issue: Can't Remove Worktree
**Problem**: Permission denied or "Git is using it"

**Solution**:
```bash
# Force remove
git worktree remove --force .worktrees/stubborn-branch

# Or manually
rm -rf .worktrees/stubborn-branch
```

### Issue: Unclean Worktree
**Problem**: Uncommitted changes prevent switching

**Solution**:
```bash
cd .worktrees/dirty-branch

# Option 1: Commit and push
git add .
git commit -m "Save work"
git push

# Option 2: Stash
git stash
git stash push -u  # Include untracked files
```

## Integration with gh-sherpa

`gh-sherpa` is a GitHub CLI extension that automates branch creation with naming conventions based on issue type.

### Sherpa Commands

```bash
# Create branch automatically (handles naming)
gh sherpa create-branch --issue JIRA-123 --base main --yes

# Create PR from branch
gh sherpa create-pr --issue JIRA-123 --yes --no-draft

# Handle multiple issues
gh sherpa create-branch --issues JIRA-123,JIRA-124 --yes
```

### Naming Conventions (Sherpa)

Sherpa automatically names branches based on issue type:

| Issue Type | Example Branch Name |
|-----------|-------------------|
| Feature/Story | `feature/JIRA-123-description` |
| Bug | `bugfix/JIRA-456-description` |
| Hotfix | `hotfix/JIRA-789-critical` |
| Chore | `chore/JIRA-999-cleanup` |
| Task | `task/JIRA-111-implement` |

### Sherpa + Worktrees Workflow

```bash
# 1. Create branch with sherpa (in main repo)
gh sherpa create-branch --issue JIRA-123 --yes

# 2. Check out newly created branch
git checkout feature/jira-123-description

# 3. Create worktree with that branch
git worktree add .worktrees/feature/jira-123-description

# 4. Enter worktree
cd .worktrees/feature/jira-123-description

# 5. Do work...
# Edit files, commit, push

# 6. Create PR with sherpa
gh sherpa create-pr --issue JIRA-123 --yes

# 7. Back to main repo, clean up
cd ../..
git worktree remove .worktrees/feature/jira-123-description
```

## Worktree Maintenance

### Regular Cleanup
```bash
# Remove all finished worktrees
git worktree list | grep finished
git worktree remove .worktrees/finished-*

# Prune stale references
git worktree prune
git gc --aggressive
```

### Monitor Worktrees
```bash
# Keep tabs on active work
watch -n5 'git worktree list --verbose'
```

### Backup Worktree
```bash
# Before risky operations
cp -r .worktrees/my-work .worktrees/my-work-backup
```

## Performance Considerations

### Disk Usage
- Initial worktree: ~200MB (with node_modules or dependencies)
- Additional worktrees: ~50-100MB each (hard links to shared objects)
- Use `.gitignore` to exclude heavy dependencies

### Build Performance
- Each worktree has independent node_modules/build artifacts
- Run builds in parallel across worktrees
- Consider using monorepo caching

### Network
- Shared remote tracking branches (no extra fetches needed per worktree)
- Push/pull from any worktree affects shared state
- Keep worktrees in sync with `git fetch origin`

## Integration with Development Workflow

### Pre-Commit Hooks
Located in `.git/hooks` (shared by all worktrees):
```bash
# Edit .git/hooks/pre-commit
#!/bin/bash
npm run lint
npm test
```

### Commit Message Templates
Shared `.gitcommitmsg` template:
```
git config commit.template .gitcommitmsg
```

### Aliases for Worktree Operations
```bash
# In .git/config
[alias]
    wt-list = worktree list --verbose
    wt-add = worktree add .worktrees
    wt-rm = worktree remove --force
    wt-clean = "!git worktree list | grep detached | awk '{print $1}' | xargs -I {} git worktree remove {}"
```

## Worktree vs Feature Branches

| Aspect | Worktree | Feature Branch |
|--------|----------|---|
| Can work on multiple at once | ✓ Yes | ✗ No (need to switch) |
| Disk usage | More | Less |
| Setup complexity | Medium | Low |
| Good for large features | ✓ Yes | ✗ Switching slow |
| Good for quick fixes | ✓ Yes | ✓ Yes |
| Team collaboration | Moderate | Excellent |

**Use worktrees when**: Heavy development, long-running features, parallel work  
**Use branches when**: Light changes, small team, limited disk space
