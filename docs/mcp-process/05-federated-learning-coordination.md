# 05 — Federated Learning Coordination

**National MCP-PAI Oncology Trials Standard v0.9.0**

Multi-site federated model training and aggregation flow, showing how clinical
trial data remains on-site while enabling collaborative learning across the network.

## Federated Learning Round Lifecycle

```
+-------------------------------------------------------------------------------+
|                        FEDERATED LEARNING ROUND LIFECYCLE                     |
+-------------------------------------------------------------------------------+
|                                                                               |
|  COORDINATOR                 SITE A               SITE B              SITE C  |
|  +----------+                +------+             +------+            +----+  |
|  |          |  1. Init Round |      |             |      |            |    |  |
|  | Round N  +--------------->+ Recv +------------>+ Recv +----------->+Recv|  |
|  | Config:  |  Global Model  |Model |             |Model |            |Mod |  |
|  | - algo   |  + Hyperparams |      |             |      |            |    |  |
|  | - epochs |                +--+---+             +--+---+            +-+--+  |
|  | - lr     |                   |                    |                  |     |
|  | - min_   |                   v                    v                  v     |
|  |   sites  |                +------+             +------+            +----+  |
|  |          |                |Local |             |Local |            |Lcl |  |
|  |          |                |Train |             |Train |            |Trn |  |
|  |          |                |on    |             |on    |            |on  |  |
|  |          |                |Site  |             |Site  |            |Ste |  |
|  |          |                |Data  |             |Data  |            |Dta |  |
|  |          |                +--+---+             +--+---+            +-+--+  |
|  |          |                   |                    |                  |     |
|  |          |                   v                    v                  v     |
|  |          |                +------+             +------+            +----+  |
|  |          |                |Apply |             |Apply |            |Aply|  |
|  |          |                |Diff  |             |Diff  |            |Dff |  |
|  |          |                |Priv  |             |Priv  |            |Prv |  |
|  |          |                |(eps) |             |(eps) |            |(ep)|  |
|  |          |                +--+---+             +--+---+            +-+--+  |
|  |          |                   |                    |                  |     |
|  |          |  2. Submit        |                    |                  |     |
|  |          |  Masked Updates   |                    |                  |     |
|  | Collect  +<------------------+--------------------+------------------+     |
|  | Updates  |                                                                 |
|  +----+-----+                                                                 |
|       |                                                                       |
|       v                                                                       |
|  +-------------------+                                                        |
|  | 3. Secure         |                                                        |
|  |    Aggregation    |                                                        |
|  |                   |                                                        |
|  | +---------------+ |                                                        |
|  | | Verify shares | |                                                        |
|  | +---------------+ |                                                        |
|  | | Reconstruct   | |                                                        |
|  | | aggregated    | |                                                        |
|  | | gradient      | |                                                        |
|  | +---------------+ |                                                        |
|  | | Apply to      | |                                                        |
|  | | global model  | |                                                        |
|  | +---------------+ |                                                        |
|  +--------+----------+                                                        |
|           |                                                                   |
|           v                                                                   |
|  +-------------------+                                                        |
|  | 4. Update Privacy |                                                        |
|  |    Budgets        |                                                        |
|  |    Site A: eps    |                                                        |
|  |      consumed     |                                                        |
|  |    Site B: eps    |                                                        |
|  |      consumed     |                                                        |
|  |    Site C: eps    |                                                        |
|  |      consumed     |                                                        |
|  +--------+----------+                                                        |
|           |                                                                   |
|           v                                                                   |
|  +-------------------+                                                        |
|  | 5. Audit + Prov   |                                                        |
|  |    Record round   |                                                        |
|  |    in ledger +    |                                                        |
|  |    provenance     |                                                        |
|  +-------------------+                                                        |
|           |                                                                   |
|           v                                                                   |
|  Round N+1 or CONVERGED                                                       |
|                                                                               |
+-------------------------------------------------------------------------------+
```

## Secure Aggregation Protocol

