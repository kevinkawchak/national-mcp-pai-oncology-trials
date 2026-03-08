# 07 — Privacy and De-identification

**National MCP-PAI Oncology Trials Standard v0.9.0**

HIPAA Safe Harbor de-identification pipeline, privacy budget management, and
data residency enforcement across the national Physical AI oncology trials network.

## HIPAA Safe Harbor 18-Identifier Removal Pipeline

```
+-----------------------------------------------------------------------------+
|              HIPAA SAFE HARBOR 18-IDENTIFIER REMOVAL PIPELINE               |
+-----------------------------------------------------------------------------+
|                                                                              |
|  RAW FHIR RESOURCE       DE-IDENTIFICATION STAGES       DE-IDENTIFIED       |
|  +------------------+    +------------------------+     +----------------+  |
|  |                  |    |                        |     |                |  |
|  | Patient:         |    | STAGE 1: Direct IDs   |     | Patient:       |  |
|  |  name: Smith     +--->+  1. Names     REDACT   +---->+  name:         |  |
|  |  address: 123..  |    |  2. Address   REDACT   |     |    [REDACTED]  |  |
|  |  birthDate:      |    |  3. Dates     YEAR     |     |  address:      |  |
|  |    1965-03-15    |    |  4. Phone     REMOVE   |     |    [REDACTED]  |  |
|  |  phone:          |    |  5. Fax       REMOVE   |     |  birthDate:    |  |
|  |    555-123-4567  |    |  6. Email     REMOVE   |     |    1965        |  |
|  |  email:          |    |                        |     |                |  |
|  |    j@example.com |    +------------------------+     +----------------+  |
|  |  ssn:            |    |                        |     |                |  |
|  |    123-45-6789   |    | STAGE 2: Quasi-IDs     |     | Identifiers:   |  |
|  |  mrn:            |    |  7. SSN       REMOVE   |     |  system: MRN   |  |
|  |    MRN-001234    |    |  8. MRN       HMAC     |     |  value:        |  |
|  |  identifier:     |    |  9. Health    REMOVE   |     |   a4f2c8d1...  |  |
|  |    HP-98765      |    |     Plan ID            |     |   (HMAC-256)   |  |
|  |  photo: [data]   |    | 10. Account   REMOVE   |     |                |  |
|  |  device_id:      |    |     Number             |     | id: 7b3c1e...  |  |
|  |    DEV-12345     |    | 11. Cert/     REMOVE   |     |   (pseudonym)  |  |
|  |                  |    |     License             |     |                |  |
|  +------------------+    +------------------------+     +----------------+  |
|                          |                        |                         |
|                          | STAGE 3: Tech IDs      |                         |
|                          | 12. Vehicle    REMOVE   |                         |
|                          | 13. Device     REMOVE   |                         |
|                          | 14. URLs       REMOVE   |                         |
|                          | 15. IP Addr    REMOVE   |                         |
|                          | 16. Biometric  REMOVE   |                         |
|                          | 17. Photo      REMOVE   |                         |
|                          | 18. Other UID  REMOVE   |                         |
|                          +------------------------+                         |
|                                                                              |
|  PSEUDONYMIZATION (HMAC-SHA256):                                             |
|  +-------------------------------------------------------------------+      |
|  |                                                                   |      |
|  |  Input:  patient_id = "patient-001"                               |      |
|  |  Key:    site_hmac_key (configurable per site)                    |      |
|  |  Output: HMAC-SHA256(key, "patient-001") = "a4f2c8d1e5..."       |      |
|  |                                                                   |      |
|  |  Properties:                                                      |      |
|  |  - Deterministic: same input + key = same output                 |      |
|  |  - One-way: cannot recover patient-001 from hash                 |      |
|  |  - Key-dependent: different key = different pseudonym            |      |
|  |  - Cross-site linkage: only possible with shared key agreement   |      |
|  |                                                                   |      |
|  +-------------------------------------------------------------------+      |
|                                                                              |
+------------------------------------------------------------------------------+
```

## Unified De-identification Pipeline (FHIR + DICOM + Free-Text)

```
+-----------------------------------------------------------------------------+
|             UNIFIED DE-IDENTIFICATION PIPELINE                              |
+-----------------------------------------------------------------------------+
|                                                                              |
|  DATA TYPE        DETECTION               MASKING            VERIFICATION   |
|  +-----------+    +------------------+    +---------------+  +------------+ |
|  |           |    |                  |    |               |  |            | |
|  | FHIR R4   +--->+ Field-level PHI  +--->+ Remove/Redact +->+ Verify no | |
|  | Resources |    | detection via    |    | per HIPAA     |  | residual   | |
|  |           |    | PHI_FIELDS set   |    | Safe Harbor   |  | PHI in     | |
|  +-----------+    +------------------+    +---------------+  | output     | |
|  |           |    |                  |    |               |  |            | |
|  | DICOM     +--->+ Tag-level PHI    +--->+ Hash patient  +->+ Verify no | |
|  | Metadata  |    | detection via    |    | names, year-  |  | pixel data | |
|  |           |    | DICOM tag list   |    | only dates    |  | leaked     | |
|  +-----------+    +------------------+    +---------------+  |            | |
|  |           |    |                  |    |               |  |            | |
|  | Free Text +--->+ Pattern-based    +--->+ Regex replace +->+ Verify no | |
|  | (Notes,   |    | PHI detection:   |    | with masks:   |  | patterns   | |
|  |  Reports) |    |  SSN: \d{3}-\d{2}|    |  [SSN]        |  | remain     | |
|  |           |    |  Phone: patterns |    |  [PHONE]      |  |            | |
|  |           |    |  Email: @domain  |    |  [EMAIL]      |  |            | |
|  |           |    |  MRN: patterns   |    |  [MRN]        |  |            | |
|  |           |    |  Date: patterns  |    |  [DATE]       |  |            | |
|  +-----------+    +------------------+    +---------------+  +------------+ |
|                                                                              |
+------------------------------------------------------------------------------+
```

