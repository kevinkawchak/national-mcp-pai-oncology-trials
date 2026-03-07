## Prompt v0.5.2

Your goal is to create 5 comprehensive prompts for national-mcp-pai-oncology-trials that will be run in separate conversations based on the two following sets of feedback (For future comprehensive 1M token processing using Claude Code Opus 4.6). The biggest concern is to make the codebase comprehensive and appropriate for national-level physical ai oncology trials mcp servers. The primary focus is to make the repository more practical, useful, and substantive in code (with any supporting code documentation needed). Do not process the 5 prompt's instructions.

For each of the prompts, consistently include these statements where most appropriate:
"Update relevant readme files and documentation throughout the repo based on all changes made (diagrams, mermaid diagrams, badges, text, repository structure, etc.)" "It is imperative that all code now be accurate, end-to-end, and appropriate for a national scale."

Include all of the claude "Implemented"/"Deferred" responses to the openai recommendations as tables in a response-A-2026-03-06.md under /peer-review in this format:
## Claude Code Opus 4.6 Responses to ChatGPT 5.4 Thinking
(no text here)
### Response
(tables here)

Place each of the 5 prompts into separate .md files under /peer-review with format claude-#-2026-03-06.md (# = 1-5) with the following content format:
## Claude Code Opus 4.6 [Prompt Only]
(no text here)
### Prompt
(text here)

