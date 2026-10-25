# Supporting services

The [Compose file](compose.yaml) supplies n8n 2.44.4 and Mailpit 1.31.6, with named persistent volumes and a shared network. FastAPI, Laya, MiniLM, embedded Qdrant, and Ollama run on Windows. There is no Qdrant server container.

From the repository root on a **fresh** machine:

```powershell
docker compose -f docker/compose.yaml config --quiet
docker compose -f docker/compose.yaml up -d
docker compose -f docker/compose.yaml ps
```

n8n: <http://localhost:5678>; Mailpit UI: <http://localhost:8025>; SMTP: `127.0.0.1:1025`. Finish n8n's local owner setup and [import the workflow](../docs/N8N_INTEGRATION.md). No credentials or workflow database are provisioned automatically.

The HTTP/SMTP ports bind to loopback. n8n reaches Windows at `host.docker.internal:8003`. FastAPI must listen on `0.0.0.0` for this route; Windows Firewall must restrict access to the trusted development environment. n8n's secure-cookie flag is false for this local HTTP configuration. Use HTTPS and an appropriately secured configuration for any deployment beyond localhost.

If existing containers already publish these ports, keep using them. Do **not** run a second Compose stack on the same ports or rename/recreate the existing containers. `scripts/start.ps1 -DockerServices` checks occupied ports and reuses existing services. Its checks do not prove that every occupant is the expected service; inspect `docker ps` and run `doctor.py`.

Shutdown for this Compose project:

```powershell
docker compose -f docker/compose.yaml stop
```

`stop` retains containers and volumes. Do not use volume deletion to resolve startup issues. Back up n8n's volume, including its encryption key, and Mailpit's volume before migration. This repository contains none of those private files.

Compose syntax validation and runtime verification are recorded separately in [VALIDATION.md](../docs/VALIDATION.md). The fresh template is not evidence that a second stack was launched on the occupied default ports.

Reference: [Mailpit's official Docker configuration](https://mailpit.axllent.org/docs/install/docker/).