## Data Residency Enforcement

```
+-----------------------------------------------------------------------------+
|                     DATA RESIDENCY ENFORCEMENT                              |
+-----------------------------------------------------------------------------+
|                                                                              |
|  JURISDICTION        POLICY                        ENFORCEMENT              |
|  +-----------------+---------------------------+------------------------+   |
|  |                 |                           |                        |   |
|  | US Federal      | HIPAA minimum necessary  | All data on US soil    |   |
|  | (All Sites)     | De-ID required for any   | Encryption at rest +   |   |
|  |                 | cross-site transfer      | in transit             |   |
|  |                 | Audit all access          | BAA required           |   |
|  |                 |                           |                        |   |
|  +-----------------+---------------------------+------------------------+   |
|  |                 |                           |                        |   |
|  | California      | CCPA consumer rights     | Right to Know audit    |   |
|  | (CA Sites)      | Data minimization        | Right to Delete impl   |   |
|  |                 | Sensitive PI protections  | Opt-Out tracking       |   |
|  |                 | 12-month retention limit  | 12-month auto-purge    |   |
|  |                 |                           |                        |   |
|  +-----------------+---------------------------+------------------------+   |
|  |                 |                           |                        |   |
|  | New York        | PHL Article 27-F (HIV)   | HIV data isolation     |   |
|  | (NY Sites)      | SHIELD Act safeguards    | Enhanced encryption    |   |
|  |                 | MHL Article 33 (mental)  | Mental health lockbox  |   |
|  |                 | DOH 10 NYCRR Parts 405   | Separate consent req   |   |
|  |                 |                           |                        |   |
|  +-----------------+---------------------------+------------------------+   |
|                                                                              |
|  CROSS-SITE TRANSFER AUTHORIZATION:                                         |
|  +-------------------------------------------------------------------+      |
|  |                                                                   |      |
|  |  1. Requesting site submits transfer request with justification   |      |
|  |  2. Source site verifies destination jurisdiction compatibility    |      |
|  |  3. Patient consent checked for data_sharing category             |      |
|  |  4. Data de-identified before transfer                            |      |
|  |  5. Transfer logged in both site audit ledgers                    |      |
|  |  6. Provenance record created linking source and destination      |      |
|  |  7. Privacy budget decremented for source site                    |      |
|  |                                                                   |      |
|  +-------------------------------------------------------------------+      |
|                                                                              |
+------------------------------------------------------------------------------+
```

## Access Control Decision Flow

```
+-----------------------------------------------------------------------------+
|                    ACCESS CONTROL DECISION FLOW                             |
+-----------------------------------------------------------------------------+
|                                                                              |
|  REQUEST                RBAC CHECK              ABAC CHECK        DECISION  |
|  +-----------+          +-------------+         +------------+    +-------+ |
|  |           |          |             |         |            |    |       | |
|  | Actor:    +--------->+ Role in     +--FAIL-->+            |    | DENY  | |
|  |  robot_   |          | permission  |         |            |    |       | |
|  |  agent    |          | matrix?     |         |            |    +-------+ |
|  |           |          +------+------+         |            |              |
|  | Resource: |                 | PASS           |            |              |
|  |  fhir_    |                 v                |            |              |
|  |  read     |          +------+------+         |            |    +-------+ |
|  |           |          | Tool        +--FAIL-->+            |    | DENY  | |
|  | Context:  |          | allowed for |         |            |    |       | |
|  |  patient  |          | this role?  |         |            |    +-------+ |
|  |  -001     |          +------+------+         |            |              |
|  |           |                 | PASS           |            |              |
|  | Data      |                 v                |            |              |
|  | Class:    |          +------+------+  +------+------+     |    +-------+ |
|  |  confid-  |          | Data class  |  | Consent     |     |    |       | |
|  |  ential   |          | allowed for +->+ status      +---->+    | ALLOW | |
|  |           |          | this role?  |  | verified?   | ALL |    |       | |
|  +-----------+          +-------------+  +-------------+ PASS    +-------+ |
|                                                                              |
|  DATA CLASSIFICATION LEVELS:                                                 |
|  +-------------------------------------------------------------------+      |
|  |  PUBLIC       : Aggregate trial statistics, published results     |      |
|  |  INTERNAL     : Site operational data, non-PHI metrics            |      |
|  |  CONFIDENTIAL : De-identified clinical data, pseudonymized IDs    |      |
|  |  RESTRICTED   : PHI, identifiable data, consent records           |      |
|  +-------------------------------------------------------------------+      |
|                                                                              |
+------------------------------------------------------------------------------+
```
