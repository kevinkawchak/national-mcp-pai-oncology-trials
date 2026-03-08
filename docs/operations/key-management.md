# Key Management Guide

**National MCP-PAI Oncology Trials Standard**
**Document Classification**: Operational / Security
**Last Updated**: 2026-03-08

---

## 1. Overview

This document defines key management requirements for MCP-PAI oncology trial deployments. It covers the lifecycle of all cryptographic keys used across the five MCP servers, including token signing, audit record integrity, FHIR de-identification, mTLS certificates, and evidence signing.

Key management must satisfy:
- **21 CFR Part 11** (electronic signatures and records) -- see `regulatory/CFR_PART_11.md`
- **HIPAA Security Rule** (encryption requirements) -- see `regulatory/HIPAA.md`
- **NIST SP 800-57** (key management best practices)

---

## 2. Key Inventory

### 2.1 Cryptographic Keys in Use

| Key Name | Algorithm | Purpose | Used By | Rotation Period |
|----------|-----------|---------|---------|-----------------|
| HMAC De-identification Key | HMAC-SHA256 | Patient ID pseudonymization in Safe Harbor pipeline | `trialmcp-fhir` (`servers/trialmcp_fhir/deid_pipeline.py`) | Annually or per trial phase |
| Audit Chain Signing Key | SHA-256 | Hash chain integrity for audit records | `trialmcp-ledger` (`servers/trialmcp_ledger/chain.py`) | Never rotated (chain-bound) |
| Token Secret | Cryptographic random (UUID v4) | Token generation and validation | `trialmcp-authz` (`servers/trialmcp_authz/token_store.py`) | 90 days |
| mTLS Server Certificates | RSA-2048 or ECDSA P-256 | Server identity and transport encryption | All servers | Annually |
| mTLS Client Certificates | RSA-2048 or ECDSA P-256 | Client authentication for inter-server communication | All servers | Annually |
| Evidence Signing Key | RSA-4096 or Ed25519 | Signing incident evidence and audit exports | Operations team | 2 years |
| Database Encryption Key | AES-256-GCM | Encryption at rest for PostgreSQL | Storage backend | Annually |
| Provenance Fingerprint Salt | SHA-256 | Data fingerprinting for provenance records | `trialmcp-provenance` (`servers/trialmcp_provenance/dag.py`) | Per trial phase |

---

## 3. Key Generation Requirements

### 3.1 General Requirements

- All keys MUST be generated using cryptographically secure random number generators (CSPRNG)
- Key generation MUST occur on FIPS 140-2 Level 2 (or higher) validated hardware when available
- Key generation events MUST be recorded in the audit ledger
- No key material may be transmitted in plaintext over any network

### 3.2 HMAC De-identification Key

The HMAC key used by the FHIR de-identification pipeline (`servers/trialmcp_fhir/deid_pipeline.py`) determines the pseudonymized patient identifiers. This key has special requirements:

```bash
# Generate a new HMAC key (256-bit)
openssl rand -hex 32

# Store in environment or secrets manager
export TRIALMCP_HMAC_KEY="<generated-key>"
```

**Requirements**:
- Minimum 256 bits of entropy
- MUST be consistent across all FHIR server replicas at a site (same pseudonym = same patient)
- MUST be different across trial sites (to prevent cross-site patient re-identification)
- MUST NOT be the default value from `deploy/config/fhir.yaml` (`change-this-to-a-secure-random-key`)
- Changing this key changes all pseudonymized IDs -- coordinate with data management

### 3.3 Token Secrets

Per `spec/security.md`, tokens are generated using UUID v4 and stored as SHA-256 hashes:

```bash
# Token generation is handled internally by trialmcp-authz
# The token store (servers/trialmcp_authz/token_store.py) uses SHA-256 hashing
# No external key generation is required for tokens themselves

# However, if using JWT-based tokens (extension), generate an RS256 key pair:
openssl genrsa -out authz-signing-key.pem 2048
openssl rsa -in authz-signing-key.pem -pubout -out authz-signing-key.pub
```

### 3.4 mTLS Certificates

