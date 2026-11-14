# Independent DNS Incident Lifecycle Demonstration

This executable example complements the WGU case study documented in the parent README. It was **written independently** using fictional device snapshots, invented hostnames, and IPv4 documentation ranges. No original university assignment code, credentials, configuration exports, or screenshots are included.

## Run it in two commands

Requirements: Python 3.11 or later; no runtime packages, AWS account, or network access required.

```bash
python portfolio_demo/dns_incident.py
python -m unittest discover -s tests -v
```

For structured JSON output, run `python portfolio_demo/dns_incident.py --json`. For a different invented timeline, use `--scenario path/to/scenario.json`.

Expected event counts from the supplied [fictional timeline](sample_timeline.json):

| Snapshot | Active issues | New events |
|---|---:|---|
| Healthy baseline | 0 | None |
| DNS service stops; resolver drifts | 2 | 2 OPENED |
| Same failure persists | 2 | None |
| Service and resolver recover | 0 | 2 RECOVERED |

## Implemented and testable

- Parse strictly validated local JSON snapshots (up to 256 KiB), with literal IPv4 resolvers and consistent device inventory.
- Independently detect stopped DNS services, unapproved resolvers, and unreachable endpoints.
- Suppress duplicate ticket-open events while incidents remain active.
- Create **fictional, in-memory ticket records**; mark recovered incidents RESOLVED. Reappearance creates a new simulated ticket.
- Add simulated notification markers; no messages are actually queued or transmitted.
- Provide deterministic human-readable and JSON reports.
- Exercise both healthy paths and error paths through [31 regression tests](../tests/test_dns_incident.py).
- Verify results automatically using [GitHub Actions](../.github/workflows/verify-dns-lab.yml).

## Scope and security boundaries

**This is an offline simulation, not a monitoring agent.** Snapshot values are supplied by the JSON file; the program does not perform DNS lookups, network connections, service restarts, endpoint changes, notifications, SMTP, REST API ticket creation, or cloud deployment. It has no scheduler, persistent state, authentication, or production remediation logic. All ticket IDs and alerts are illustrative only.

Changing or removing a device from one snapshot to the next is rejected instead of being interpreted as recovery. No restricted WGU source code was reused.

The engineering principle illustrated here is that reachability, DNS-service state, and resolver configuration must be assessed independently, and incident recovery should be verified without flooding a ticketing system with duplicate notifications.

See [the parent WGU case study](../README.md) for the distinct historical academic outcomes and the separate [Network Reliability Lab](https://github.com/montezguido/network-reliability-lab) for live **loopback-only** HTTP/TCP testing.
