# 04 — Safety Gate Evaluation

**National MCP-PAI Oncology Trials Standard v0.9.0**

Pre-procedure safety matrix and gate evaluation flow for Physical AI robot-assisted
clinical procedures, including human approval checkpoints and emergency stop semantics.

## Safety Gate Evaluation Matrix

```
+-------------------------------------------------------------------------------+
|                        PRE-PROCEDURE SAFETY GATE MATRIX                       |
+-------------------------------------------------------------------------------+
|                                                                               |
|  GATE              SOURCE               CHECK                    REQUIRED     |
|  +----------------+--------------------+------------------------+----------+  |
|  |                |                    |                        |          |  |
|  | 1. Patient     | trialmcp-fhir      | Consent status is      | MUST     |  |
|  |    Consent     | (consent-status)   | ACTIVE for all         |          |  |
|  |                |                    | required categories:   |          |  |
|  |                |                    |   general_trial        |          |  |
|  |                |                    |   physical_ai          |          |  |
|  |                |                    |   imaging              |          |  |
|  |                |                    |                        |          |  |
|  +----------------+--------------------+------------------------+----------+  |
|  |                |                    |                        |          |  |
|  | 2. Site        | site-capability    | Site has required:     | MUST     |  |
|  |    Capability  | profile            |   MCP servers (5)      |          |  |
|  |                |                    |   Storage backend      |          |  |
|  |                |                    |   Network connectivity |          |  |
|  |                |                    |   Regulatory overlay   |          |  |
|  |                |                    |                        |          |  |
|  +----------------+--------------------+------------------------+----------+  |
|  |                |                    |                        |          |  |
|  | 3. Robot       | robot-capability   | Robot has:             | MUST     |  |
|  |    Capability  | profile            |   Valid USL score      |          |  |
|  |                |                    |   Clinical cert        |          |  |
|  |                |                    |   Procedure match      |          |  |
|  |                |                    |   Calibration current  |          |  |
|  |                |                    |                        |          |  |
|  +----------------+--------------------+------------------------+----------+  |
|  |                |                    |                        |          |  |
|  | 4. Protocol    | task-order         | Task matches:          | MUST     |  |
|  |    Compliance  | schema             |   Trial protocol       |          |  |
|  |                |                    |   Procedure type       |          |  |
|  |                |                    |   Time window          |          |  |
|  |                |                    |   Eligibility criteria |          |  |
|  |                |                    |                        |          |  |
|  +----------------+--------------------+------------------------+----------+  |
|  |                |                    |                        |          |  |
|  | 5. Human       | approval           | Authorized clinician   | MUST     |  |
|  |    Approval    | checkpoint         | approves within        |          |  |
|  |                |                    | timeout (300s)         |          |  |
|  |                |                    |                        |          |  |
|  +----------------+--------------------+------------------------+----------+  |
|                                                                               |
|  ALL GATES MUST PASS FOR PROCEDURE TO PROCEED                                 |
|  ANY SINGLE FAILURE -> PROCEDURE BLOCKED                                      |
|                                                                               |
+-------------------------------------------------------------------------------+
```

## Gate Evaluation Flow

```
+------------------------------------------------------------------------------+
|                             GATE EVALUATION FLOW                             |
+------------------------------------------------------------------------------+
|                                                                              |
|  START                                                                       |
|    |                                                                         |
|    v                                                                         |
|  +-------------------+                                                       |
|  | Load Task Order   |                                                       |
|  | from Schedule     |                                                       |
|  +--------+----------+                                                       |
|           |                                                                  |
|           v                                                                  |
|  +-------------------+     +-------------------+                             |
|  | Gate 1: Patient   |---->| FAIL: Consent not |---> BLOCK + AUDIT LOG       |
|  | Consent Check     |     | active for all    |                             |
|  +--------+----------+     | required cats     |                             |
|           | PASS           +-------------------+                             |
|           v                                                                  |
|  +-------------------+     +-------------------+                             |
|  | Gate 2: Site      |---->| FAIL: Missing     |---> BLOCK + AUDIT LOG       |
|  | Capability Check  |     | infrastructure    |                             |
|  +--------+----------+     +-------------------+                             |
|           | PASS                                                             |
|           v                                                                  |
|  +-------------------+     +-------------------+                             |
|  | Gate 3: Robot     |---->| FAIL: Robot not   |---> BLOCK + AUDIT LOG       |
|  | Capability Check  |     | eligible          |                             |
|  +--------+----------+     +-------------------+                             |
|           | PASS                                                             |
|           v                                                                  |
|  +-------------------+     +-------------------+                             |
|  | Gate 4: Protocol  |---->| FAIL: Protocol    |---> BLOCK + AUDIT LOG       |
|  | Compliance Check  |     | violation         |                             |
|  +--------+----------+     +-------------------+                             |
|           | PASS                                                             |
|           v                                                                  |
|  +-------------------+     +-------------------+                             |
|  | Gate 5: Human     |---->| TIMEOUT/DENY:     |---> ESCALATE + AUDIT LOG    |
|  | Approval Request  |     | Not approved in   |                             |
|  +--------+----------+     | 300 seconds       |                             |
|           | APPROVE        +-------------------+                             |
|           v                                                                  |
|  +-------------------+                                                       |
|  | ALL GATES PASSED  |                                                       |
|  | Transition to     |                                                       |
|  | APPROVED state    |                                                       |
|  +-------------------+                                                       |
|           |                                                                  |
|           v                                                                  |
|  +-------------------+                                                       |
|  | Audit: Log all    |                                                       |
|  | gate results to   |                                                       |
|  | trialmcp-ledger   |                                                       |
|  +-------------------+                                                       |
|                                                                              |
+------------------------------------------------------------------------------+
```