```bash
# Generate site CA (do this once per site)
openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:P-256 \
  -keyout site-ca-key.pem -out site-ca-cert.pem -days 1825 \
  -subj "/C=US/ST=CA/O=TrialMCP Site/CN=Site CA" -nodes

# Generate server certificate (per server)
openssl req -newkey ec -pkeyopt ec_paramgen_curve:P-256 \
  -keyout trialmcp-authz-key.pem -out trialmcp-authz-csr.pem \
  -subj "/C=US/ST=CA/O=TrialMCP Site/CN=trialmcp-authz" -nodes

openssl x509 -req -in trialmcp-authz-csr.pem \
  -CA site-ca-cert.pem -CAkey site-ca-key.pem -CAcreateserial \
  -out trialmcp-authz-cert.pem -days 365

# Repeat for fhir, dicom, ledger, provenance servers
```

### 3.5 Evidence Signing Key

```bash
# Generate Ed25519 key pair for evidence signing
openssl genpkey -algorithm Ed25519 -out evidence-signing-key.pem
openssl pkey -in evidence-signing-key.pem -pubout -out evidence-signing-key.pub

# Or generate GPG key for evidence signing
gpg --full-generate-key  # Select RSA 4096, no expiration for archival use
```

---

## 4. Key Storage Requirements

### 4.1 Storage Hierarchy

| Security Level | Storage Method | Applicable Keys |
|---------------|----------------|-----------------|
| **Level 1** (Highest) | Hardware Security Module (HSM) / Cloud KMS | Audit chain signing key, site CA private key, evidence signing key |
| **Level 2** | Secrets manager (HashiCorp Vault, AWS Secrets Manager) | HMAC de-identification key, token secrets, database encryption key |
| **Level 3** | Kubernetes Secrets (encrypted at rest) or encrypted config files | mTLS certificates, provenance fingerprint salt |

### 4.2 HSM/KMS Integration

For Level 1 keys, use a FIPS 140-2 Level 3 HSM or cloud KMS:

```yaml
# Example Vault configuration for HMAC key
# vault kv put secret/trialmcp/fhir hmac_key=<key>

# Kubernetes external secrets operator example
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: trialmcp-fhir-secrets
  namespace: trialmcp
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: ClusterSecretStore
  target:
    name: trialmcp-fhir-hmac
  data:
    - secretKey: TRIALMCP_HMAC_KEY
      remoteRef:
        key: secret/trialmcp/fhir
        property: hmac_key
```

### 4.3 Key Storage Prohibitions

- NEVER store keys in source code or version control
- NEVER store keys in container images
- NEVER log key material at any log level
- NEVER transmit keys via email, chat, or unencrypted channels
- NEVER use the default HMAC key from `deploy/config/fhir.yaml`
- NEVER store private keys on shared filesystems without encryption

---

## 5. Token Signing Key Lifecycle

### 5.1 Token Lifecycle (per spec/security.md)

```
Generation --> Issuance --> Validation --> Revocation/Expiry
    |                           |
    |  SHA-256 hash stored      |  Hash comparison
    |  in token_store            |  against stored hash
    v                           v
  token_store.py            token_store.py
```

### 5.2 Token Constraints

Per `deploy/config/authz.yaml` and `spec/security.md`:

| Parameter | Value | Source |
|-----------|-------|--------|
| Default token expiry | 3,600 seconds (1 hour) | `deploy/config/authz.yaml` `token_default_expiry` |
| Maximum token expiry | 86,400 seconds (24 hours) | `deploy/config/authz.yaml` `token_max_expiry` |
| Token format | UUID v4 | `spec/security.md` Section 3.1 |
| Storage format | SHA-256 hash of token value | `spec/security.md` Section 3.1 |
| Revocation | Immediate, idempotent | `spec/security.md` Section 3.3 |

### 5.3 Token Rotation for Long-Running Procedures

Per `spec/security.md` Section 3.4, robotic procedures that exceed the token expiry must use token rotation:

1. A new token is issued before the current token expires
2. The old token is revoked atomically with new token issuance
3. Both events (revocation and issuance) are recorded in the audit ledger
4. The robot agent must handle the token swap without interrupting the procedure

