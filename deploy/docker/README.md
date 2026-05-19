# deploy/docker/

`Dockerfile`(s) and `docker-compose.yaml` for containerized deployment.

Targets multi-arch (`linux/amd64`, `linux/arm64`) so the same image runs on a laptop, a server, or a Pi 5. Image carries only `runa` + minimal Python runtime; models, secrets, and state are mounted from the host or fetched at first run.
