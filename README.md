# Deploy agent
A lightweight deployment agent that watches a Git repository and automatically deploys Docker Compose stacks when changes are detected.
It’s designed for simple, Git-driven deployments on a single host. I wanted something like this because my servers are not accessible by the public, but don't have the hardware to easily run my own git infrastructure/github runners and wanted a bit more flexibility than a simple bash script.

## How it works
1. Clones (or pulls) a Git repository on a fixed interval
2. Detects changes on a configured branch
3. Determines which Docker Compose stacks were modified
4. Pulls updated images and runs docker compose up -d
5. Optionally injects secrets from ```/secrets/<stack>.env```

It can deploy:
- Only changed stacks (default)
- All stacks on every change (forced mode)

## Repository structure

Expected structure inside the Git repo:

```
/stacks
├── stack-a/
│   ├── docker-compose.yml
│   └── ...
├── stack-b/
│   ├── compose.yaml
│   └── ...
```

Each top-level directory containing a Compose file is treated as a stack.
Supported filenames:
- ```docker-compose.yml```
- ```docker-compose.yaml```
- ```compose.yml```
- ```compose.yaml```


## Secrets handling
If a secrets file exists at:
```
/secrets/<stack-name>.env
```
It will be copied to:
```
/stacks/<stack-name>/.env
```
before deployment.

If no secrets file exists, the stack is deployed without a ```.env```.

## Environment variables

|Variables|Default|Descrition|
|-|-|-|
|```GIT_REPO```|not set *(required)*|Git repository URL|
|```BRANCH```|```main```|Branch to track|
|```CHECK_INTERVAL```|```300```|Polling interval in seconds|
|```COMPOSE_DIR```|not set (root)|Subdirectory to use under ```/stacks```, so by default it assumes that all compose files are under here|
|```FORCE_DEPLOY_ALL```|```False```|Redeploy all stacks, even when just one changes|
|```LOG_LEVEL```|```INFO```|Logging level|

## Running with Docker

Example ```compose.yml```:
```yaml
services:
  deploy-agent:
    image: ghcr.io/woutnerd/pull-cd:latest
    restart: unless-stopped
    environment:
      GIT_REPO: https://github.com/your-org/your-stacks.git
      BRANCH: main
      CHECK_INTERVAL: 300
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./stacks:/stacks
      - ./secrets:/secrets
```
> [!IMPORTANT]
> The Docker socket must be mounted for the agent to control Docker on the host.

## Deployment behavior

### On startup:

- Clones the entire repo (if needed)
- Deploys __all detected stacks__

### On change detection:

- Fetches latest changes
- If ```FORCE_DEPLOY_ALL=False```:
  - Deploys only stacks affected by the Git diff
- If ```FORCE_DEPLOY_ALL!=False```:
  - Deploys all stacks

## Logging