---

## 6. Audit Record Signing Key Management

### 6.1 Hash Chain Integrity Model

The audit chain (`servers/trialmcp_ledger/chain.py`) uses SHA-256 hash chaining rather than asymmetric signing. Each record's hash is computed as:

```
hash = SHA-256(previous_hash + canonical_json(record))
```

The genesis hash is `"0" * 64` (64 zero characters), as defined in `deploy/config/ledger.yaml`.

### 6.2 Chain Anchor Protection

The genesis hash is the trust anchor for the entire audit chain. Protect it by:

1. Recording the genesis hash in the site capability profile
2. Storing a signed copy of the genesis hash in the HSM/KMS
3. Including the genesis hash in the site certification evidence pack
4. Verifying the genesis hash during every chain integrity check

### 6.3 Optional Asymmetric Signing Extension

For sites requiring non-repudiation beyond hash chaining:

```bash
# Generate an Ed25519 key pair for ledger record signing
openssl genpkey -algorithm Ed25519 -out ledger-signing-key.pem

# Store in HSM for production use
# Sign each audit record after hash computation
# Append the signature as an extension field per governance/EXTENSIONS.md
```

---

## 7. mTLS Certificate Management

### 7.1 Certificate Authority Hierarchy

```
National MCP Root CA (offline, air-gapped)
  |
  +--> Site Intermediate CA (per hospital site)
         |
         +--> Server Certificates (per MCP server instance)
         +--> Client Certificates (per authorized client/robot)
```

### 7.2 Certificate Requirements

| Attribute | Requirement |
|-----------|-------------|
| Key algorithm | ECDSA P-256 (preferred) or RSA-2048 (minimum) |
| Signature algorithm | SHA-256 |
| Server certificate validity | 1 year maximum |
| Client certificate validity | 1 year maximum |
| Intermediate CA validity | 5 years maximum |
| Root CA validity | 20 years |
| Key usage | Digital Signature, Key Encipherment |
| Extended key usage | Server Auth (servers), Client Auth (clients) |
| Subject Alternative Names | Required for all server certificates |
| CRL / OCSP | Required for production deployments |

### 7.3 Certificate Deployment

```yaml
# Kubernetes TLS secret for trialmcp-authz
apiVersion: v1
kind: Secret
metadata:
  name: trialmcp-authz-tls
  namespace: trialmcp
type: kubernetes.io/tls
data:
  tls.crt: <base64-encoded-cert-chain>
  tls.key: <base64-encoded-private-key>
  ca.crt: <base64-encoded-ca-cert>
```

---

## 8. Key Rotation Procedures

### 8.1 Rotation Schedule

| Key Type | Rotation Period | Rotation Method | Downtime Required |
|----------|----------------|-----------------|-------------------|
| HMAC de-identification key | Annually or per trial phase | Dual-key transition | No (rolling) |
| Token secrets | 90 days | New tokens issued with new secret | No |
| mTLS server certificates | Annually | Rolling certificate update | No (rolling) |
| mTLS client certificates | Annually | Re-issue and distribute | No |
| Evidence signing key | 2 years | New key pair, old key archived | No |
| Database encryption key | Annually | Re-encryption with new key | Planned maintenance window |
| Provenance fingerprint salt | Per trial phase | New salt, document the change | No |

### 8.2 HMAC Key Rotation Procedure

The HMAC key rotation for the FHIR de-identification pipeline requires careful coordination because changing the key changes all pseudonymized patient IDs:

1. **Pre-rotation**: Document the current HMAC key fingerprint (SHA-256 of the key itself)
2. **Generate new key**: `openssl rand -hex 32`
3. **Dual-key period**: Configure the FHIR server to accept both old and new pseudonyms for a transition period
4. **Update secrets store**: Write the new key to Vault/KMS
5. **Rolling restart**: Restart FHIR server replicas one at a time
6. **Verification**: Confirm de-identification produces expected pseudonyms with new key
7. **Record in audit ledger**: The key rotation event must be audited
8. **Update data management**: Notify the data management team of the pseudonym mapping change

