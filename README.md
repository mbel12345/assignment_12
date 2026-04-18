# Repos
Github: https://github.com/mbel12345/assignment_12/
Dockerhub: https://hub.docker.com/r/msb64/assignment_12

# Project Setup

## Set up Repo
In Github:
Create new repo called assignment_12 and make sure it is public

In WSL/VS Code Terminal:
```bash
mkdir assignment_12
cd assignment_12/
git init
git branch -m main
git remote add origin git@github.com:mbel12345/assignment_12.git
vim README.md
git add . -v
git commit -m "Initial commit"
git push -u origin main
```

## Set up virtual environment
In WSL/VS Code Terminal:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Build image and start container
Note: This must be already running for all local testing
In WSL/VS Code Terminal:
```bash
docker compose up --build
```

## Run test cases locally

In second WSL/VS Code Terminal:
```bash
pytest
```

## Configure Github Actions
Github Actions will run on any pushes or pull requests. Only pull requests will result in the deployment step.
Pre-requisite: In Dockerhub, create an Access Token, then add it to Environment var "DOCKERHUB_TOKEN" in GitHub. Add DOCKERHUB_USERNAME also.

Add these environment variables in Github:
  - POSTGRES_USER = postgres
  - POSTGRES_PASSWORD = postgres
