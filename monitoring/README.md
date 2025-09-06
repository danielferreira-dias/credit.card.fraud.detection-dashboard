Running monitoring stack

This folder contains configuration for Prometheus, Loki, Promtail and Grafana used by the project's `docker-compose.yml`.

Quick start:

1. From the project root run:

   docker-compose up -d prometheus loki promtail grafana

2. Open Grafana at http://localhost:3000 (user: admin, password: admin)
3. Prometheus UI: http://localhost:9090
4. Loki API: http://localhost:3100

Promtail is configured to scrape Docker container logs using the Docker socket. Ensure Docker is running and the socket is available at `/var/run/docker.sock`.

Logs from the `backend` service will be available in Grafana Explore using the Loki datasource. You can search for `compose_service="backend"` or the container name `fraud-detection-backend`.