```
+-----------------------------------------------------------------------------+
|                         SECURE AGGREGATION PROTOCOL                         |
+-----------------------------------------------------------------------------+
|                                                                             |
|  PHASE 1: SHARE GENERATION                                                  |
|  +-------------------------------------------------------------------+      |
|  |                                                                   |      |
|  |  Site A                   Site B                   Site C         |      |
|  |  +------------------+    +------------------+    +-------------+  |      |
|  |  | Local Update: Ua |    | Local Update: Ub |    | Update: Uc  |  |      |
|  |  | Generate mask Ma |    | Generate mask Mb |    | Gen mask Mc |  |      |
|  |  | Share: Ua + Ma   |    | Share: Ub + Mb   |    | Sh: Uc + Mc |  |      |
|  |  +------------------+    +------------------+    +-------------+  |      |
|  |                                                                   |      |
|  +-------------------------------------------------------------------+      |
|                                                                             |
|  PHASE 2: MASKED SUBMISSION                                                 |
|  +-------------------------------------------------------------------+      |
|  |                                                                   |      |
|  |  Site A sends (Ua + Ma) ------+                                   |      |
|  |  Site B sends (Ub + Mb) ------+--> Coordinator                    |      |
|  |  Site C sends (Uc + Mc) ------+    (cannot see individual Ux)     |      |
|  |                                                                   |      |
|  +-------------------------------------------------------------------+      |
|                                                                             |
|  PHASE 3: AGGREGATION                                                       |
|  +-------------------------------------------------------------------+      |
|  |                                                                   |      |
|  |  Coordinator computes:                                            |      |
|  |    Sum = (Ua+Ma) + (Ub+Mb) + (Uc+Mc)                              |      |
|  |        = (Ua+Ub+Uc) + (Ma+Mb+Mc)                                  |      |
|  |                                                                   |      |
|  |  Masks cancel: Ma + Mb + Mc = 0 (by construction)                 |      |
|  |    Result = Ua + Ub + Uc  (true aggregate)                        |      |
|  |                                                                   |      |
|  +-------------------------------------------------------------------+      |
|                                                                             |
|  PHASE 4: DISTRIBUTION                                                      |
|  +-------------------------------------------------------------------+      |
|  |                                                                   |      |
|  |  Coordinator distributes updated global model to all sites        |      |
|  |  Each site verifies aggregate matches expected structure          |      |
|  |  Privacy budget updated: eps_consumed += eps_round                |      |
|  |                                                                   |      |
|  +-------------------------------------------------------------------+      |
|                                                                             |
+-----------------------------------------------------------------------------+
```

## Privacy Budget Accounting

```
+------------------------------------------------------------------------------+
|                          PRIVACY BUDGET ACCOUNTING                           |
+------------------------------------------------------------------------------+
|                                                                              |
|  SITE         TOTAL BUDGET    CONSUMED    REMAINING    STATUS                |
|  +-----------+---------------+-----------+-----------+-----------+           |
|  |           |               |           |           |           |           |
|  | Site A    |  eps = 10.0   |    3.2    |    6.8    |  ACTIVE   |           |
|  | Site B    |  eps = 10.0   |    4.1    |    5.9    |  ACTIVE   |           |
|  | Site C    |  eps = 10.0   |    8.7    |    1.3    |  WARNING  |           |
|  | Site D    |  eps = 10.0   |   10.0    |    0.0    | EXHAUSTED |           |
|  |           |               |           |           |           |           |
|  +-----------+---------------+-----------+-----------+-----------+           |
|                                                                              |
|  Budget Consumption per Round:                                               |
|  +-------+------------+------------+------------+------------+               |
|  | Round | Site A eps | Site B eps | Site C eps | Site D eps |               |
|  +-------+------------+------------+------------+------------+               |
|  |   1   |    0.8     |    0.8     |    0.8     |    0.8     |               |
|  |   2   |    0.8     |    1.1     |    2.3     |    3.2     |               |
|  |   3   |    0.8     |    1.1     |    2.3     |    3.2     |               |
|  |   4   |    0.8     |    1.1     |    3.3     |    2.8     |               |
|  +-------+------------+------------+------------+------------+               |
|                                                                              |
|  Policy Rules:                                                               |
|  - WARNING  when remaining < 20% of total budget                             |
|  - EXHAUSTED when remaining = 0 (site excluded from future rounds)           |
|  - Budget reset requires IRB re-approval + new consent epoch                 |
|                                                                              |
+------------------------------------------------------------------------------+
```

## Site Data Harmonization

```
+-----------------------------------------------------------------------------+
|                          SITE DATA HARMONIZATION                            |
+-----------------------------------------------------------------------------+
|                                                                             |
|  RAW SITE DATA         HARMONIZATION PIPELINE          HARMONIZED DATA      |
|  +----------------+    +------------------------+      +----------------+   |
|  |                |    |                        |      |                |   |
|  | Site A Schema  +--->+ 1. Schema Mapping      +----->+ Unified Schema |   |
|  | (custom fields)|    |    Map site-specific   |      | (standard      |   |
|  |                |    |    fields to national  |      |  field names)  |   |
|  +----------------+    +------------------------+      +----------------+   |
|  |                |    |                        |      |                |   |
|  | Site B Values  +--->+ 2. Value Set Alignment +----->+ Standard Codes |   |
|  | (local codes)  |    |    Map local codes to  |      | (ICD-10,       |   |
|  |                |    |    national standards  |      |  SNOMED CT)    |   |
|  +----------------+    +------------------------+      +----------------+   |
|  |                |    |                        |      |                |   |
|  | Site C Dates   +--->+ 3. Temporal Alignment  +----->+ UTC Dates      |   |
|  | (mixed TZ)     |    |    Normalize timezones |      | (ISO-8601)     |   |
|  |                |    |    and date formats    |      |                |   |
|  +----------------+    +------------------------+      +----------------+   |
|  |                |    |                        |      |                |   |
|  | All Sites      +--->+ 4. Quality Scoring     +----->+ Quality Score  |   |
|  | (varied quality)|   |    Completeness,       |      | (0.0 - 1.0)    |   |
|  |                |    |    consistency, range  |      |                |   |
|  +----------------+    +------------------------+      +----------------+   |
|                                                                             |
+-----------------------------------------------------------------------------+
```
