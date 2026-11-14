# WGU D522 — Historical Evidence and Public Verification Map

This engineering summary distinguishes **completed academic work** from **independently developed public software**. It was prepared from privately retained WGU evaluation records for the two completed *Python for IT Automation (D522)* assessments. Both assessments were evaluated as passing. The evaluation reports, original GitLab submissions, device details, credentials, screenshots, and institution-provided instructions are **not published** here.

## Historical academic assessment evidence

| Assessment | Verified technical capability | Evidence level | Related interview talking point |
|---|---|---|---|
| **Task 1: Incident Response and Remediation** | Python processed a device inventory and classified device status and DNS configuration | Passed academic assessment; private evaluation record | Distinguish device reachability from correctness of DNS configuration |
| Task 1 | Automated stakeholder alert delivery using a controlled mail service | Passed academic assessment; private evaluation record | Confirm that an alert was actually delivered, not merely generated |
| Task 1 | Created issue-specific tickets through a web service | Passed academic assessment; private evaluation record | Preserve source/device context in incident tracking |
| Task 1 | Checked an unavailable DNS service, restarted it, and verified service restoration | Passed academic assessment; private evaluation record | Verify post-change service state before closing an incident |
| Task 1 | Corrected affected endpoints' DNS settings and sent a resolution notification | Passed academic assessment; private evaluation record | Recheck the endpoint's resolver configuration, not just its network link |
| **Task 2: Proactive Monitoring and Prevention** | Backed up DNS configuration files and processed a device inventory | Passed academic assessment; private evaluation record | Establish a recoverable baseline and scope |
| Task 2 | Monitored device availability and produced an administrator alert and ticket for an unavailable device | Passed academic assessment; private evaluation record | Link monitoring signals to consistent escalation |
| Task 2 | Automated DNS configuration monitoring and corrective workflow | Passed academic assessment; private evaluation record | Detect drift before it becomes a prolonged outage |
| Task 2 | Wrote timestamped operational status entries to a log | Passed academic assessment; private evaluation record | Produce audit-friendly evidence and verify continued health |

**Verification scope:** These are summaries of work accepted in a controlled WGU lab, not claims that the original environment remains accessible, operates continuously, or was deployed in production. The private reports attest to assessment outcomes; they do not authorize publishing the original solution code.

## Independent public code — different implementation, different proof

| Public artifact | What reviewers can run or inspect | What it does **not** do |
|---|---|---|
| [Offline DNS simulation](../portfolio_demo/dns_incident.py) | Parse fictional device snapshots, classify DNS-service/resolver issues, simulate OPENED and RECOVERED incidents | No actual DNS checks, device configuration changes, SMTP, or REST API requests |
| [Synthetic scenario](../portfolio_demo/sample_timeline.json) | Replay healthy → DNS outage/resolver drift → persistent failure → recovery | Does not reproduce the school's lab topology or data |
| [Regression tests](../tests/test_dns_incident.py) | Test lifecycle, duplicate-event suppression, inventory consistency, and input handling | Does not validate a live enterprise environment |
| [GitHub Actions](../.github/workflows/verify-dns-lab.yml) | Cross-platform automated tests | Is not the original assessment evaluation |
| [Network Reliability Lab](https://github.com/montezguido/network-reliability-lab) | Separately developed loopback-only HTTP/TCP monitoring and recovery walkthrough | Does not provide live DNS remediation or external ticketing |

## Interview-ready explanation

In the original D522 academic labs, I implemented and verified Python automation for DNS incident response and proactive monitoring, including device inventory, configuration checks, notifications, ticketing, recovery, backups, and logging. For a public portfolio that respects coursework restrictions, I built a **separate** testable Python simulation of DNS incident state transitions and ticket lifecycle. It demonstrates my code and testing methodology; it is not presented as the original assessment submission.

## Opportunities to strengthen this project further

1. Develop an **original local mock HTTP ticket service** with contract tests.
2. Build an **independent, non-remediating DNS verification probe** for explicitly permitted loopback test services.
3. Add structured logging and event persistence to the independent example.

These are **future enhancements**, not features currently claimed as completed.

The goal is precise, interview-defensible evidence: **historical lab competencies** documented honestly, and **new public code** that hiring managers can actually run.