## Emergency Stop Signal Propagation

```
+--------------------------------------------------------------------------------+
|                      EMERGENCY STOP SIGNAL PROPAGATION                         |
+--------------------------------------------------------------------------------+
|                                                                                |
|  E-STOP TRIGGER                                                                |
|  (Clinician, Safety System, or Robot Self-Detect)                              |
|    |                                                                           |
|    v                                                                           |
|  +-------------------+                                                         |
|  | E-Stop Controller |                                                         |
|  | Signal Generated  |                                                         |
|  | ID: estop-{uuid}  |                                                         |
|  | Time: ISO-8601    |                                                         |
|  +--------+----------+                                                         |
|           |                                                                    |
|  +---+----+---+---------+----------+-----------+-----------+----+              |
|      |        |         |          |           |           |                   |
|      v        v         v          v           v           v                   |
|  +------+ +------+ +--------+ +--------+ +----------+ +---------+              |
|  |AuthZ | |FHIR  | |DICOM   | |Ledger  | |Provenance| |Robot    |              |
|  |Server| |Server| |Server  | |Server  | |Server    | |Agent    |              |
|  +--+---+ +--+---+ +---+----+ +---+----+ +----+-----+ +----+----+              |
|     |        |         |          |           |            |                   |
|     v        v         v          v           v            v                   |
|  +------+ +------+ +--------+ +--------+ +----------+ +---------+              |
|  |Revoke| |Lock  | |Suspend | |Append  | |Record    | |Halt Mot.|              |
|  |Active| |Active| |Active  | |E-Stop  | |E-Stop    | |+Preserve|              |
|  |Tokens| |Reads | |Queries | |Audit   | |Lineage   | |State    |              |
|  +------+ +------+ +--------+ +--------+ +----------+-+---------+              |  
|                                                                                |
|                                                                                |
|  POST-ABORT SEQUENCE:                                                          |
|  +-------------------------------------------------------------------+         |
|  | 1. Capture robot state at time of e-stop                          |         |
|  | 2. Log all active procedure state to trialmcp-ledger              |         |
|  | 3. Record e-stop provenance in trialmcp-provenance                |         |
|  | 4. Notify trial coordinator and site PI                           |         |
|  | 5. Await re-authorization before any procedure restart            |         |
|  +-------------------------------------------------------------------+         |
|                                                                                |
+--------------------------------------------------------------------------------+
```

## Human Approval Checkpoint Protocol

```
+-----------------------------------------------------------------------------+
|                      HUMAN APPROVAL CHECKPOINT PROTOCOL                     |
+-----------------------------------------------------------------------------+
|                                                                             |
|  SAFETY GATE            APPROVAL SYSTEM              AUTHORIZED CLINICIAN   |
|  +----------+           +------------------+          +------------------+  |
|  |          |           |                  |          |                  |  |
|  | Generate +---------->+ Create Approval  |          |                  |  |
|  | Approval |  Request  | Request          +--------->+ Review Request   |  |
|  | Request  |  ID+Data  | (ID, procedure,  |  Present | (patient, robot, |  |
|  |          |           |  patient, robot, |          |  procedure type, |  |
|  |          |           |  gate results)   |          |  gate results)   |  |
|  |          |           +--------+---------+          +--------+---------+  |
|  |          |                    |                             |            |
|  |          |           +--------v---------+          +--------v---------+  |
|  |          |           |                  |          |                  |  |
|  |          |           | Start Timeout    |          | Decision:        |  |
|  |          |           | Counter (300s)   |          |   APPROVE        |  |
|  |          |           |                  |          |   DENY           |  |
|  |          |           +--------+---------+          +--------+---------+  | 
|  |          |                    |                             |            |
|  |          |                    |                    +--------v---------+  |
|  |          |                    |                    | Sign Decision    |  |
|  |          |                    |                    | with Clinician   |  |
|  |          |                    +<-------------------+ Credentials      |  |
|  |          |           +--------v---------+          +------------------+  |
|  |          |           |                  |                                |
|  | Receive  +<----------+ Process Decision |                                |
|  | Decision |  Result   | (APPROVE/DENY/   |                                |
|  |          |           |  TIMEOUT)        |                                |
|  +----+-----+           +------------------+                                |
|       |                                                                     |
|       +---> APPROVE: Transition to APPROVED state                           |
|       +---> DENY:    Block procedure + audit log                            |
|       +---> TIMEOUT: Escalate to site PI + audit log                        |
|                                                                             |
+-----------------------------------------------------------------------------+
```
