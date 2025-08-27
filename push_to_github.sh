
#!/usr/bin/env bash
set -euo pipefail
git init
git add .
git commit -m "feat: CrewAI + Celery + Redis + SQLAlchemy; fixes + README + tests"
git branch -M main
if [ -z "${1-}" ]; then
  echo "Usage: ./push_to_github.sh <repo-url>"
  exit 1
fi
git remote add origin "$1"
git push -u origin main
echo "Pushed to $1"
