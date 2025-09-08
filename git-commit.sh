#!/bin/bash

# A simple script to add, commit, and push changes.
# It takes the commit message as a single argument.

# Exit immediately if a command fails.
set -e

# Check if a commit message was provided as an argument.
if [ -z "$1" ]; then
  echo "ERROR: No commit message provided."
  echo "Usage: ./git-commit.sh \"Your commit message\""
  exit 1
fi

# 1. Add all changes to staging.
echo ">>> Staging all changes..."
git add .

# 2. Commit the changes with the provided message.
echo ">>> Committing with message: \"$1\""
git commit -m "$1"

# 3. Push the changes to the remote repository.
echo ">>> Pushing to remote..."
git push

echo "✅ Changes have been successfully pushed."