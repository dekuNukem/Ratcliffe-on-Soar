#!/bin/bash

# Check for commit message
if [[ $# -eq 0 ]]; then
    read -r -p "Enter a commit comment: " commit_message
    if [[ -z "$commit_message" ]]; then
        echo "error: commit comment cannot be empty"
        exit 1
    fi
else
    commit_message="$*"
fi

# Cleanup junk files
find . -type f -name "*.DS_Store*" -exec rm -f {} \;
find . -type f -name "*.eggs*" -exec rm -f {} \;
find . -name "__pycache__" -exec rm -rf {} \;

# Git workflow
current_branch=$(git rev-parse --abbrev-ref HEAD)

git add --all
git commit -m "$commit_message"
git push origin "$current_branch"

