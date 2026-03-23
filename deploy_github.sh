#!/bin/bash
set -e

FOLDER="$HOME/Documents/Claude Works/PhD Dashboard"
REPO="NclKgn/phd-dashboard"

echo "🚀 Déploiement du PhD Dashboard sur GitHub Pages..."
cd "$FOLDER"

# Clean up any partial .git from previous attempts
if [ -f ".git/index.lock" ]; then
  rm -f ".git/index.lock"
fi

# Init git if needed
if [ ! -d ".git" ]; then
  git init
  git branch -M main
fi

# Copy dashboard_preview.html to index.html if index.html doesn't exist
if [ ! -f "index.html" ]; then
  if [ -f "dashboard_preview.html" ]; then
    cp dashboard_preview.html index.html
    echo "✅ index.html créé depuis dashboard_preview.html"
  elif [ -f "dashboard.html" ]; then
    cp dashboard.html index.html
    echo "✅ index.html créé depuis dashboard.html"
  fi
fi

# Stage and commit
git add index.html dashboard.html dashboard_preview.html update_dashboard.py "données_phd.xlsx" 2>/dev/null || git add .
git commit -m "Initial commit — PhD Dashboard" 2>/dev/null || echo "Nothing new to commit"

# Create GitHub repo and push
if ! git remote | grep -q origin; then
  gh repo create "$REPO" --public --description "PhD Data Collection Dashboard" --source=. --remote=origin --push
else
  git push -u origin main
fi

# Enable GitHub Pages
gh api repos/$REPO/pages --method POST --field source[branch]=main --field source[path]=/ 2>/dev/null || echo "Pages already enabled or being activated..."

echo ""
echo "✅ Déploiement terminé !"
echo "🌐 Ton dashboard sera disponible dans ~60 secondes sur :"
echo "   https://nclkgn.github.io/phd-dashboard/"
