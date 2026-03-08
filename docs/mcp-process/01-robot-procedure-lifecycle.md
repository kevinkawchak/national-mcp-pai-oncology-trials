# 01 — Robot Procedure Lifecycle

**National MCP-PAI Oncology Trials Standard v0.9.0**

Complete state machine for a robot-assisted clinical procedure, showing all MCP server
interactions, safety gates, human approval checkpoints, and evidence capture.

## Procedure State Machine

```
+-----------------------------------------------------------------------------+
|                     ROBOT PROCEDURE LIFECYCLE                                |
|                     State Machine with MCP Interactions                      |
+-----------------------------------------------------------------------------+
|                                                                              |
|  +------------+     schedule      +-------------+     verify      +-------+  |
|  |            |  task-order via   |             |   safety gates  |       |  |
|  | SCHEDULED  +------------------>+  PRE_CHECK  +--------------->+ GATES |  |
|  |            |  trialmcp-ledger  |             |  gate_service   | EVAL  |  |
|  +-----+------+                   +------+------+                 +---+---+  |
|        |                                 |                            |      |
|        | cancel                          | fail                       |      |
|        v                                 v                      pass  |      |
|  +------------+                   +-------------+                     |      |
|  |            |                   |             |                     |      |
|  |  ABORTED   |                   |   FAILED    |                     |      |
|  |            |                   |             |                     |      |
|  +------------+                   +-------------+                     |      |
|                                          ^                            |      |
|                                          |                            v      |
|                                          |                   +--------+----+ |
|                                          |    deny/timeout   |             | |
|  +------------+     complete      +------+------+<-----------+ HUMAN       | |
|  |            |  post-procedure   |             |            | APPROVAL    | |
|  | COMPLETED  +<------------------+ IN_PROGRESS +<-----------+             | |
|  |            |  evidence capture |             |  approve   +-------------+ |
|  +------------+                   +------+------+                            |
|        |                                 |                                   |
|        |                                 | e-stop                            |
|        v                                 v                                   |
|  +------------+                   +-------------+                            |
|  |            |                   |             |                            |
|  | POST_CHECK |                   |   ABORTED   |                            |
|  | (evidence) |                   | (preserved) |                            |
|  +------------+                   +-------------+                            |
|                                                                              |
+------------------------------------------------------------------------------+
```

## MCP Server Interactions per State

```
+------------------+-----------------------------------------------------------+
| STATE            | MCP SERVER INTERACTIONS                                   |
+------------------+-----------------------------------------------------------+
|                  |                                                           |
| SCHEDULED        | trialmcp-authz   : Validate scheduling token             |
|                  | trialmcp-ledger  : Append schedule audit record           |
|                  | trialmcp-fhir    : Verify patient enrollment status       |
|                  |                                                           |
+------------------+-----------------------------------------------------------+
|                  |                                                           |
| PRE_CHECK        | trialmcp-authz   : Verify robot agent credentials        |
|                  | trialmcp-fhir    : Confirm consent status (6 categories) |
|                  | trialmcp-dicom   : Validate imaging availability         |
|                  | safety           : Evaluate all gate conditions          |
|                  |   gate_service   :   Patient consent gate                |
|                  |                  :   Site capability gate                 |
|                  |                  :   Robot capability gate                |
|                  |                  :   Protocol compliance gate             |
|                  |                  :   Human approval gate                  |
|                  |                                                           |
+------------------+-----------------------------------------------------------+
|                  |                                                           |
| APPROVED         | trialmcp-authz   : Issue procedure execution token       |
|                  | trialmcp-ledger  : Append approval audit record          |
|                  | trialmcp-provenance : Record approval lineage           |
|                  |                                                           |
+------------------+-----------------------------------------------------------+
|                  |                                                           |
| IN_PROGRESS      | trialmcp-dicom   : Stream imaging metadata pointers      |
|                  | trialmcp-ledger  : Continuous audit trail                |
|                  | trialmcp-provenance : Real-time lineage updates         |
|                  | safety           : Monitor for e-stop signals            |
|                  |                                                           |
+------------------+-----------------------------------------------------------+
|                  |                                                           |
| POST_CHECK       | trialmcp-fhir    : Capture clinical observations         |
|                  | trialmcp-dicom   : Link post-procedure imaging          |
|                  | trialmcp-ledger  : Append completion audit record       |
|                  | trialmcp-provenance : Finalize procedure lineage        |
|                  |                                                           |
+------------------+-----------------------------------------------------------+
|                  |                                                           |
| COMPLETED        | trialmcp-ledger  : Seal procedure audit chain            |
|                  | trialmcp-provenance : Close provenance subgraph         |
|                  |                                                           |
+------------------+-----------------------------------------------------------+
|                  |                                                           |
| ABORTED          | trialmcp-ledger  : Append abort record with reason       |
|                  | trialmcp-provenance : Record abort lineage              |
|                  | safety           : Capture post-abort evidence           |
|                  |                  : Initiate recovery authorization        |
|                  |                                                           |
+------------------+-----------------------------------------------------------+
```

## Timing Constraints

```
+------------------+--------------------+--------------------------------------+
| TRANSITION       | MAX DURATION       | ESCALATION                           |
+------------------+--------------------+--------------------------------------+
| SCHEDULED        |                    |                                      |
|   -> PRE_CHECK   | Per protocol       | Notify trial coordinator             |
+------------------+--------------------+--------------------------------------+
| PRE_CHECK        |                    |                                      |
|   -> APPROVED    | 300 seconds        | Escalate to site PI                  |
+------------------+--------------------+--------------------------------------+
| APPROVED         |                    |                                      |
|   -> IN_PROGRESS | 60 seconds         | Auto-abort if not started            |
+------------------+--------------------+--------------------------------------+
| IN_PROGRESS      |                    |                                      |
|   -> POST_CHECK  | Per procedure type | E-stop if exceeded                   |
+------------------+--------------------+--------------------------------------+
| POST_CHECK       |                    |                                      |
|   -> COMPLETED   | 600 seconds        | Flag incomplete evidence             |
+------------------+--------------------+--------------------------------------+
```
