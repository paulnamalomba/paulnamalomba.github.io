# Git + GitHub CLI (gh) PowerUser Guide

<br>
**Last updated**: March 01, 2026<br>
**Author**: [Paul Namalomba](https://github.com/paulnamalomba)<br>
  - SESKA Computational Engineer<br>
  - SEAT Backend Developer<br>
  - Software Developer<br>
  - PhD Candidate (Civil Engineering Spec. Computational and Applied Mechanics)<br>
**Contact**: [kabwenzenamalomba@gmail.com](mailto:kabwenzenamalomba@gmail.com)<br>
**Website**: [paulnamalomba.github.io](https://paulnamalomba.github.io)<br>
<br>

[![CLI](https://img.shields.io/badge/SCM-Git-1f425f.svg)](https://git-scm.com/docs)
[![CLI](https://img.shields.io/badge/GitHub-CLI__gh-black.svg)](https://cli.github.com/manual/)
[![License: MIT](https://img.shields.io/badge/License-MIT-gray.svg)](https://opensource.org/licenses/MIT)

## Overview

This guide is a practical deep dive into **Git** (core version control) and **GitHub CLI (`gh`)** (GitHub automation from the terminal). It covers repository creation/deletion, local and remote repo management, authentication (HTTPS/PAT, SSH, and `gh`), professional collaboration workflows (feature branches, PRs, rebase strategies), recovery techniques (`reflog`, resets, revert), and **CLI-driven deployments** (Git push deployments, remote servers via bare repos/hooks, and GitHub Actions triggered and operated via `gh`).

## Contents

- [Git + GitHub CLI (gh) PowerUser Guide](#git--github-cli-gh-poweruser-guide)
  - [Overview](#overview)
  - [Contents](#contents)
  - [Quickstart](#quickstart)
  - [1. Installation (Windows, Linux, macOS)](#1-installation-windows-linux-macos)
    - [Git](#git)
    - [GitHub CLI (`gh`)](#github-cli-gh)
  - [2. Identity, Config, and Safety Defaults](#2-identity-config-and-safety-defaults)
    - [Set user identity (global)](#set-user-identity-global)
    - [Useful global defaults](#useful-global-defaults)
    - [Line endings (Windows vs Linux)](#line-endings-windows-vs-linux)
    - [Quality-of-life aliases (optional)](#quality-of-life-aliases-optional)
  - [3. Authentication (Git HTTPS/PAT, SSH, and gh)](#3-authentication-git-httpspat-ssh-and-gh)
    - [3.1 Git over HTTPS (PAT) + Credential Manager](#31-git-over-https-pat--credential-manager)
    - [3.2 Git over SSH (recommended for power users)](#32-git-over-ssh-recommended-for-power-users)
    - [3.3 GitHub CLI authentication](#33-github-cli-authentication)
  - [4. Repository Lifecycle (Create, Clone, Delete, Archive)](#4-repository-lifecycle-create-clone-delete-archive)
    - [4.1 Create a local repo](#41-create-a-local-repo)
    - [4.2 Clone an existing repo](#42-clone-an-existing-repo)
    - [4.3 Create a GitHub repo from the terminal (gh)](#43-create-a-github-repo-from-the-terminal-gh)
    - [4.4 Rename a GitHub repo (gh)](#44-rename-a-github-repo-gh)
    - [4.5 Archive vs Delete (be deliberate)](#45-archive-vs-delete-be-deliberate)
  - [5. Daily Git Workflow (Add/Commit/Log/Diff)](#5-daily-git-workflow-addcommitlogdiff)
    - [5.1 Inspect state](#51-inspect-state)
    - [5.2 Stage changes](#52-stage-changes)
    - [5.3 Commit](#53-commit)
    - [5.4 View history](#54-view-history)
    - [5.5 Compare changes](#55-compare-changes)
    - [5.6 File operations (tracked content)](#56-file-operations-tracked-content)
    - [5.7 Ignore rules (.gitignore) and debugging ignores](#57-ignore-rules-gitignore-and-debugging-ignores)
  - [6. Branching and Integration (Merge, Rebase, Cherry-pick)](#6-branching-and-integration-merge-rebase-cherry-pick)
    - [6.1 Branch basics](#61-branch-basics)
    - [6.2 Merge (preserves branch topology)](#62-merge-preserves-branch-topology)
    - [6.3 Rebase (rewrites history; keep it disciplined)](#63-rebase-rewrites-history-keep-it-disciplined)
    - [6.4 Cherry-pick (copy a commit)](#64-cherry-pick-copy-a-commit)
    - [6.5 Resolve conflicts efficiently](#65-resolve-conflicts-efficiently)
  - [7. Undo, Recovery, and Forensics (Restore, Reset, Reflog)](#7-undo-recovery-and-forensics-restore-reset-reflog)
    - [7.1 Discard local file edits](#71-discard-local-file-edits)
    - [7.2 Reset (moves branch pointer; can be destructive)](#72-reset-moves-branch-pointer-can-be-destructive)
    - [7.3 Revert (safe for shared branches)](#73-revert-safe-for-shared-branches)
    - [7.4 Reflog (time machine)](#74-reflog-time-machine)
    - [7.5 Investigate who changed what](#75-investigate-who-changed-what)
    - [7.6 Stash (parking local changes)](#76-stash-parking-local-changes)
    - [7.7 Clean (remove untracked files/directories)](#77-clean-remove-untracked-filesdirectories)
  - [8. Remotes and Collaboration (Fetch/Pull/Push, Forks, Upstream)](#8-remotes-and-collaboration-fetchpullpush-forks-upstream)
    - [8.1 Remotes](#81-remotes)
    - [8.2 Fetch vs Pull](#82-fetch-vs-pull)
    - [8.3 Fork workflow](#83-fork-workflow)
  - [9. Tags, Releases, and Versioning](#9-tags-releases-and-versioning)
    - [9.1 Tags](#91-tags)
    - [9.2 GitHub releases (gh)](#92-github-releases-gh)
  - [10. Advanced Git (Worktrees, Submodules, Sparse Checkout, Bisect)](#10-advanced-git-worktrees-submodules-sparse-checkout-bisect)
    - [10.1 Worktrees (multiple branches, one clone)](#101-worktrees-multiple-branches-one-clone)
    - [10.2 Submodules (use only if necessary)](#102-submodules-use-only-if-necessary)
    - [10.3 Sparse checkout (huge monorepos)](#103-sparse-checkout-huge-monorepos)
    - [10.4 Bisect (find the commit that broke something)](#104-bisect-find-the-commit-that-broke-something)
    - [10.5 Rewrite history (danger zone)](#105-rewrite-history-danger-zone)
    - [10.6 Hooks (local automation)](#106-hooks-local-automation)
    - [10.7 Git LFS (large files)](#107-git-lfs-large-files)
  - [11. GitHub CLI (gh) Deep Dive (repo, pr, issue, api, workflow)](#11-github-cli-gh-deep-dive-repo-pr-issue-api-workflow)
    - [11.1 Repo operations](#111-repo-operations)
    - [11.2 Pull Requests](#112-pull-requests)
    - [11.3 Issues](#113-issues)
    - [11.4 Workflows and runs (GitHub Actions)](#114-workflows-and-runs-github-actions)
    - [11.5 Secrets and variables (for CI/CD)](#115-secrets-and-variables-for-cicd)
    - [11.6 `gh api` (advanced automation)](#116-gh-api-advanced-automation)
    - [11.7 Aliases and extensions](#117-aliases-and-extensions)
  - [12. CLI-Driven Deployment (Git Push, Remote Hooks, GitHub Actions)](#12-cli-driven-deployment-git-push-remote-hooks-github-actions)
    - [12.1 Push-to-deploy via GitHub Actions (operate with gh)](#121-push-to-deploy-via-github-actions-operate-with-gh)
    - [12.2 Tag-driven releases and deployments](#122-tag-driven-releases-and-deployments)
    - [12.3 Remote server deployment using a bare repo + hook](#123-remote-server-deployment-using-a-bare-repo--hook)
    - [12.4 Remote deployment key management (GitHub + servers)](#124-remote-deployment-key-management-github--servers)
  - [13. Security and Governance](#13-security-and-governance)
    - [Avoid committing secrets](#avoid-committing-secrets)
    - [Signed commits (optional)](#signed-commits-optional)
    - [Least privilege](#least-privilege)
  - [14. Troubleshooting](#14-troubleshooting)
    - [Credentials keep failing](#credentials-keep-failing)
    - [Detached HEAD](#detached-head)
    - [“non-fast-forward” push rejected](#non-fast-forward-push-rejected)
    - [Accidental `git reset --hard`](#accidental-git-reset---hard)
  - [References and Further Reading](#references-and-further-reading)

---

## Quickstart

Minimal end-to-end flow: authenticate, create repo, commit, push, open PR.

```bash
# 1) Authenticate to GitHub
gh auth login
gh auth status

# 2) Create a new repo on GitHub and clone it
gh repo create OWNER/new-repo --public --clone
cd new-repo

# 3) First commit
echo "# new-repo" > README.md
git add -A
git commit -m "Initial commit"
git push -u origin main

# 4) Create a feature branch + PR
git switch -c feature/demo
echo "More content" >> README.md
git add -A
git commit -m "Update README"
git push -u origin feature/demo

gh pr create
```

## 1. Installation (Windows, Linux, macOS)

### Git

**Windows (recommended: Git for Windows + Git Credential Manager)**

```powershell
winget install --id Git.Git -e
# Optional: verify
git --version
```

**macOS**

```bash
brew install git
git --version
```

**Ubuntu/Debian**

```bash
sudo apt update
sudo apt install -y git
git --version
```

### GitHub CLI (`gh`)

**Windows**

```powershell
winget install --id GitHub.cli -e
gh --version
```

**macOS**

```bash
brew install gh
gh --version
```

**Ubuntu/Debian** (many distros package `gh`; use official instructions if you need latest)

```bash
sudo apt update
sudo apt install -y gh
gh --version
```

---

## 2. Identity, Config, and Safety Defaults

### Set user identity (global)

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

### Useful global defaults

```bash
# Use a modern default branch name (optional)
git config --global init.defaultBranch main

# Better push behavior
git config --global push.default simple

# Rebase-aware pulls (common in professional repos)
git config --global pull.rebase true

# Auto-stash local changes during rebase pulls
git config --global rebase.autoStash true

# Prune stale remote branches on fetch
git config --global fetch.prune true

# Make conflict resolution less painful
git config --global rerere.enabled true
```

Inspect config sources (useful for debugging surprises):

```bash
git config --list --show-origin
```

### Line endings (Windows vs Linux)

If you collaborate cross-platform, decide on a policy and enforce it:

**Windows typical**

```bash
# Converts CRLF <-> LF automatically (works for many repos, but be consistent)
git config --global core.autocrlf true
```

**Linux/macOS typical**

```bash
git config --global core.autocrlf input
```

If the repo already has a `.gitattributes`, follow the repo policy (repo settings should win over personal preference).

### Quality-of-life aliases (optional)

```bash
git config --global alias.s "status -sb"
git config --global alias.l "log --oneline --decorate --graph --all"
git config --global alias.d "diff"
git config --global alias.co "checkout"
```

---

## 3. Authentication (Git HTTPS/PAT, SSH, and gh)

You have two separate concepts:

- **Git transport auth** (push/pull): HTTPS (PAT) or SSH
- **GitHub API auth** (issues, PRs, actions): `gh auth`

### 3.1 Git over HTTPS (PAT) + Credential Manager

GitHub no longer supports password auth for Git operations. Use:

- Personal Access Token (PAT)
- Git Credential Manager (recommended on Windows)

When using HTTPS remotes like:

```bash
git remote -v
# https://github.com/OWNER/REPO.git
```

Git will prompt for credentials; use:

- Username: your GitHub username
- Password: your PAT

To inspect credential helper:

```bash
git config --global credential.helper
```

### 3.2 Git over SSH (recommended for power users)

**Generate an SSH key**

```bash
ssh-keygen -t ed25519 -C "you@example.com"
# Press enter for default path; set a passphrase
```

**Start ssh-agent and add key**

Linux/macOS:

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

Windows (PowerShell):

```powershell
Get-Service ssh-agent | Set-Service -StartupType Automatic
Start-Service ssh-agent
ssh-add $env:USERPROFILE\.ssh\id_ed25519
```

**Add public key to GitHub**

```bash
cat ~/.ssh/id_ed25519.pub
```

Copy into GitHub: Settings → SSH and GPG keys.

**Use SSH remote**

```bash
git remote set-url origin git@github.com:OWNER/REPO.git
ssh -T git@github.com
```

### 3.3 GitHub CLI authentication

**Login**

```bash
gh auth login
```

Explicit login patterns:

```bash
# Prefer SSH for Git operations
gh auth login -p ssh

# Authenticate to a specific host (GitHub Enterprise Server)
gh auth login --hostname github.company.com
```

Configure Git to use your `gh` auth for HTTPS operations (optional):

```bash
gh auth setup-git
```

**Status + active account**

```bash
gh auth status
```

**Logout**

```bash
gh auth logout
```

Refresh scopes/token (useful if Actions/Packages commands fail):

```bash
gh auth refresh
```

Print the active token (avoid pasting this into logs):

```bash
gh auth token
```

**Select default protocol for Git operations**

```bash
gh config set git_protocol ssh
# or
gh config set git_protocol https
```

---

## 4. Repository Lifecycle (Create, Clone, Delete, Archive)

### 4.1 Create a local repo

```bash
mkdir my-repo
cd my-repo
git init
```

### 4.2 Clone an existing repo

```bash
git clone https://github.com/OWNER/REPO.git
# or
git clone git@github.com:OWNER/REPO.git
```

### 4.3 Create a GitHub repo from the terminal (gh)

Create and optionally push the current directory:

```bash
# inside an existing local repo
gh repo create OWNER/REPO --private --source=. --remote=origin --push
```

Create a new repo and clone it:

```bash
gh repo create OWNER/new-repo --public --clone
```

### 4.4 Rename a GitHub repo (gh)

```bash
gh repo rename new-name
```

Fork a repo (and clone your fork):

```bash
gh repo fork OWNER/REPO --clone
```

Create from a template repo:

```bash
gh repo create OWNER/new-from-template --private --template OWNER/TEMPLATE_REPO --clone
```

### 4.5 Archive vs Delete (be deliberate)

**Archive (reversible, safer)**

```bash
gh repo archive OWNER/REPO
```

**Delete (irreversible)**

Before deletion, consider taking a mirror backup:

```bash
git clone --mirror git@github.com:OWNER/REPO.git
# Produces REPO.git directory with full refs
```

Then delete:

```bash
gh repo delete OWNER/REPO --confirm
```

---

## 5. Daily Git Workflow (Add/Commit/Log/Diff)

### 5.1 Inspect state

```bash
git status
```

### 5.2 Stage changes

```bash
# stage all tracked edits + new files
git add -A

# stage interactively (power tool)
git add -p
```

### 5.3 Commit

```bash
git commit -m "Explain what changed"
```

Amend the last commit (common for small fixes):

```bash
git commit --amend
```

Create a fixup commit (pairs well with `git rebase -i --autosquash`):

```bash
git commit --fixup <commit_sha>
```

Commit with editor message:

```bash
git commit
```

### 5.4 View history

```bash
git log

git log --oneline --decorate --graph --all
```

### 5.5 Compare changes

```bash
# unstaged differences
git diff

# staged differences
git diff --staged

# compare two refs
git diff main..feature-branch
```

### 5.6 File operations (tracked content)

Rename/move a file:

```bash
git mv oldname newname
```

Remove a tracked file:

```bash
git rm path/to/file
```

### 5.7 Ignore rules (.gitignore) and debugging ignores

Add patterns to `.gitignore` to prevent files being tracked.

Debug why a path is ignored:

```bash
git check-ignore -v path/to/file
```

---

## 6. Branching and Integration (Merge, Rebase, Cherry-pick)

### 6.1 Branch basics

```bash
git branch

git switch -c feature/login
# or (older)
# git checkout -b feature/login
```

Push a new branch to origin:

```bash
git push -u origin feature/login
```

Delete branches:

```bash
# local
git branch -d feature/login
# force delete local (unmerged)
git branch -D feature/login

# remote
git push origin --delete feature/login
```

### 6.2 Merge (preserves branch topology)

```bash
git switch main
git pull

git merge feature/login
```

### 6.3 Rebase (rewrites history; keep it disciplined)

Common workflow: keep your feature branch updated on top of `main`.

```bash
git switch feature/login
git fetch origin
git rebase origin/main
```

Interactive rebase (squash / reorder / edit messages):

```bash
git rebase -i origin/main
```

If you already pushed and you rebase, you will need a force push:

```bash
git push --force-with-lease
```

`--force-with-lease` is safer than `--force` because it refuses to overwrite someone else’s new pushes.

### 6.4 Cherry-pick (copy a commit)

```bash
# apply a specific commit onto current branch
git cherry-pick <commit_sha>
```

### 6.5 Resolve conflicts efficiently

When a conflict happens:

```bash
git status
# edit files to resolve

git add -A
# if in merge
git commit
# if in rebase
git rebase --continue
```

Abort a rebase if needed:

```bash
git rebase --abort
```

---

## 7. Undo, Recovery, and Forensics (Restore, Reset, Reflog)

These are the commands that differentiate beginners from professionals.

### 7.1 Discard local file edits

Discard unstaged edits for a file:

```bash
git restore path/to/file
```

Unstage (move from index back to working tree):

```bash
git restore --staged path/to/file
```

Restore a file from a specific commit:

```bash
git restore --source <commit_sha> -- path/to/file
```

### 7.2 Reset (moves branch pointer; can be destructive)

Think of `reset` as: **move `HEAD` to a different commit**, optionally changing index/worktree.

```bash
# keep changes staged (rare)
git reset --soft HEAD~1

# keep changes unstaged (common)
git reset --mixed HEAD~1

# discard changes completely (danger)
git reset --hard HEAD~1
```

### 7.3 Revert (safe for shared branches)

Revert creates a new commit that undoes changes (no history rewrite):

```bash
git revert <commit_sha>
```

### 7.4 Reflog (time machine)

If you “lost” commits after a reset/rebase, reflog usually saves you:

```bash
git reflog
# find the previous HEAD state

git reset --hard HEAD@{1}
```

### 7.5 Investigate who changed what

```bash
# who changed each line
git blame path/to/file

# find commit that introduced a string
git log -S "some text" -- path/to/file
```

### 7.6 Stash (parking local changes)

Stash tracked changes:

```bash
git stash push -m "wip"
git stash list
git stash pop
```

Include untracked files:

```bash
git stash push -u -m "wip + untracked"
```

Apply a specific stash without dropping it:

```bash
git stash apply stash@{1}
```

### 7.7 Clean (remove untracked files/directories)

Preview what would be removed:

```bash
git clean -nd
```

Remove untracked files + directories:

```bash
git clean -fd
```

---

## 8. Remotes and Collaboration (Fetch/Pull/Push, Forks, Upstream)

### 8.1 Remotes

```bash
git remote -v # list remotes and URLs

git remote add origin git@github.com:OWNER/REPO.git # add a remote named "origin"

git remote add upstream git@github.com:UPSTREAM_OWNER/REPO.git # if you forked and want to track the main repo

git remote set-url origin git@github.com:OWNER/REPO.git # change URL of origin
```

Rename a remote:

```bash
git remote rename origin github
```

Remove a remote:

```bash
git remote remove upstream
```

Prune deleted remote branches:

```bash
git fetch --prune
```

### 8.2 Fetch vs Pull

- `git fetch`: update your view of the remote; does not change your working files
- `git pull`: fetch + integrate (merge or rebase depending on config)

```bash
git fetch origin # get latest from origin, but stay on current branch

git pull # implicitly does fetch + merge/rebase based on config

git pull --rebase # explicitly
```

### 8.3 Fork workflow

When working on a fork:

- `origin`: your fork
- `upstream`: the main repository

```bash
git fetch upstream # get latest from main repo

git switch main # or master, depending on default branch name

git merge upstream/main # or rebase if you prefer a cleaner history

git rebase upstream/main # or keep your commits on top of the latest main

git push origin main # update your fork's main branch
```

---

## 9. Tags, Releases, and Versioning

### 9.1 Tags

Lightweight tag:

```bash
git tag v1.2.3
```

Annotated tag (recommended):

```bash
git tag -a v1.2.3 -m "Release v1.2.3"
```

Push tags:

```bash
git push --tags # pushes all tags

git push origin v1.2.3 # push a specific tag
```

Describe the current commit using the nearest tag:

```bash
git describe --tags --always
```

### 9.2 GitHub releases (gh)

Create a release (can upload assets too):

```bash
gh release create v1.2.3 --title "v1.2.3" --notes "Key changes..."
```

List releases:

```bash
gh release list
```

Upload an asset:

```bash
gh release upload v1.2.3 ./dist/app.zip
```

Download release assets:

```bash
gh release download v1.2.3
```

---

## 10. Advanced Git (Worktrees, Submodules, Sparse Checkout, Bisect)

### 10.1 Worktrees (multiple branches, one clone)

Worktrees let you check out multiple branches in parallel without stashing:

```bash
git worktree add ../my-repo-hotfix hotfix/urgent # from repo root

git worktree list # list worktrees

git worktree remove ../my-repo-hotfix # remove when done
```

### 10.2 Submodules (use only if necessary)

Add a submodule:

```bash
git submodule add git@github.com:OWNER/dep-repo.git deps/dep-repo
```

Clone repo with submodules:

```bash
git clone --recurse-submodules git@github.com:OWNER/REPO.git
```

Update submodules:

```bash
git submodule update --init --recursive
```

### 10.3 Sparse checkout (huge monorepos)

```bash
git clone --filter=blob:none --no-checkout git@github.com:OWNER/REPO.git
cd REPO

git sparse-checkout init --cone # use cone mode for simple directory patterns
git sparse-checkout set path/to/subdir another/subdir #

git checkout # checkout the default branch with only the specified paths
```

### 10.4 Bisect (find the commit that broke something)

```bash
git bisect start # start bisect session
git bisect bad # (HEAD is bad; the bug is present here)

git bisect good <good_commit_sha> # choose a known good commit

git bisect reset # end bisect session and return to original HEAD when finished
```

### 10.5 Rewrite history (danger zone)

Use history rewriting only when you understand the consequences.

- For local cleanups: `git rebase -i`
- For removing large files/secrets from history: prefer `git filter-repo` (external tool) over `filter-branch`

### 10.6 Hooks (local automation)

Hooks run scripts at certain points (`pre-commit`, `commit-msg`, `pre-push`). Common uses:

- Format/lint before committing
- Block committing secrets
- Enforce commit message rules

Local hooks live in `.git/hooks/` by default. To share hooks across a team, store them in the repo and set a hooks path:

```bash
git config core.hooksPath .githooks
```

### 10.7 Git LFS (large files)

If you must version large binaries (datasets, PSDs, large media), use Git LFS instead of bloating normal Git history.

```bash
git lfs install # one-time install per machine (requires git-lfs installed)

# below: track patterns (writes to .gitattributes)
git lfs track "*.psd"
git lfs track "*.mp4"

# below: add to gitattributes and commit
git add .gitattributes
git commit -m "Configure Git LFS"
```

---

## 11. GitHub CLI (gh) Deep Dive (repo, pr, issue, api, workflow)

### 11.1 Repo operations

```bash
gh repo view --web # view repo in browser

gh repo clone OWNER/REPO # clone via gh (uses your auth settings)

gh repo list --limit 50 # list your repos

gh repo sync OWNER/FORK_REPO # sync a fork from upstream (default branch)
```

### 11.2 Pull Requests

```bash
gh pr create # create PR from current branch

gh pr list # list PRs

gh pr view 123 # view PR details

gh pr checkout 123 # checkout a PR locally

gh pr merge 123 # merge a PR (respects repo settings)
```

Review a PR:

```bash
gh pr review 123 --approve

# or request changes
# gh pr review 123 --request-changes -b "Reason..."
```

See PR status for your branches:

```bash
gh pr status
```

### 11.3 Issues

```bash
gh issue create # create a new issue interactively

gh issue list # list issues

gh issue view 42 # view issue details
```

### 11.4 Workflows and runs (GitHub Actions)

List workflows:

```bash
gh workflow list
```

View a workflow definition:

```bash
gh workflow view "Deploy" --yaml
```

Run a workflow manually (workflow_dispatch):

```bash
gh workflow run "Deploy" -f environment=prod
```

Watch runs:

```bash
gh run list --limit 20

gh run watch

# or view a specific run
gh run view <run_id> --log
```

Re-run a failed workflow:

```bash
gh run rerun <run_id>
```

Cancel a run:

```bash
gh run cancel <run_id>
```

### 11.5 Secrets and variables (for CI/CD)

Set a repository secret:

```bash
# reads from stdin
printf "%s" "MY_SECRET_VALUE" | gh secret set MY_SECRET
```

List secrets:

```bash
gh secret list
```

Set an Actions variable:

```bash
printf "%s" "staging" | gh variable set DEPLOY_ENV
```

List variables:

```bash
gh variable list
```

### 11.6 `gh api` (advanced automation)

When `gh` doesn’t have a subcommand, `gh api` gives you raw GitHub API access.

Example: list repo webhooks:

```bash
gh api repos/OWNER/REPO/hooks
```

Example: create a label:

```bash
gh api repos/OWNER/REPO/labels -f name="priority:high" -f color="B60205"
```

### 11.7 Aliases and extensions

Aliases:

```bash
gh alias set prs "pr list --limit 50"
```

Extensions (install community tooling):

```bash
gh extension list
# gh extension install OWNER/EXTENSION
```

---

## 12. CLI-Driven Deployment (Git Push, Remote Hooks, GitHub Actions)

Deployment is usually one of these patterns:

1. **Git push triggers CI/CD** (GitHub Actions, GitLab CI, etc.)
2. **Git push deploys to a platform remote** (some PaaS patterns)
3. **Git push to a server bare repo** + `post-receive` hook

### 12.1 Push-to-deploy via GitHub Actions (operate with gh)

Typical flow:

- You push to `main` or a tag
- GitHub Actions deploy workflow runs
- You observe, re-run, and troubleshoot with `gh`

```bash
# push code
git push origin main

# view runs
gh run list --limit 10

# watch logs
gh run watch
```

Manual deployment trigger:

```bash
gh workflow run "Deploy" -f environment=staging
```

### 12.2 Tag-driven releases and deployments

Many production systems deploy only from version tags.

```bash
# create + push a tag
git tag -a v2.0.0 -m "Release v2.0.0"
git push origin v2.0.0

# create a GitHub release
gh release create v2.0.0 --title "v2.0.0" --generate-notes
```

### 12.3 Remote server deployment using a bare repo + hook

This is the classic **"git push production"** pattern.

**On the server (Linux)**

Create a dedicated deploy user and a bare repo:

```bash
sudo adduser --disabled-password deploy

sudo mkdir -p /srv/git
sudo chown deploy:deploy /srv/git

sudo -u deploy git init --bare /srv/git/myapp.git
```

Create a working tree path:

```bash
sudo mkdir -p /var/www/myapp
sudo chown deploy:deploy /var/www/myapp
```

Add a `post-receive` hook to deploy on push:

```bash
sudo -u deploy nano /srv/git/myapp.git/hooks/post-receive
```

Hook example (minimal):

```bash
#!/bin/sh
set -eu

BRANCH="refs/heads/main"

while read oldrev newrev refname
do
  if [ "$refname" = "$BRANCH" ]; then
    GIT_WORK_TREE=/var/www/myapp git --git-dir=/srv/git/myapp.git checkout -f main

    # Example: restart a service
    # systemctl restart myapp.service
  fi
done
```

Make it executable:

```bash
sudo -u deploy chmod +x /srv/git/myapp.git/hooks/post-receive
```

**On your local machine**

Add a remote and push:

```bash
git remote add production deploy@YOUR_SERVER:/srv/git/myapp.git

git push production main
```

Notes:

- This is intentionally minimal. In production, you typically add build steps, atomic deploy directories, and rollbacks.
- You must manage permissions carefully (deploy user, SSH keys, and service restart permissions).

### 12.4 Remote deployment key management (GitHub + servers)

Common pattern:

- Use SSH deploy keys (server-only key)
- Store tokens/keys as GitHub secrets

Use `gh secret set` for CI/CD secrets:

```bash
printf "%s" "ssh-private-key-material" | gh secret set DEPLOY_SSH_KEY
```

---

## 13. Security and Governance

### Avoid committing secrets

- Add secrets to `.gitignore`
- Rotate any secret that accidentally hit Git history
- Use environment variables and secret stores in CI/CD

Quick checks:

```bash
# scan tracked files for suspicious strings
git grep -n "BEGIN RSA PRIVATE KEY" || true
git grep -n "AKIA" || true
```

### Signed commits (optional)

Modern Git can sign commits/tags using either GPG or SSH signing, depending on your setup.

General idea:

- generate signing key
- configure Git to sign
- verify on GitHub

Example: SSH-based commit signing (modern approach):

```bash
# Tell Git to use SSH keys for signing
git config --global gpg.format ssh

# Use your SSH public key as the signing key
git config --global user.signingkey ~/.ssh/id_ed25519.pub

# Sign commits by default
git config --global commit.gpgsign true

# Make a signed commit
git commit -S -m "Signed commit"
```

To get the “Verified” badge on GitHub, add the same public key under GitHub Settings → SSH and GPG keys.

### Least privilege

- Use fine-grained PATs where possible
- Use SSH keys with passphrases
- Restrict secrets to environments (staging/prod) and to protected branches

---

## 14. Troubleshooting

### Credentials keep failing

- Check `gh auth status`
- Ensure remote URL matches the intended auth method (`https://` vs `git@github.com:`)

```bash
git remote -v

gh auth status
```

### Detached HEAD

You checked out a commit directly. Create a branch to keep work:

```bash
git switch -c fix/detached
```

### “non-fast-forward” push rejected

You’re behind the remote:

```bash
git fetch origin
git rebase origin/main
# or merge
# git merge origin/main

git push
```

### Accidental `git reset --hard`

Try reflog recovery:

```bash
git reflog
# find old HEAD
git reset --hard <sha>
```

---

## References and Further Reading

- Git documentation: https://git-scm.com/docs
- Pro Git book (free): https://git-scm.com/book/en/v2
- GitHub CLI manual: https://cli.github.com/manual/
- GitHub docs (auth, SSH, PAT): https://docs.github.com/