Provide a copy of this exact prompt under main prompts.md. Be sure to fix and address errors that would cause failed checks for the single pull request (such as Python environment issues to avoid the following error during final checks): "3 failing checks
x Cl / lint-and-format (3.10) (pull...
x Cl / lint-and-format (3.11) (pull...
x Cl / lint-and-format (3.12) (pull... " Place the new release notes in releases.md under main using the format below (which is the same format of the last published version). Update changelog.md using v0.5.2. When you are finished, auto-push the update to GitHub on your own for my review. The user will then review your updates in GitHub prior to finalization.

"FORMAT"
Release title
v0.5.2 -

## Summary

## Features

## Contributors
@kevinkawchak
@claude
@openai

## Notes

"START FEEDBACK 1"
Here's a candid repo review based on the repository's current files and implementation shape.

The main gap is that the repo already reads like a national standard, but the codebase is still mostly a specification-and-fixtures repository rather than a practical, adoptable source implementation. The README positions it as a "Normative Specification" and "United States Industry Standard"  , but the executable artifacts that stakeholders would expect for a national source repo are still thin: the Python reference is a single in-memory Level 1 stub, the TypeScript reference is also a stub, and the conformance suite mostly validates fixture objects and schemas rather than black-box behavior of real MCP servers        .

1. Highest-priority changes: make it an implementation repo, not just a spec repo

Add
	1.	A real runnable MCP server stack, not just helper functions.
The Python reference currently exposes plain functions like authz_evaluate, ledger_append, and health_status, backed by an in-memory token store  . To be credible as a national source, the repo should add:
	•	a real MCP server entrypoint
	•	transport support
	•	request routing
	•	configuration loading
	•	structured logging
	•	persistent storage adapters
	•	health/readiness endpoints
	•	a Docker-based local deployment
	2.	A complete reference implementation for all five server domains.
The README claims five servers and 23 tools as the standard surface  , but the reference code only implements a minimal Level 1 core example in Python and TypeScript      . Add actual reference servers for:
	•	authz
	•	fhir
	•	dicom
	•	ledger
	•	provenance
	3.	A deployment model that hospitals and vendors can actually evaluate.
Add:
	•	docker-compose.yml for a single-site deployment
	•	Kubernetes manifests or Helm chart
	•	example secrets/config templates
	•	local mock services for FHIR, DICOM, and audit storage
	•	sample site profile configs
	4.	A persistence layer.
The current token handling is explicitly in-memory and non-production  . Add durable implementations for:
	•	token store
	•	policy store
	•	audit ledger storage
	•	provenance graph storage
	•	site capability registry

Fix
	1.	Turn the "reference implementation" into a real reference architecture.
Right now it is more a code sketch than a reference system. The code needs:
	•	package layout by server/domain
	•	interfaces and adapters
	•	config management
	•	environment-based bootstrapping
	•	proper exception handling and error mapping
	•	versioned API compatibility tests
	2.	Add end-to-end workflows.
Stakeholders will want to see practical workflows, such as:
	•	robot requests token → token validated → FHIR read → DICOM query → ledger append → provenance record
	•	trial coordinator study lookup
	•	auditor replay and chain verification
	•	multi-site provenance trace

Remove or de-emphasize

Until those pieces exist, remove or soften positioning that implies the repo is already the national implementation source. The current README's "United States Industry Standard" framing is ahead of what the code supports  .

2. Fix internal contract mismatches immediately

This is the most important code-quality issue. The repository currently contains schema/code/test drift.

Examples of drift

In Python:
	•	authz_evaluate() returns decision, resource_id, reason, matching_rules as strings, and timestamp
	•	but the schema requires allowed, effect, role, server, tool, and evaluated_at, with matching_rules as structured objects

In Python:
	•	ledger_append() returns record_id and prev_hash
	•	but the audit schema requires audit_id and previous_hash

In Python:
	•	health_status() returns server, timestamp, and dependencies as an object
	•	but the health schema requires server_name, checked_at, and dependencies as an array of typed objects

The same mismatch pattern exists in TypeScript, where the stub returns decision/timestamp and record_id/prev_hash shapes that do not match the normative schemas      .

Add

Create a single canonical contract source of truth:
	•	either schemas generate code models
	•	or code models generate schemas
	•	but not both manually

Add:
	•	generated typed models for Python and TypeScript
	•	schema-to-code consistency checks in CI
	•	snapshot tests for all example payloads
	•	contract tests that validate runtime outputs against schemas

Fix

Rename and normalize fields across repo artifacts:
	•	record_id → audit_id
	•	prev_hash → previous_hash
	•	server → server_name where appropriate
	•	timestamp → checked_at or evaluated_at where schema requires it
	•	unify decision/effect and allowed semantics

Remove

Remove duplicate hand-maintained payload definitions in fixtures once generated canonical models exist.

3. Replace fixture-based conformance with black-box conformance

The current conformance suite is useful, but it is mostly validating fixture objects and helper outputs. For example, test_core_conformance.py imports sample fixtures and local helper constructors rather than exercising a real deployment boundary  . The conformance runner just builds pytest paths; it does not target a remote server, base URL, MCP transport, or deployment manifest  .

Add
	1.	Real black-box conformance harness
Add a test harness that can point at:
	•	a local process
	•	a containerized deployment
	•	a staging URL
	•	a vendor implementation
	2.	Test adapters
Add pluggable adapters for:
	•	stdin/stdout MCP
	•	HTTP transport if used
	•	authenticated sessions
	•	seeded test data
	3.	Certification-style output
Add:
	•	machine-readable test reports
	•	profile pass/fail summary
	•	evidence bundle export
	•	reproducible certification manifest
	4.	Negative and adversarial test packs
Expand into:
	•	authz bypass attempts
	•	PHI leakage checks
	•	replay attacks
	•	tampered audit chain imports
	•	malformed DICOM/FHIR resource handling
	•	rate limiting and abuse cases

Fix

Refactor the existing conformance suite into:
	•	unit tests for fixtures and helpers
	•	integration tests for reference servers
	•	black-box conformance tests for external implementations

Remove

Stop counting fixture-validation tests as the primary measure of implementation maturity. "269 passing" is not yet equivalent to "deployable national conformance" if most tests do not cross a real server boundary    .

4. Make the repository operationally credible

Add
	1.	Security implementation details
The spec is strong on intent, but the code should add:
	•	key management strategy
	•	signed audit records
	•	token signing and verification
	•	mTLS guidance
	•	secrets rotation
	•	tamper-evident storage design
	•	SBOM and dependency scanning
	•	threat model document
	•	incident response runbook
	2.	Production concerns
Add:
	•	retries and circuit breakers for clinical dependencies
	•	idempotency behavior for write-like actions
	•	concurrency and locking strategy for ledger writes
	•	backpressure and queueing
	•	observability standards
	•	audit export and archival flows
	3.	Reliability docs
Add SLO/SLA guidance:
	•	uptime targets
	•	latency budgets
	•	fail-safe modes
	•	degraded operation rules
	•	data recovery procedures

Fix

The current CI is not enough for stakeholder confidence.
	•	It installs Python lint/test dependencies only
	•	It does not build or test the TypeScript reference
	•	The docs link checker prints broken links but exits with 0 regardless, so it won't fail the build on broken links

Add CI jobs for:
	•	TypeScript build/test/lint
	•	container build
	•	schema/code drift
	•	API contract snapshots
	•	end-to-end conformance runs
	•	security scanning
	•	docs lint that actually fails on errors

5. Expand the code surface where stakeholders will care most

Add
	1.	Real FHIR handling
Add:
	•	SMART-on-FHIR or equivalent auth integration patterns
	•	patient/resource access filters
	•	de-identification implementation with test corpus
	•	capability statements
	•	terminology mapping strategy
	•	realistic Bundle handling
	2.	Real DICOM handling
Add:
	•	QIDO/WADO/STOW guidance if relevant
	•	retrieval-pointer handling
	•	modality restrictions
	•	metadata normalization
	•	image reference safety constraints
	•	RECIST measurement payload examples and validators
	3.	Real provenance and federated functions
The README claims a federated layer and provenance DAGs  , but this needs runnable code for:
	•	lineage graph creation
	•	integrity verification
	•	cross-site trace merging
	•	privacy budget accounting
	•	site-level federation policy enforcement
	4.	Clinical safety guardrails
For "Physical AI oncology clinical trial systems," add executable policy layers for:
	•	procedure eligibility checks
	•	site capability verification
	•	trial protocol constraints
	•	robot capability gating
	•	mandatory human-approval gates
	•	emergency stop / override semantics
	•	simulation-only mode

6. Strengthen packaging and developer usability

Add
	1.	Proper installable packages and CLIs
The Python project currently declares only basic project metadata and optional test dependencies  . Add:
	•	entry points / CLI scripts
	•	runtime dependencies
	•	extras for FHIR/DICOM/dev/test/docs
	•	versioned release artifacts
	2.	Developer quickstarts
Add:
	•	5-minute local demo
	•	local single-site sandbox
	•	"run first request" example
	•	seeded demo data
	•	sample config bundles for site/sponsor/CRO
	3.	SDKs or starter kits
Add:
	•	Python client
	•	TypeScript client
	•	profile scaffolding tool
	•	policy authoring templates
	•	schema codegen helpers

Fix

The TypeScript package is very minimal: just build and start, with no tests, lint, or publishing shape  . It should become a maintained implementation, not a stub.

7. Tighten governance and documentation for stakeholder trust

Add
	1.	Adoption evidence
To be taken seriously as a national source repo, add:
	•	decision log of accepted/declined changes
	•	implementation status matrix
	•	roadmap with target adopters and milestones
	•	compatibility matrix by version/profile
	•	list of known gaps and non-goals
	•	contribution policy for regulators, vendors, providers, CROs
	2.	Architecture decision records
Explain why:
	•	MCP is the right protocol boundary
	•	these 5 servers were chosen
	•	these 23 tools are the minimal stable surface
	•	profiles map to clinical deployment tiers
	3.	Clear labeling of normative vs informative
The repo already uses those terms in README structure  , but it still needs much sharper boundaries so implementers know what is binding, experimental, or placeholder.

Fix

Revise docs to be more honest about maturity:
	•	"reference implementation" should say "Level 1 illustrative implementation" where applicable
	•	"national standard" should be framed as a proposed standard unless there is multi-stakeholder governance and adoption evidence
	•	separate "current state" from "target state"

Remove

Remove static maturity signals that can be read as proof of broad adoption when they are really repository-local indicators. The README's status badge stack is polished, but several items read more mature than the code currently supports  .

8. Recommended restructuring plan

Phase 1: correctness
	•	fix schema/code/test drift
	•	fix CI gaps
	•	make docs lint fail properly
	•	align field names and examples everywhere

Phase 2: runnable source
	•	add real Python reference servers
	•	add persistence and config
	•	add dockerized deployment
	•	add end-to-end demo

Phase 3: conformance credibility
	•	build black-box harness
	•	generate signed reports
	•	add vendor-targetable test adapters
	•	publish profile certification criteria

Phase 4: stakeholder readiness
	•	add operational runbooks
	•	add governance evidence
	•	add interoperability demos
	•	reduce overclaiming in README until adoption catches up

Bottom line

To be considered by more stakeholders as the source repo for national MCP servers, this repository needs to move from "well-written normative proposal + schemas + fixtures" to "reference standard plus deployable, testable, black-box-verifiable implementation."

The biggest concrete issues today are:
	•	too little runnable code for the breadth of claims
	•	clear schema/code mismatches in core payloads
	•	conformance testing that is still mostly internal/fixture-based rather than deployment-based
	•	CI that does not yet validate the full stated surface area, especially TypeScript and docs correctness

I can turn this into a prioritized gap table with "add / remove / fix / rationale / suggested file changes" format next.





"START FEEDBACK 2"
Below is a practical gap-analysis outline for kevinkawchak/national-mcp-pai-oncology-trials aimed at making it credible to more stakeholders as the source repository for National MCP servers for Physical AI oncology clinical trial systems.
My overall read: the repository is already strong as a normative standard/specification repo with profiles, schemas, governance, and conformance language, but it is still too thin in executable substance to serve as the canonical source most implementers, hospital IT teams, vendors, regulators, and standards bodies would rely on. The repo itself says the implementations are "NON-NORMATIVE reference implementations," and the Python/TypeScript examples are minimal Level-1 stubs rather than deployable national-grade servers    . By contrast, the companion repos already contain much richer operational code for FHIR, DICOM, privacy, agent interfaces, and federated coordination      .
1. Biggest strategic change: make this repo the canonical integration and reference implementation repo, not just the spec repo
What to add
Create a clear two-layer structure:
* Normative layer: current spec/, schemas/, profiles/, regulatory/, governance/
* Reference implementation layer: production-shaped packages for the five MCP servers, integration adapters, deployment manifests, validation tools, and realistic examples
Suggested top-level additions:
* servers/trialmcp_authz/
* servers/trialmcp_fhir/
* servers/trialmcp_dicom/
* servers/trialmcp_ledger/
* servers/trialmcp_provenance/
* integrations/fhir/
* integrations/dicom/
* integrations/ros2/
* integrations/federation/
* deploy/
* examples/
* benchmarks/
* sdk/python/
* sdk/typescript/
What to remove or demote
Keep reference/, but stop presenting it as the main practical implementation surface. The current Python core server is an in-memory Level-1 demo with in-memory token storage and helper functions, not a deployable MCP service  . The TypeScript version is also explicitly a stub  .
Rename or reposition:
* reference/ → examples/minimal-reference/
* badge/README emphasis should move away from "passing conformance tests" toward "reference servers + deployment guides + interoperability testbed"
Why this matters
Stakeholders deciding whether a repo should become a national source will ask:
* Where are the actual servers?
* How do I deploy them?
* What does site integration look like?
* How do I certify and operate them?
Right now the companion repo mcp-pai-oncology-trials looks more like the implementation source because it already has server code and a reference agent  .



2. Promote and consolidate the real server code from
mcp-pai-oncology-trials
The most immediate way to make the national repo substantive is to fold in or vendor the working server code patterns from kevinkawchak/mcp-pai-oncology-trials.
What to add
Port or adapt these into the national repo as the official reference implementation baseline:
* FHIR server patterns from servers/trialmcp_fhir/src/fhir_server.py:
    * read/search/patient lookup/study status
    * de-identification pipeline
    * synthetic bundle loading
    * audit hooks
    * validation/error patterns
* Equivalent DICOM, ledger, authz, provenance server packages from that repo
* The reference robot agent workflow, but rewritten as a national interoperability demo, not a standalone proof of concept
What to fix during import
Do not copy them over unchanged. Harden them.
Examples:
* replace in-memory stores with storage interfaces
* replace direct synthetic-only assumptions with adapter layers
* separate transport, domain logic, policy, and schema validation
* convert server handlers into actual MCP server entrypoints
* add typed models and explicit config management
What to remove
Remove duplicated spec text inside implementation docstrings where possible. Keep implementation code focused on behavior, and point to normative spec sections for requirements.
Why this matters
The FHIR server in the implementation repo already contains more realistic clinical-domain behavior than the national repo's current Level-1 examples, including supported resource types, de-identification, search logic, and audit emission  . That is the substance stakeholders will expect to see in the national source.



3. Expand from "Level 1 Core" examples to all five server implementations and all five conformance levels
The national repo currently highlights Level-1/Core examples and conformance framing, but a national source needs end-to-end implementable paths for all major profiles.
What to add
For each server, provide:
* MCP transport entrypoint
* schema-bound request/response models
* authn/authz middleware
* audit hooks
* health/readiness
* structured errors
* persistence abstraction
* adapter interfaces
* test fixtures
* deployment examples
For each conformance level:
* L1 Core: AuthZ + Ledger
* L2 Clinical Read: FHIR implementation with de-identification
* L3 Imaging: DICOM query/retrieve metadata + RECIST path
* L4 Federated Site: provenance + site federation coordination
* L5 Robot Procedure: safety-gated workflow orchestration and robot/task order execution
What to fix
The current repository has extensive profile language, but too little runnable code behind Levels 2–5. That mismatch weakens credibility with engineering stakeholders.
What to remove
Reduce claims that imply operational completeness where only schema/spec completeness exists.



4. Add real integration adapters, not just abstract contracts
A standards repo becomes practical when it shows how to connect to real systems.
What to add
FHIR adapters
* HAPI FHIR adapter
* generic SMART-on-FHIR/OAuth2 adapter
* synthetic/mock adapter for local testing
* capability statement ingestion
* terminology mapping hooks
DICOM adapters
* Orthanc adapter
* dcm4chee adapter
* study metadata and retrieve-pointer generation
* DICOMweb support path
Identity/security adapters
* OIDC/JWT validation
* mTLS support
* external policy engine integration option
* KMS/HSM-backed signing key hooks
Clinical operations adapters
* eConsent/IRB metadata adapter
* scheduling/task-order adapter
* provenance export adapter
Context from companion repos
The implementation repo already points toward production FHIR and DICOM proxy directions in its milestones; the national repo should absorb that trajectory and make it official rather than leaving it implied  .
Why this matters
Hospitals and vendors will not adopt a "national source" unless they can see a practical bridge from standard to installed systems.



5. Pull in the strongest privacy, regulatory, and governance code from
physical-ai-oncology-trials
 and
pai-oncology-trial-fl
The national repo is strong in policy text, but weaker in operational compliance tooling than the companion repos.
What to add
From physical-ai-oncology-trials:
* reusable privacy modules
* access control manager patterns
* de-identification pipeline patterns
* IRB/FDA/GCP support tools
* deployment readiness checks
* unified agent/tool interface patterns
From pai-oncology-trial-fl:
* federated coordinator abstractions
* secure aggregation hooks
* differential privacy hooks
* site enrollment and data harmonization interfaces
* clinical analytics/reporting patterns where relevant to multi-site trial coordination
What to fix
These should not be copied wholesale into the national repo as broad research modules. They need to be narrowed to what directly supports the MCP national standard.
What to remove
Avoid importing unrelated breadth that turns the national repo into a giant umbrella "all oncology AI" repository. Keep only modules that materially strengthen MCP server operation, interoperability, compliance, or federation.
Why this matters
The FL repo already contains a more substantive multi-site orchestration story than the national repo's current federated layer narrative alone  .



6. Add a true "national interoperability testbed"
Conformance tests are good, but stakeholders will want more than unit-style assertions.
What to add
Create interop-testbed/ with:
* multi-site docker-compose or k8s local cluster
* Site A / Site B / Sponsor / CRO / Auditor personas
* mock EHR/PACS services
* cross-site provenance and audit replay
* token exchange and revocation scenarios
* partial outage scenarios
* schema drift scenarios
* state overlay tests (CA, NY, FDA)
* end-to-end robot workflow simulations
Add test categories:
* conformance
* interoperability
* resilience
* security abuse cases
* site onboarding certification
* upgrade compatibility
* extension compatibility
What to fix
The current conformance suite is useful, but it is still centered on contract validation. National adoption requires proving cross-site behavior, deployment consistency, and failure modes.



7. Add deployment artifacts and operating model docs
A national source repo needs to answer "how do I run this safely?"
What to add
* Dockerfiles for each server
* Helm charts / Kustomize
* reference Kubernetes manifests
* example .env.example and config schemas
* production configuration matrix
* observability stack examples
* log redaction defaults
* key rotation and signing key guidance
* backup/restore and chain recovery procedures
* upgrade playbooks
* site bootstrap scripts
Add docs:
* docs/deployment/local-dev.md
* docs/deployment/hospital-site.md
* docs/deployment/multi-site-federated.md
* docs/operations/runbook.md
* docs/operations/incident-response.md
* docs/operations/key-management.md
What to fix
The current repo is organized like a standard, not like an operable system source. That is fine for a spec repo, but not enough for a canonical national source.



8. Add stakeholder-specific implementation guides
The README speaks broadly to sites, sponsors, CROs, and vendors, but the repository needs role-specific paths.
What to add
Create dedicated guides for:
* Hospital IT / Cancer Center
    * site deployment checklist
    * network and identity requirements
    * PACS/EHR integration path
    * PHI boundary and retention controls
* Robot vendor
    * capability descriptor requirements
    * task-order semantics
    * safety gate expectations
    * simulator-to-clinical promotion path
* Sponsor/CRO
    * cross-site reporting interfaces
    * provenance and audit review
    * state/federal overlay implications
* Regulator/IRB
    * evidence package structure
    * conformance artifacts
    * audit replay package
    * change control and validation package
* Standards community
    * extension proposal process
    * compatibility policy
    * schema evolution rules
What to remove
Reduce generic marketing language that is not paired with actionable stakeholder guidance.



9. Tighten scope and prune claims that exceed current code reality
The repo is ambitious, but some statements read more mature than the implementation appears.
What to fix
Clarify throughout the README and docs:
* what is normative
* what is reference implementation
* what is mock/synthetic only
* what is planned
* what is demonstrated
* what is validated
Examples of likely fixes
* replace "industry standard" tone with "proposed national standard / reference standard" unless there is formal adoption
* distinguish "schema coverage" from "production readiness"
* distinguish "federated architecture defined" from "federated coordination implementation supplied"
What to remove
* any implication that the repo already provides deployable national infrastructure when much of the implementation is still minimal or imported by reference from sibling repos
This is one of the biggest credibility gains available.



10. Add a formal migration and consolidation plan across the four repositories
Right now the value is fragmented:
* national-mcp-pai-oncology-trials = spec/governance/conformance center
* mcp-pai-oncology-trials = most concrete MCP server implementation surface
* physical-ai-oncology-trials = broader robotics, privacy, regulatory, digital twin tooling
* pai-oncology-trial-fl = substantive federation/privacy/regulatory infrastructure
What to add
A docs/repository-strategy.md that says exactly:
* what stays in each repo
* what graduates into the national repo
* what is mirrored vs imported vs referenced
* what becomes deprecated
* what becomes the canonical implementation source
Recommended direction
Make the national repo the canonical home for:
* normative artifacts
* official server implementations
* official testbed
* official deployment patterns
* official SDKs
* official examples
Leave the other repos as:
* research incubators
* broader frameworks
* companion experiments
* upstream module sources until stabilized



11. Add versioned SDKs and generated client/server bindings
A national standard becomes more adoptable when people can generate against it.
What to add
* Python SDK
* TypeScript SDK
* generated schema bindings
* server scaffolding CLI
* profile-aware code generation
* example clients for each actor role
Suggested outputs:
* typed request/response classes from schemas
* client stubs for 23 tools
* policy templates
* example middleware for auth/audit/error handling
What to fix
The current TypeScript code is mainly a small stub around AJV validation and helper functions  . That should evolve into a usable SDK and server starter kit.



12. Add benchmark, validation, and evidence-pack generation
National stakeholders will want objective evidence, not only passing tests.
What to add
* latency and throughput benchmarks by server/tool
* conformance report generator
* site certification report generator
* evidence pack generator for IRB/FDA/internal compliance review
* schema compatibility diff tool
* audit chain integrity report exporter
* provenance graph exporter
Borrow from companion repos
The FL repo already has stronger notions of coordinator summaries and operational reporting patterns that can inform evidence generation  .



13. Add robot-facing safety and execution boundaries
Because this is for Physical AI, not just software agents, the national source needs more explicit execution-control substance.
What to add
* safety gate service or policy layer
* robot capability registry
* task-order validator with safety constraints
* human-approval checkpoint patterns
* e-stop and abort semantics
* procedure-state machine
* simulation-only vs clinical-mode flags
* precondition verification contracts
* post-procedure evidence capture contracts
Context from companion repos
The physical-ai repo's unified agent/tool patterns and robotics-oriented tool abstractions are useful starting points for this layer, even if many are still mock-like today  .
What to fix
Right now "robot procedure" appears more strongly in the standard language than in the codebase substance.



14. Improve documentation quality by replacing breadth with adoption-grade depth
The repo already has a lot of docs. The problem is not volume; it is that some key docs need to become more operational.
Highest-value docs to add or rewrite
* architecture decision records
* one complete walkthrough per profile
* "how a hospital site goes live"
* "how a vendor becomes conformant"
* "how a CRO validates a multi-site deployment"
* "how schemas map to running services"
* "how to extend without breaking national compatibility"
* "what data may never leave site boundaries"
* "how audit/provenance differ and interact"
What to remove
Reduce repetitive diagrams and README-level summary material once deeper docs exist. Replace some broad narrative with precise onboarding sequences.



15. Add stronger software engineering hygiene around the implementation layer
What to add
* package boundaries and dependency rules
* typed configs
* migration/version upgrade tests
* fuzz/property tests for schema edges
* secret scanning
* SBOM generation
* signed releases
* release provenance
* compatibility matrix by version/profile
What to fix
The national repo's CI and conformance messaging are good, but the implementation layer needs production software practices once real servers are brought in.



16. A concrete prioritized roadmap
Phase 1: make the repo believable as the national implementation source
* import and harden the five real server packages from mcp-pai-oncology-trials
* add deployment artifacts
* add integration adapters
* add multi-site testbed
* rewrite README to distinguish spec vs implementation
Phase 2: make it adoptable by institutions
* add SDKs
* add stakeholder guides
* add certification/evidence tooling
* add config/deployment/runbook docs
* add hospital/vendor reference deployments
Phase 3: make it governable as a national standard source
* formal repository strategy across sibling repos
* extension registry process
* compatibility guarantees
* versioned implementation baselines
* deprecation policy for non-canonical sibling components



17. The shortest honest summary
To be considered by more stakeholders as the source for national MCP servers, this repository needs to evolve from:
* excellent standard/specification repo
into
* standard + canonical reference implementation + deployment + interoperability + evidence repo
The fastest path is not to invent all of that from scratch here. It is to promote, narrow, harden, and consolidate the strongest implementation pieces already present in:
* kevinkawchak/mcp-pai-oncology-trials for the MCP servers and workflow surface
* kevinkawchak/physical-ai-oncology-trials for privacy/regulatory/agentic/robotics integration patterns
* kevinkawchak/pai-oncology-trial-fl for federation, privacy, secure aggregation, and reporting infrastructure
At the moment, the national repo looks like the right governance/spec home, but not yet the strongest implementation home. That is the core issue to fix.
I can turn this into a sharper deliverable next, such as a repo-by-repo migration matrix or a proposed new directory tree with file-level recommendations.

---

## Prompt v0.5.1

Perform tests and fix code for national-mcp-pai-oncology-trials based on the following verifications and other comprehensive checks/tests repository wide. Make note of any changes made throughout relevant documentation. If necessary, create a new directory(s) on main.:
1. pytest tests/ — All 39 existing tests still pass (no existing code modified)
2. pytest conformance/ — Conformance suite runs against reference implementation
3. python reference/python/schema_validator.py — All schemas validate
4. Every /spec/ file uses RFC 2119 MUST/SHOULD/MAY
5. Every /reference/ file labeled NON-NORMATIVE
6. .github/workflows/ci.yml executes successfully
7. prompts.md contains all 5 new prompts with comprehensive instructions
8. Each version has releases.md entry and changelog.md entry

Provide a copy of this exact prompt under main prompts.md. Be sure to fix and address errors that would cause failed checks for the single pull request (such as Python environment issues to avoid the following error during final checks): "3 failing checks
x Cl / lint-and-format (3.10) (pull...
x Cl / lint-and-format (3.11) (pull...
x Cl / lint-and-format (3.12) (pull... " Place the new release notes in releases.md under main using the format below (which is the same format of the last published version). Update changelog.md using v0.5.1. When you are finished, auto-push the update to GitHub on your own for my review. The user will then review your updates in GitHub prior to finalization.

"FORMAT"
Release title
v0.5.1 -

## Summary

## Features

## Contributors
@kevinkawchak
@claude

## Notes

---

## Prompt v0.5.0

Your goal in the comprehensive national-mcp-pai-oncology-trials v0.5.0 release is to continue scaling to a United States national industry-wide MCP standard for the physical ai oncology trials industry based in part from the prior kevinkawchak/mcp-pai-oncology-trials. It is important that only directories/files/modified files be used that are truly useful on the national scale rather than the prior repository being used as a reference implementation / seed specification.

Update national specific documentation throughout the repo (diagrams, mermaid diagrams, text, repository structure, etc.) After completing these tasks, focus on performing the main prompt below exhaustively for the national level (Keep in mind that this prompt, and future prompts are aimed at MCP servers being fully scaled and automated industry wide across the U.S.)


It is imperative that all types of information now utilized from across the prior repository be accurate and appropriate to a national scale. For references: use the three references at the bottom of the main kevinkawchak/mcp-pai-oncology-trials Readme; and exact working internal and external sites URLs where necessary from kevinkawchak/physical-ai-oncology-trials and kevinkawchak/pai-oncology-trial-fl.

Provide a copy of this exact prompt under main prompts.md. Be sure to fix and address errors that would cause failed checks for the single pull request (such as Python environment issues to avoid the following error during final checks): "3 failing checks
x Cl / lint-and-format (3.10) (pull...
x Cl / lint-and-format (3.11) (pull...
x Cl / lint-and-format (3.12) (pull... " Place the new release notes in releases.md under main using the format below (which is the same format of the last published version). Update changelog.md using v0.5.0. When you are finished, auto-push the update to GitHub on your own for my review. The user will then review your updates in GitHub prior to finalization.

"FORMAT"
Release title
v0.5.0 -

## Summary

## Features

## Contributors
@kevinkawchak
@claude

## Notes

"START MAIN PROMPT"
(v0.5.0): Reference Implementations + CI/CD + Documentation
Creates: /reference/python/, /reference/typescript/, .github/workflows/ci.yml, /docs/ (3 files), updated README.md
* reference/python/ — NON-NORMATIVE. Minimal Core server, schema validator, conformance runner.
* reference/typescript/ — NON-NORMATIVE. Minimal Core server stub with ajv validation.
* .github/workflows/ci.yml — Lint (ruff), test (pytest), schema validation, conformance suite, docs linting.
* docs/architecture.md — 5-server topology, data flow, audit chain (ASCII diagrams).
* docs/adoption-roadmap.md — Phase 0 (spec) → Phase 1 (profiles) → Phase 2 (conformance) → Phase 3 (pilots).
* docs/glossary.md — Standard terminology.
* Updated README.md — Repository layout section, normative vs informative labels, CI badges.
"END PROMPT"

---

## Prompt v0.4.0

Your goal in the comprehensive national-mcp-pai-oncology-trials v0.4.0 release is to continue scaling to a United States national industry-wide MCP standard for the physical ai oncology trials industry based in part from the prior kevinkawchak/mcp-pai-oncology-trials. It is important that only directories/files/modified files be used that are truly useful on the national scale rather than the prior repository being used as a reference implementation / seed specification.

Update national specific documentation throughout the repo (diagrams, mermaid diagrams, text, repository structure, etc.) After completing these tasks, focus on performing the main prompt below exhaustively for the national level (Keep in mind that this prompt, and future prompts are aimed at MCP servers being fully scaled and automated industry wide across the U.S.)

It is imperative that all types of information now utilized from across the prior repository be accurate and appropriate to a national scale. For references: use the three references at the bottom of the main kevinkawchak/mcp-pai-oncology-trials Readme; and exact working internal and external sites URLs where necessary from kevinkawchak/physical-ai-oncology-trials and kevinkawchak/pai-oncology-trial-fl.

Provide a copy of this exact prompt under main prompts.md. Be sure to fix and address errors that would cause failed checks for the single pull request (such as Python environment issues to avoid the following error during final checks): "3 failing checks
x Cl / lint-and-format (3.10) (pull...
x Cl / lint-and-format (3.11) (pull...
x Cl / lint-and-format (3.12) (pull... " Place the new release notes in releases.md under main using the format below (which is the same format of the last published version). Update changelog.md using v0.4.0. When you are finished, auto-push the update to GitHub on your own for my review. The user will then review your updates in GitHub prior to finalization.

"FORMAT"
Release title
v0.4.0 -

## Summary

## Features

## Contributors
@kevinkawchak
@claude

## Notes

"START MAIN PROMPT"
(v0.4.0): Conformance Test Suite
Creates: /conformance/ (README + conftest + fixtures + 4 test directories with actual test files)
* conformance/README.md — Harness overview, how to run, how to add tests
* conformance/conftest.py — Shared fixtures, schema validation helpers
* conformance/fixtures/ — Extracted from datasets/
* conformance/positive/test_core_conformance.py — Audit production, error envelope, health, authz (from tests/audit/)
* conformance/positive/test_clinical_read_conformance.py — FHIR + de-identification (from tests/integration/)
* conformance/positive/test_imaging_conformance.py — DICOM conformance
* conformance/negative/test_invalid_inputs.py — Malformed requests, schema mismatches
* conformance/negative/test_unauthorized_access.py — Deny-by-default (from tests/security/TestPermissionEscalation)
* conformance/security/test_ssrf_prevention.py — URL injection (from tests/security/TestSSRFPrevention)
* conformance/security/test_token_lifecycle.py — Expiry, revocation
* conformance/security/test_chain_integrity.py — Hash chain tampering
* conformance/interoperability/test_cross_server_trace.py — Multi-server audit linkage (from tests/integration/)
* conformance/interoperability/test_schema_validation.py — All outputs validated against /schemas/
"END PROMPT"

---

## Prompt v0.3.0

Your goal in the comprehensive national-mcp-pai-oncology-trials v0.3.0 release is to continue scaling to a United States national industry-wide MCP standard for the physical ai oncology trials industry based in part from the prior kevinkawchak/mcp-pai-oncology-trials. It is important that only directories/files/modified files be used that are truly useful on the national scale rather than the prior repository being used as a reference implementation / seed specification.

Update national specific documentation throughout the repo (diagrams, mermaid diagrams, text, repository structure, etc.) After completing these tasks, focus on performing the main prompt below exhaustively for the national level (Keep in mind that this prompt, and future prompts are aimed at MCP servers being fully scaled and automated industry wide across the U.S.)

It is imperative that all types of information now utilized from across the prior repository be accurate and appropriate to a national scale. For references: use the three references at the bottom of the main kevinkawchak/mcp-pai-oncology-trials Readme; and exact working internal and external sites URLs where necessary from kevinkawchak/physical-ai-oncology-trials and kevinkawchak/pai-oncology-trial-fl.

Provide a copy of this exact prompt under main prompts.md. Be sure to fix and address errors that would cause failed checks for the single pull request (such as Python environment issues to avoid the following error during final checks): "3 failing checks
x Cl / lint-and-format (3.10) (pull...
x Cl / lint-and-format (3.11) (pull...
x Cl / lint-and-format (3.12) (pull... " Place the new release notes in releases.md under main using the format below (which is the same format of the last published version). Update changelog.md using v0.3.0. When you are finished, auto-push the update to GitHub on your own for my review. The user will then review your updates in GitHub prior to finalization.

"FORMAT"
Release title
v0.3.0 -

## Summary

## Features

## Contributors
@kevinkawchak
@claude

## Notes

"START MAIN PROMPT"
(v0.3.0): Profiles and Conformance Level Definitions
Creates: /profiles/ (8 markdown files)
* base-profile.md — Core conformance: authz + audit + error taxonomy. Every implementation MUST.
* clinical-read.md — FHIR read/search + HIPAA de-identification. MUST: fhir_read, fhir_search, fhir_patient_lookup, fhir_study_status.
* imaging-guided-oncology.md — DICOM query/retrieve + role-based modality restrictions. MUST: CT, MR, PT. SHOULD: RTSTRUCT, RTPLAN.
* multi-site-federated.md — Cross-site provenance, federated audit chain, data residency policy.
* robot-assisted-procedure.md — Robot capability profile, task-order contract, safety matrix, USL scoring. References schemas.
* state-us-ca.md — California CCPA overlay.
* state-us-ny.md — New York health info overlay.
* country-us-fda.md — FDA 21 CFR Part 11 overlay.
Each profile: mandatory tools, optional tools, forbidden ops, required schemas, regulatory overlays, conformance test subset.
"END PROMPT"

---

## Prompt v0.2.0

Include more Readme badges such as version, language(s), tests, protocol, date, and contributors. Update national specific documentation throughout the repo (diagrams, mermaid diagrams, text, repository structure, etc.) After completing these tasks, focus on performing the main prompt below exhaustively for the national level (Keep in mind that this prompt, and future prompts are aimed at MCP servers being fully scaled and automated industry wide across the U.S.)

It is imperative that all types of information now utilized from across the prior repository be accurate and appropriate to a national scale. For references: use the three references at the bottom of the main kevinkawchak/mcp-pai-oncology-trials Readme; and exact working internal and external sites URLs where necessary from kevinkawchak/physical-ai-oncology-trials and kevinkawchak/pai-oncology-trial-fl.

Provide a copy of this exact prompt under main prompts.md. Be sure to fix and address errors that would cause failed checks for the single pull request (such as Python environment issues to avoid the following error during final checks): "3 failing checks
x Cl / lint-and-format (3.10) (pull...
x Cl / lint-and-format (3.11) (pull...
x Cl / lint-and-format (3.12) (pull... " Place the new release notes in releases.md under main using the format below (which is the same format of the last published version, don't use the format from releases.md). Update changelog.md using v0.2.0. When you are finished, auto-push the update to GitHub on your own for my review. The user will then review your updates in GitHub prior to finalization.

"FORMAT"
Release title
v0.2.0 -

## Summary

## Features

## Contributors
@kevinkawchak
@claude

## Notes

"START MAIN PROMPT"
(v0.2.0): Machine-Readable JSON Schemas
Creates: /schemas/ (13 JSON Schema files)
Each schema extracted from existing server code structures:
* capability-descriptor.schema.json — Server capability ad (name, version, tools, conformance level)
* robot-capability-profile.schema.json — From trial_robot_agent.py (platform, robot_type) + trial_schedule.json (usl_score, safety prerequisites)
* site-capability-profile.schema.json — Site descriptor (jurisdiction, servers, data residency)
* task-order.schema.json — From datasets/scheduling/trial_schedule.json structure
* audit-record.schema.json — From ledger_server.py AuditRecord dataclass fields
* provenance-record.schema.json — From provenance_server.py ProvenanceRecord fields
* consent-status.schema.json — Consent state machine
* authz-decision.schema.json — From authz_server.py evaluate return shape
* dicom-query.schema.json — From dicom_server.py dicom_query params/output
* fhir-read.schema.json — From fhir_server.py fhir_read params/output
* fhir-search.schema.json — From fhir_server.py fhir_search params/output
* error-response.schema.json — From servers/common/__init__.py error_response()
* health-status.schema.json — From servers/common/__init__.py health_status()
All use JSON Schema draft 2020-12 with $id, title, description, required, examples.
"END PROMPT"

---

## Prompt v0.1.0

Your goal in the new comprehensive national-mcp-pai-oncology-trials v0.1.0 release is to scale to a United States national industry-wide MCP standard for the physical ai oncology trials industry based in part from the prior kevinkawchak/mcp-pai-oncology-trials. It is important that only directories/files/modified files be used that are truly useful on the national scale rather than the prior repository being used as a reference implementation / seed specification.

Create national specific documentation throughout the repo; the main readme needs to be disbursed with the following throughout: 3 relevant text diagrams and 3 relevant colored mermaid diagrams (make sure mermaid diagrams view well on smartphones, and don't require excessive pan/zoom due to being too long in one dimension). State the features and benefits of this national approach opposed to the prior kevinkawchak/mcp-pai-oncology-trials repository, existing oncology trial approaches, and other known MCP/AI software servers approaches for oncology trials. After completing these tasks, focus on performing the main prompt below exhaustively for the national level (Keep in mind that this prompt, and future prompts are aimed at MCP servers being fully scaled and automated industry wide across the U.S.)

"START MAIN PROMPT"
(v0.1.0): Normative Specification + Governance + Regulatory Overlays + Community Files
Creates: /spec/ (9 files), /governance/ (5 files), /regulatory/ (4 files), .github/ (templates), CODE_OF_CONDUCT.md
Key spec files and their source material from existing code:
* spec/core.md — Protocol scope, design principles, 5 conformance levels (Core, Clinical Read, Imaging, Federated Site, Robot Procedure). Uses RFC 2119 MUST/SHOULD/MAY.
* spec/actor-model.md — 6 actors extracted from servers/trialmcp_authz/src/authz_server.pyDEFAULT_POLICY roles (robot_agent, trial_coordinator, data_monitor, auditor) plus sponsor and CRO.
* spec/tool-contracts.md — All 23 tool signatures from the 5 servers' handle_tool_call methods, with input params, output shape, error codes, and audit requirements.
* spec/security.md — Deny-by-default RBAC from authz_server.py PolicyEngine, token lifecycle, SSRF prevention from servers/common/__init__.py validators.
* spec/privacy.md — HIPAA Safe Harbor de-identification from fhir_server.py _deidentify_resource(), HMAC-SHA256 pseudonymization, DICOM patient hashing from dicom_server.py.
* spec/provenance.md — DAG lineage model from provenance_server.py DataSource/ProvenanceRecord, SHA-256 fingerprinting, forward/backward queries.
* spec/audit.md — Hash-chained ledger from ledger_server.py, genesis hash, chain verification, replay trace, 21 CFR Part 11 mapping.
* spec/conformance.md — 5 conformance levels with MUST/SHOULD/MAY per level, mandatory tool sets per level.
* spec/versioning.md — SemVer, compatibility policy, extension namespace x-{vendor}, deprecation rules.
* governance/CHARTER.md, DECISION_PROCESS.md, EXTENSIONS.md, VERSION_COMPATIBILITY.md, CODEOWNERS
* regulatory/US_FDA.md, HIPAA.md, CFR_PART_11.md, IRB_SITE_POLICY_TEMPLATE.md
* .github/ISSUE_TEMPLATE/bug_report.md, feature_request.md, spec_change.md; .github/PULL_REQUEST_TEMPLATE.md
* CODE_OF_CONDUCT.md (Contributor Covenant)
"END PROMPT"

It is imperative that all types of information now utilized from across the prior repository be accurate and appropriate to a national scale. For references: use the three references at the bottom of the main kevinkawchak/mcp-pai-oncology-trials Readme; and exact working internal and external sites URLs where necessary from kevinkawchak/physical-ai-oncology-trials and kevinkawchak/pai-oncology-trial-fl.

Provide a copy of this prompt under main prompts.md. Be sure to fix and address errors that would cause failed checks for the single pull request (such as Python environment issues to avoid the following error during final checks): "3 failing checks
x Cl / lint-and-format (3.10) (pull...
x Cl / lint-and-format (3.11) (pull...
x Cl / lint-and-format (3.12) (pull... " Place the new release notes in releases.md under main using the format below. Update changelog.md using v0.1.0. When you are finished, auto-push the update to GitHub on your own for my review. The user will then review your updates in GitHub prior to finalization.

"FORMAT"
Release title
v0.1.0 -

## Summary

## Features

## Contributors
@kevinkawchak
@claude

## Notes
