# Writers Codespaces Environment

This repository ships with a [Development Container](https://containers.dev/) configuration that enables a fully reproducible GitHub Codespaces experience. The dev container bundles Docker tooling so that the multi-service stack (ASR → NLP → Worker → MinIO → Redis → PostgreSQL) can be orchestrated with Docker Compose directly from within the Codespace.

## What the dev container does

- Builds on top of `mcr.microsoft.com/devcontainers/base:ubuntu-22.04` with Python, build tools, Git, curl, Make, and the Docker CLI + Compose plugin installed.
- Binds the host Docker socket into the Codespace so `docker compose` commands operate on the outer Docker engine.
- Adds the non-root `vscode` user to the `docker` group so Compose commands work without `sudo`.
- Forwards all application ports so the services are reachable from your browser:
  - `7000` – Whisper ASR API
  - `8000` – Optional vLLM/OpenAI-compatible API
  - `8001` – Writers NLP API / backend
  - `9000` – MinIO S3 endpoint
  - `9001` – MinIO admin console
  - `5432` – PostgreSQL database
  - `6379` – Redis broker/cache
- Exposes GPU-related environment variables so that, when a Codespace (or local dev container) is scheduled on GPU-capable hardware, the stack can use NVIDIA devices. Codespaces currently does not provide GPUs, so the services automatically fall back to CPU execution.
- Runs `make build && make up && make migrate && make init-bucket` right after the Codespace is created so the full stack is built, started, migrated, and the default MinIO bucket is created.

## Working with the stack

The project is driven via the `Makefile` targets which wrap Docker Compose:

```bash
make build       # Build/update service images
make up          # Start all services in the background
make logs        # Follow combined service logs
make down        # Stop services
make migrate     # Run database migrations inside the NLP service
make init-bucket # Seed the writers bucket in MinIO
make clean       # Tear everything down (containers, volumes, generated data)
```

The post-create hook already builds and starts the stack. To confirm everything is running, use `make logs` or inspect the Docker tab in VS Code (Docker extension is preinstalled).

### Manual service control

You can also interact with Docker Compose directly:

```bash
docker compose ps
docker compose restart nlp
```

Both `models/` and `data/` are bind-mounted into the ASR service so that downloaded Whisper models and generated transcription data persist across container rebuilds.

## Known limitations

- **GPU acceleration**: GitHub Codespaces does not currently expose GPU hardware. The ASR/LLM services detect this automatically and fall back to CPU inference, which is slower but functional.
- **Resource usage**: Running all services simultaneously requires a medium Codespace (4+ vCPUs / 8+ GB RAM). The devcontainer requests these resources via `hostRequirements`, but you may need to adjust the machine size manually if you run into OOM issues.
- **Cold start**: The initial `make build` step can take several minutes because it builds multiple service images and downloads ML models as needed.

## Troubleshooting

- If `docker compose` commands fail with permissions errors, run `groups` to ensure your session is part of the `docker` group. Rebuilding or reloading the window usually fixes group membership issues after initial creation.
- To reclaim disk space, run `make clean` which removes containers, volumes, and cached models/data. Re-run `make up` afterwards to recreate them.
- When working offline or with bandwidth constraints, pre-pull service images and models locally, then push them to a registry/minio bucket to avoid long builds inside the Codespace.

## Additional tooling

The devcontainer preinstalls the VS Code extensions most commonly used in this project:

- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker)
- [GitLens](https://marketplace.visualstudio.com/items?itemName=eamodio.gitlens)
- [Jupyter](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter)

Feel free to add more in `.devcontainer/devcontainer.json` under `customizations.vscode.extensions`.
