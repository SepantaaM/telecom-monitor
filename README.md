# Telecom Service Monitor

A production-grade observability stack for telecom infrastructure, built with Docker Compose. Provides real-time metrics collection, dashboards, alerting, and automated health checks.

## Stack

| Component | Role |
|-----------|------|
| **Prometheus** | Metrics collection & alert evaluation |
| **Grafana** | Dashboards & visualization |
| **Node Exporter** | Host-level metrics (CPU, RAM, disk, network) |
| **Nginx Exporter** | Web service metrics |
| **Nginx** | Simulated service endpoint |
| **Health Checker** | Custom Python alerting with webhook support |

## Architecture

```
                    ┌─────────────────────────────────────┐
                    │         Docker Network               │
                    │                                      │
  ┌──────────┐     │  ┌────────────┐   ┌──────────────┐  │
  │  Browser │────▶│  │  Grafana   │──▶│  Prometheus  │  │
  └──────────┘     │  │  :3000     │   │  :9090       │  │
                    │  └────────────┘   └──────┬───────┘  │
                    │                          │ scrapes   │
                    │  ┌────────────┐   ┌──────▼───────┐  │
                    │  │   Nginx    │   │Node Exporter │  │
                    │  │   :8080    │   │   :9100      │  │
                    │  └─────┬──────┘   └──────────────┘  │
                    │        │          ┌──────────────┐  │
                    │        └─────────▶│Nginx Exporter│  │
                    │                   │   :9113      │  │
                    │  ┌────────────┐   └──────────────┘  │
                    │  │  Health    │                      │
                    │  │  Checker  │──── webhook alerts    │
                    │  └────────────┘                      │
                    └─────────────────────────────────────┘
```

## Quick Start

```bash
# Clone the repo
git clone https://github.com/SepantaaM/telecom-monitor
cd telecom-monitor

# Configure environment
cp .env.example .env
# Edit .env if needed

# Start the stack
docker compose up -d

# Check status
docker compose ps
```

Then open:
- **Grafana**: http://localhost:3000 (admin / changeme_in_production)
- **Prometheus**: http://localhost:9090
- **Service health**: http://localhost:8080/health

## Alert Rules

Pre-configured Prometheus alert rules (`prometheus/alerts.yml`):

| Alert | Threshold | Severity |
|-------|-----------|----------|
| High CPU | > 85% for 2m | Warning |
| High Memory | > 80% for 2m | Warning |
| Disk Critical | > 90% | Critical |
| Service Down | unreachable for 1m | Critical |
| High Nginx Error Rate | > 5% 5xx | Warning |

## Webhook Alerts

Set `ALERT_WEBHOOK` in `.env` to a Slack or Teams webhook URL to receive alerts on service state changes.

## CI/CD

GitHub Actions pipeline (`.github/workflows/ci.yml`) on every push:
1. Lints Python code
2. Validates Docker Compose syntax
3. Validates Prometheus config and alert rules with `promtool`
4. Boots the full stack and runs integration tests against live endpoints

## What This Demonstrates

- **Containerization**: Multi-service Docker Compose with named networks and volumes
- **Observability**: Prometheus metrics pipeline + Grafana dashboards
- **Alerting**: Rule-based alerts + webhook notifications
- **Infrastructure as Config**: All config declarative and version-controlled
- **CI/CD**: Automated validation and integration testing on every push
- **Security**: Secrets via `.env`, never committed to git

## License

MIT
