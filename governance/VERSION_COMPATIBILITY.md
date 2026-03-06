# Version Compatibility Policy

**National MCP-PAI Oncology Trials Standard — Version Compatibility**
**Version**: 0.1.0

---

## 1. Overview

This document defines the version compatibility policy ensuring that implementations can interoperate across specification versions and that upgrades follow a predictable, non-disruptive path.

---

## 2. Compatibility Matrix

### 2.1 Server-to-Server Compatibility

MCP servers within the same site deployment MUST all conform to the same MAJOR version. MINOR version differences within a site are acceptable provided the lowest-versioned server satisfies the site's declared conformance level.

### 2.2 Client-to-Server Compatibility

Clients (robot agents, coordinator interfaces) conforming to version X.Y MUST work with servers conforming to version X.Z where Z >= Y. Servers MUST accept requests from clients conforming to the same MAJOR version.

### 2.3 Cross-Site Compatibility

Sites participating in the same federated trial SHOULD conform to the same MINOR version. Sites MUST conform to the same MAJOR version. The federated coordination layer MUST handle minor version differences gracefully.

---

## 3. Upgrade Policy

### 3.1 PATCH Upgrades

- PATCH upgrades MUST NOT require implementation changes
- PATCH upgrades MAY be applied without testing
- Implementations SHOULD stay current with PATCH releases

### 3.2 MINOR Upgrades

- MINOR upgrades MUST NOT break existing tool contracts
- MINOR upgrades MAY add new required tools at higher conformance levels
- Implementations SHOULD upgrade within 6 months of a MINOR release
- New MUST requirements added in a MINOR version apply only to new conformance claims

### 3.3 MAJOR Upgrades

- MAJOR upgrades MAY include breaking changes
- Implementations MUST be given at least 12 months to migrate
- The previous MAJOR version MUST receive security patches for at least 12 months after the new MAJOR release
- Migration guides MUST be provided

---

## 4. Multi-Version Support

### 4.1 Transition Periods

During MAJOR version transitions, sites MAY operate implementations conforming to either version. The federated coordination layer MUST support both versions during the transition period.

### 4.2 Version Negotiation

When a client connects to a server, the server's health check response MUST include the conformance version. Clients SHOULD verify version compatibility before making tool calls.

### 4.3 Sunset Schedule

| Phase | Duration | Status |
|-------|----------|--------|
| Active | Until next MAJOR release | Full support, new features |
| Maintenance | 12 months after next MAJOR release | Security patches only |
| End of Life | After maintenance period | No support |

---

## 5. Version Discovery

### 5.1 Health Check

All servers MUST expose version information in their health check response:

```json
{
  "server": "implementation-name",
  "version": "1.0.0",
  "conformance_level": 3,
  "conformance_version": "0.1.0",
  "status": "healthy",
  "timestamp": "2026-03-06T00:00:00Z"
}
```

### 5.2 Capability Advertisement

Servers SHOULD advertise their supported tools and conformance level to enable client-side feature detection.
