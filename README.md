# Python Network Automation & Incident Response

A professional case study demonstrating Python-based network operations, DNS incident response, REST API integration, automated notifications, remediation, configuration protection, and proactive monitoring in a controlled enterprise lab environment.

> **Portfolio disclosure:** This repository documents the engineering approach, technologies, outcomes, and lessons learned from a successfully completed academic lab. The original assessment instructions, solution code, lab credentials, configuration files, screenshots, and other restricted course materials are intentionally not published.

---

## Project Overview

The project centered on a simulated enterprise network incident involving an internal DNS service outage and endpoints configured to use an unauthorized DNS resolver. The objective was not only to restore service, but to automate as much of the detection, escalation, remediation, verification, and follow-up process as possible.

The work was completed in two phases:

1. **Incident Response and Remediation** — detect the DNS issue, identify affected devices, notify stakeholders, generate help-desk tickets, restore DNS service, correct endpoint DNS settings, verify recovery, and send a resolution notification.
2. **Proactive Monitoring and Prevention** — back up DNS configurations, automate device inventory, monitor availability, alert on outages, create tickets automatically, detect and correct altered DNS settings, resolve tickets programmatically, and log healthy DNS state.

---

## Incident Response Lifecycle

```text
Network Inventory
      |
      v
Device & DNS Verification
      |
      v
Unauthorized DNS Detected
      |
      +---------------------+
      |                     |
      v                     v
Stakeholder Alert      Help-Desk Tickets
      |                     |
      +----------+----------+
                 |
                 v
         DNS Service Check
                 |
                 v
        Service Restoration
                 |
                 v
       Endpoint Remediation
                 |
                 v
         Recovery Verification
                 |
                 v
        Resolution Notification
```

---

## Proactive Monitoring Lifecycle

```text
Configuration Backup
        |
        v
Automated Device Inventory
        |
        v
Availability Monitoring
        |
   +----+----+
   |         |
Healthy   Unavailable
   |         |
   |         +--> Email Alert
   |         +--> Help-Desk Ticket
   |                |
   |                v
   |        DNS Configuration Check
   |                |
   |        Alteration Detected?
   |                |
   |                v
   |        Automated Remediation
   |                |
   |                v
   |        Ticket Updated to Resolved
   |                |
   +----------------+
        |
        v
DNS Health & Configuration Logging
```

---

## Technologies and Concepts

**Programming & Automation**  
Python • CSV processing • JSON • File operations • Structured logging

**Networking**  
DNS • BIND • ICMP reachability • Linux networking • Service validation • Port verification

**Integration**  
REST APIs • HTTP POST/PATCH • JSON payloads • SMTP email automation

**Operations & Security**  
Incident response • Configuration validation • Unauthorized DNS detection • Automated remediation • Root-cause troubleshooting • Service restoration

**Development Workflow**  
Git • GitLab • Branch-based development • Incremental commits • Evidence-based validation

---

## Engineering Capabilities Demonstrated

### Automated Device Discovery and Validation

Python workflows were used to process a structured device inventory, validate device reachability, collect network information, and classify DNS state as authorized, unauthorized, unknown, or not applicable.

### DNS Incident Detection

The monitoring workflow identified systems that were operational but resolving through an unauthorized DNS server. This distinction was important because simple reachability alone would not have exposed the configuration compromise.

### Automated Stakeholder Notification

When affected systems were identified, an automated SMTP workflow generated incident notifications containing device-specific information and incident context.

### REST API Ticket Automation

The workflow integrated with a help-desk web service to create structured incident tickets. Ticket type and priority were determined by the condition detected, and API authentication was handled separately from application logic.

### DNS Service Recovery

The internal DNS service was checked programmatically, identified as unavailable, restarted, and then verified both at the service level and by confirming DNS was listening on the expected port.

### Endpoint DNS Remediation

Affected devices were reconfigured to use the approved internal DNS servers. The remediation process included verification that the unauthorized resolver had been removed before the device was considered corrected.