### 8.3 mTLS Certificate Rotation Procedure

```bash
# 1. Generate new certificate
openssl req -newkey ec -pkeyopt ec_paramgen_curve:P-256 \
  -keyout trialmcp-authz-key-new.pem -out trialmcp-authz-csr-new.pem \
  -subj "/C=US/ST=CA/O=TrialMCP Site/CN=trialmcp-authz" -nodes

openssl x509 -req -in trialmcp-authz-csr-new.pem \
  -CA site-ca-cert.pem -CAkey site-ca-key.pem -CAcreateserial \
  -out trialmcp-authz-cert-new.pem -days 365

# 2. Update Kubernetes secret
kubectl create secret tls trialmcp-authz-tls-new \
  --cert=trialmcp-authz-cert-new.pem \
  --key=trialmcp-authz-key-new.pem \
  -n trialmcp --dry-run=client -o yaml | kubectl apply -f -

# 3. Rolling restart
kubectl rollout restart deployment/trialmcp-authz -n trialmcp

# 4. Verify
kubectl rollout status deployment/trialmcp-authz -n trialmcp
curl -sf --cacert site-ca-cert.pem https://trialmcp-authz:8001/health
```

---

## 9. Secrets Rotation Automation

### 9.1 Automated Rotation with HashiCorp Vault

```hcl
# Vault policy for HMAC key rotation
path "secret/data/trialmcp/fhir" {
  capabilities = ["create", "read", "update"]
}

# Vault rotation configuration
resource "vault_generic_secret" "hmac_rotation" {
  path = "secret/trialmcp/fhir"
  data_json = jsonencode({
    hmac_key = var.hmac_key
    rotated_at = timestamp()
  })

  lifecycle {
    # Rotate annually
    ignore_changes = [data_json]
  }
}
```

### 9.2 Kubernetes CronJob for Certificate Renewal

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: trialmcp-cert-renewal
  namespace: trialmcp
spec:
  schedule: "0 2 1 */3 *"  # Quarterly check
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: cert-renewal
              image: trialmcp-cert-manager:latest
              command:
                - /bin/sh
                - -c
                - |
                  # Check certificate expiry
                  for server in authz fhir dicom ledger provenance; do
                    expiry=$(openssl x509 -in /certs/${server}.pem -noout -enddate)
                    echo "trialmcp-${server}: ${expiry}"
                  done
              volumeMounts:
                - name: certs
                  mountPath: /certs
                  readOnly: true
          restartPolicy: OnFailure
          volumes:
            - name: certs
              secret:
                secretName: trialmcp-tls-certs
```

### 9.3 Rotation Audit Trail

Every key rotation MUST be recorded in the audit ledger with:
- Key type rotated
- Rotation timestamp
- Authorized by (operator identity)
- Old key fingerprint (SHA-256 of key, not the key itself)
- New key fingerprint
- Verification result (confirm new key is functional)

---

## 10. Compromise Response

### 10.1 Key Compromise Indicators

- Unauthorized audit records appearing in the chain
- De-identified data containing recognizable patient information
- mTLS handshake failures with valid certificates
- Unexpected token validation successes for revoked tokens
- Alerts from HSM/KMS indicating unauthorized access

### 10.2 Compromise Response Procedure

1. **Classify as P1 incident** per `docs/operations/incident-response.md`
2. **Immediately revoke** the compromised key
3. **Generate replacement key** following procedures in Section 3
4. **Assess exposure window**: Determine the time range during which the compromised key was active
5. **Audit trail review**: Export and analyze audit records for the exposure window
6. **Notify stakeholders**: Per the incident response escalation matrix
7. **Regulatory notification**: If PHI exposure is confirmed, follow HIPAA breach notification procedures
8. **Re-issue dependent credentials**: Rotate any tokens or certificates that depended on the compromised key

---

*For operational procedures, see `docs/operations/runbook.md`.*
*For incident response, see `docs/operations/incident-response.md`.*
*For backup and recovery of key material, see `docs/operations/backup-recovery.md`.*
