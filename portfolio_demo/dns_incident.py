#!/usr/bin/env python3
"""Offline DNS incident simulation using synthetic snapshots.

This is independently developed portfolio code, not a university lab solution.
No DNS queries, device changes, emails, tickets, or HTTP calls are performed.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
from pathlib import Path
from typing import Any

MAX_INPUT_BYTES = 256 * 1024
MAX_FRAMES = 64
MAX_DEVICES = 256
MAX_APPROVED = 16


class ScenarioError(ValueError):
    """Invalid or unsupported synthetic scenario data."""


def _name(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 64:
        raise ScenarioError(f"{label}: expected a nonempty string of at most 64 characters")
    if not all(c.isascii() and (c.isalnum() or c in "-_ .") for c in value):
        raise ScenarioError(f"{label}: only ASCII letters, numbers, spaces, '-', '_', '.' allowed")
    return value


def _ip(value: Any, label: str) -> str:
    if not isinstance(value, str):
        raise ScenarioError(f"{label}: expected a literal IPv4 address")
    try:
        return str(ipaddress.IPv4Address(value))
    except ValueError as exc:
        raise ScenarioError(f"{label}: invalid IPv4 address") from exc


def parse_scenario(document: Any) -> tuple[set[str], list[dict[str, Any]]]:
    """Validate inputs before processing; do not silently skip malformed devices."""
    if not isinstance(document, dict):
        raise ScenarioError("scenario: expected an object")
    allowed = document.get("approved_resolvers")
    if not isinstance(allowed, list) or not 1 <= len(allowed) <= MAX_APPROVED:
        raise ScenarioError(f"approved_resolvers: expected 1-{MAX_APPROVED} IPv4 addresses")
    approved = {_ip(ip, f"approved_resolvers[{i}]") for i, ip in enumerate(allowed)}
    if len(approved) != len(allowed):
        raise ScenarioError("approved_resolvers: duplicate IP address")
    frames = document.get("frames")
    if not isinstance(frames, list) or not 1 <= len(frames) <= MAX_FRAMES:
        raise ScenarioError(f"frames: expected 1-{MAX_FRAMES} snapshots")

    clean = []
    baseline_devices: set[str] | None = None
    for i, frame in enumerate(frames):
        prefix = f"frames[{i}]"
        if not isinstance(frame, dict):
            raise ScenarioError(f"{prefix}: expected an object")
        label = _name(frame.get("label"), f"{prefix}.label")
        status = frame.get("dns_service")
        if status not in ("running", "stopped"):
            raise ScenarioError(f"{prefix}.dns_service: must be 'running' or 'stopped'")
        devices = frame.get("devices")
        if not isinstance(devices, list) or not 1 <= len(devices) <= MAX_DEVICES:
            raise ScenarioError(f"{prefix}.devices: expected 1-{MAX_DEVICES} devices")
        seen = set()
        valid_devices = []
        for j, device in enumerate(devices):
            label_prefix = f"{prefix}.devices[{j}]"
            if not isinstance(device, dict):
                raise ScenarioError(f"{label_prefix}: expected an object")
            device_id = _name(device.get("id"), f"{label_prefix}.id")
            if device_id in seen:
                raise ScenarioError(f"{prefix}: duplicate device id '{device_id}'")
            seen.add(device_id)
            reachable = device.get("reachable")
            if type(reachable) is not bool:
                raise ScenarioError(f"{label_prefix}.reachable: expected boolean")
            resolver = _ip(device.get("resolver"), f"{label_prefix}.resolver")
            valid_devices.append({"id": device_id, "reachable": reachable, "resolver": resolver})
        if baseline_devices is None:
            baseline_devices = seen
        elif seen != baseline_devices:
            raise ScenarioError(f"{prefix}: device inventory changed across snapshots; no implicit recovery from missing devices")
        clean.append({"label": label, "dns_service": status, "devices": valid_devices})
    return approved, clean


def assess(approved: set[str], frame: dict[str, Any]) -> dict[str, dict[str, str]]:
    """Classify observed DNS service, endpoint reachability and resolver policy."""
    issues: dict[str, dict[str, str]] = {}
    if frame["dns_service"] == "stopped":
        issues["service/dns"] = {
            "category": "DNS_SERVICE_DOWN", "severity": "critical",
            "recommendation": "Inspect the DNS service and verify recovery; no action is executed.",
        }
    for d in frame["devices"]:
        name = d["id"]
        if not d["reachable"]:
            issues[f"device/{name}/availability"] = {
                "category": "DEVICE_UNREACHABLE", "severity": "high",
                "recommendation": "Check endpoint connectivity and network path; no action is executed.",
            }
        if d["resolver"] not in approved:
            issues[f"device/{name}/resolver"] = {
                "category": "UNAPPROVED_RESOLVER", "severity": "high",
                "recommendation": "Review the endpoint resolver configuration; no change is executed.",
            }
    return issues


def simulate(document: Any) -> dict[str, Any]:
    """Compute incident/ticket lifecycle with no external side effects."""
    approved, frames = parse_scenario(document)
    active: dict[str, dict[str, str]] = {}
    tickets: list[dict[str, str]] = []
    active_tickets: dict[str, dict[str, str]] = {}
    output = []
    next_ticket = 1

    for frame in frames:
        current = assess(approved, frame)
        events = []
        for key in sorted(current.keys() - active.keys()):
            issue = current[key]
            ticket_id = f"SIM-{next_ticket:04d}"
            next_ticket += 1
            ticket = {"id": ticket_id, "status": "OPEN", "category": issue["category"], "incident": key}
            tickets.append(ticket)
            active_tickets[key] = ticket
            events.append({
                "type": "OPENED", "incident": key, "ticket": ticket_id,
                "notification": "QUEUED_IN_SIMULATION", "severity": issue["severity"],
            })
        for key in sorted(active.keys() - current.keys()):
            ticket = active_tickets.pop(key)
            ticket_id = ticket["id"]
            ticket["status"] = "RESOLVED"
            events.append({"type": "RECOVERED", "incident": key, "ticket": ticket_id,
                           "notification": "QUEUED_IN_SIMULATION"})
        output.append({
            "label": frame["label"],
            "active_incidents": sorted(current),
            "events": events,
        })
        active = current

    return {
        "mode": "offline_simulation",
        "frames": output,
        "tickets": tickets,
        "final_active_incidents": sorted(active),
    }


def load_scenario(path: Path) -> Any:
    """Bound input size to limit accidental large-file processing."""
    try:
        with path.open("rb") as handle:
            payload = handle.read(MAX_INPUT_BYTES + 1)
    except OSError as exc:
        raise ScenarioError(f"cannot read scenario: {exc.strerror or type(exc).__name__}") from exc
    if len(payload) > MAX_INPUT_BYTES:
        raise ScenarioError("scenario exceeds 256 KiB limit")
    try:
        return json.loads(payload.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ScenarioError("scenario must be valid UTF-8 JSON") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline, synthetic DNS incident lifecycle")
    parser.add_argument("--scenario", type=Path,
                        default=Path(__file__).with_name("sample_timeline.json"))
    parser.add_argument("--json", action="store_true", help="Print machine-readable report")
    args = parser.parse_args(argv)
    try:
        result = simulate(load_scenario(args.scenario))
    except ScenarioError as exc:
        parser.exit(2, f"Scenario error: {exc}
")
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for frame in result["frames"]:
            kinds = [f'{e["type"]} {e["incident"]} ({e["ticket"]})' for e in frame["events"]]
            print(f'{frame["label"]}: active={len(frame["active_incidents"])} '
                  f'events={kinds or "none"}')
        print("Offline simulation complete; no external actions performed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