### Configuration Backup and Change Detection

DNS server configurations were backed up to establish a known-good state. Later monitoring compared current DNS record data with the stored baseline to identify unexpected changes.

### Automated Ticket Lifecycle Management

The proactive-monitoring workflow did more than create a ticket. After successful DNS remediation, it updated the existing ticket to a resolved state through the API, demonstrating end-to-end incident lifecycle automation.

### Operational Logging

Healthy DNS state was written to a persistent log with timestamps, device names, service status, and configuration status. This provided a simple operational record that could support auditing and trend analysis.

---

## Validated Outcomes

The completed lab demonstrated the following outcomes:

- Automated inventory processing across a 16-device network environment
- Detection of four endpoints using an unauthorized DNS resolver
- Successful automated incident email delivery
- Successful help-desk ticket creation through a REST API
- Detection of an inactive internal DNS service
- Successful DNS service restart and validation
- Successful endpoint DNS remediation and verification
- Successful resolution-notification delivery
- Automated backup of both DNS server configurations
- Detection of an unavailable server and automatic notification
- Automatic creation of an outage ticket
- Detection and correction of an altered DNS configuration
- Programmatic update of the associated ticket to resolved
- Health logging confirming both DNS servers were functioning correctly and unchanged

The underlying academic submissions were formally evaluated as passing and competent across the required technical areas.

---

## Security and Operational Practices

Several practices from the project translate directly to production-oriented infrastructure work:

- **Separate secrets from code** by using environment variables for API authentication.
- **Validate before declaring success** by checking service state, expected configuration, and network listening state after remediation.
- **Preserve evidence** by writing structured CSV/JSON results and operational logs.
- **Prioritize based on impact** rather than treating every network condition identically.
- **Close the incident lifecycle** by notifying stakeholders and updating tickets after recovery.
- **Maintain a known-good baseline** for detecting unauthorized configuration changes.

---

## Engineering Challenges and Lessons Learned

### Reachability Is Not Health

A device can respond to a ping while still being misconfigured or compromised. Combining availability checks with configuration validation provides a more meaningful picture of operational health.

### Automation Needs Verification

A command completing successfully does not guarantee the desired state was achieved. The remediation workflow explicitly checked the resulting DNS configuration and service state before reporting success.

### Incident Automation Works Best as a Workflow

The strongest result came from linking multiple functions together: detection, alerting, ticket creation, remediation, validation, logging, and closure. Each component becomes more valuable when it participates in a complete operational process.

### Baselines Improve Preventive Operations

Backing up a known-good configuration enabled later automation to distinguish healthy state from unexpected change. That shifts the approach from purely reactive troubleshooting toward proactive monitoring.

---

## Future Improvements

A production-oriented version of this concept could add:

- SSH or API-based device management instead of console-oriented lab access
- Centralized secrets management
- Structured application logging with log levels
- Unit and integration tests
- Retry and backoff logic for API and SMTP failures
- Parallel device checks for larger environments
- Configuration management with Ansible or another automation platform
- Metrics export to a monitoring platform
- SIEM integration for security-event correlation
- Containerized mock services for repeatable testing
- CI/CD validation through GitHub Actions

---

## Independent Demonstration Roadmap

Because the original academic solution code is restricted from public distribution, a future iteration of this repository can include a completely independent implementation using synthetic infrastructure and newly written code. That version could use fictional devices, mock DNS state, a local REST API, and a local SMTP test service while demonstrating the same general engineering concepts without reproducing course solutions.

---

## Skills Demonstrated

`Python` `Network Automation` `DNS` `BIND` `REST APIs` `SMTP` `Incident Response` `Linux` `Monitoring` `Configuration Management` `Git` `GitLab` `Troubleshooting` `Operational Automation`

---

## Academic Integrity Note

This repository is intentionally a **case study rather than a solution repository**. It describes the engineering problem, methods, technical competencies, and validated outcomes while excluding restricted assessment content and original solution code.