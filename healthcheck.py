#!/usr/bin/env python3
"""
Telecom Service Health Checker
Monitors service endpoints and sends alerts via webhook (Slack, Teams, etc.)
Designed for high-availability telecom infrastructure monitoring.
"""

import os
import sys
import time
import logging
import requests
from datetime import datetime, timezone
from typing import Optional

# --- Configuration ---
TARGETS = os.environ.get("TARGETS", "http://localhost:80").split(",")
CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", "30"))
ALERT_WEBHOOK = os.environ.get("ALERT_WEBHOOK", "")
REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", "5"))

# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

# Track state to avoid alert spam (only alert on state change)
service_states: dict[str, bool] = {}


def check_endpoint(url: str) -> tuple[bool, float, Optional[str]]:
    """
    Check a single endpoint.
    Returns: (is_healthy, response_time_ms, error_message)
    """
    try:
        start = time.monotonic()
        resp = requests.get(url.strip(), timeout=REQUEST_TIMEOUT)
        elapsed = (time.monotonic() - start) * 1000
        is_ok = resp.status_code < 500
        return is_ok, round(elapsed, 2), None
    except requests.exceptions.ConnectionError as e:
        return False, 0.0, f"Connection refused: {e}"
    except requests.exceptions.Timeout:
        return False, 0.0, f"Timed out after {REQUEST_TIMEOUT}s"
    except Exception as e:
        return False, 0.0, str(e)


def send_alert(url: str, is_up: bool, error: Optional[str] = None):
    """Send a webhook alert (Slack-compatible format)."""
    if not ALERT_WEBHOOK:
        return

    status = "✅ RECOVERED" if is_up else "🔴 DOWN"
    color = "good" if is_up else "danger"
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    payload = {
        "attachments": [
            {
                "color": color,
                "title": f"[Telecom Monitor] Service {status}",
                "fields": [
                    {"title": "Service", "value": url, "short": False},
                    {"title": "Status", "value": status, "short": True},
                    {"title": "Time", "value": ts, "short": True},
                    {"title": "Error", "value": error or "None", "short": False},
                ],
                "footer": "telecom-monitor",
            }
        ]
    }

    try:
        requests.post(ALERT_WEBHOOK, json=payload, timeout=5)
        log.info(f"Alert sent for {url}: {status}")
    except Exception as e:
        log.warning(f"Failed to send alert: {e}")


def run_checks():
    """Run one round of health checks across all targets."""
    all_healthy = True
    for url in TARGETS:
        url = url.strip()
        if not url:
            continue

        is_healthy, response_time, error = check_endpoint(url)
        prev_state = service_states.get(url)

        if is_healthy:
            log.info(f"[OK] {url} — {response_time}ms")
        else:
            log.error(f"[FAIL] {url} — {error}")
            all_healthy = False

        # Alert only on state change
        if prev_state is not None and prev_state != is_healthy:
            send_alert(url, is_healthy, error)

        service_states[url] = is_healthy

    return all_healthy


def main():
    log.info("=== Telecom Service Health Checker starting ===")
    log.info(f"Targets: {TARGETS}")
    log.info(f"Check interval: {CHECK_INTERVAL}s")
    log.info(f"Webhook configured: {'yes' if ALERT_WEBHOOK else 'no'}")

    # Initial check
    run_checks()

    while True:
        time.sleep(CHECK_INTERVAL)
        run_checks()


if __name__ == "__main__":
    main()
