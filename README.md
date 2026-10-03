# Adobe Journey Simulation Engine
## Synthetic Customer, Event-State, Coverage, Policy and Journey Optimization Reference Platform

## Current Adobe context

Adobe Journey Optimizer now documents Journey Simulation as generally available. Adobe's current documentation describes Quick Simulation and Manual Simulation, simulated users, AI-generated users/event values, path/result inspection, and Journey Agent-assisted simulation. 

## Comprehensive contents

This README covers the executable code, journey compiler, synthetic users, deterministic state machine, parallel execution, path/drop-off/fatigue/conversion/policy analysis, Quick and Manual simulation architecture, virtual time, event generation, branch coverage, constraint solving, distributed execution, durable state, idempotency, outbox, checkpointing, cancellation, multi-tenancy, privacy, security, observability, capacity planning, Kubernetes, CI/CD, testing, failure recovery, operational runbooks, production gaps and Principal-level design tradeoffs.


## Architecture

```text
Journey Definition
       |
       v
Journey Parser / Validator
       |
       v
Simulation Compiler
       |
       +--------------------+
       |                    |
       v                    v
Synthetic Users       Synthetic Events
       |                    |
       +---------+----------+
                 |
                 v
       Parallel Simulation Engine
                 |
         Event / State Engine
                 |
      +----------+----------+
      |          |          |
   Traversal   Messages  Conversions
      |          |          |
      +----------+----------+
                 |
                 v
       Analysis / Validation
        |    |     |     |
        v    v     v     v
     Paths Dropoff Fatigue Policy
                 |
                 v
       Optimization Findings
```

## What the source code actually implements

- typed journey graph;
- journey compiler and graph validation;
- missing-edge validation;
- cycle rejection for the reference execution model;
- synthetic customer generation;
- persona attributes;
- deterministic condition evaluation;
- parallel user execution;
- start/condition/message/wait/event/conversion/end node model;
- node traversal events;
- path analysis;
- conversion-rate calculation;
- drop-off detection;
- simple channel-fatigue detection;
- consent-policy validation;
- FastAPI simulation endpoint;
- PostgreSQL domain schema for future durable runs/traversals/findings;
- Docker Compose;
- tests;
- sample journey;
- operational runbook.

## Repository structure

```text
app/
  main.py
  api.py
  domain.py
  compiler.py
  personas.py
  expressions.py
  engine.py
  analyzers.py
  policy.py
  service.py
  security.py
  models.py
  db.py
  config.py
examples/
  journey.json
tests/
docs/
Dockerfile
docker-compose.yml
pyproject.toml
```

## Core concept 1 — Journey definition

A journey is a directed graph.

```text
Node = business state/activity
Edge = possible transition
Condition = predicate controlling an edge
```

Example:

```text
Start
 |
 +-- tier=gold --> VIP Email --> Conversion?
 |
 +-- otherwise --> Push --> Wait --> SMS --> End
```

The API uses a typed representation so malformed structures fail before execution.

## Core concept 2 — Simulation compiler

`compiler.py` converts the declarative journey into a fast in-memory representation.

It validates:
- start node exists;
- every edge targets an existing node;
- the reference graph is acyclic.

Why compile first?

```text
authoring representation
        |
validation/normalization
        |
executable representation
```

A real AJO-scale simulator would support additional constructs such as bounded loops, jumps, event waits, decisioning, schedules, timeouts and external actions. Those require explicit simulation semantics rather than blindly invoking production systems.

## Core concept 3 — Synthetic customers

`personas.py` generates temporary customers from persona specifications.

Example:

```json
{
  "name":"Gold engaged",
  "count":10,
  "attributes":{
    "tier":"gold",
    "engagement_score":0.9,
    "consent":true
  }
}
```

Production generation should optimize for **coverage**, not merely random realism.

Useful generation strategies:

```text
branch coverage
boundary-value coverage
pairwise attribute coverage
historical-distribution sampling
risk-focused personas
rare-segment generation
adversarial personas
```

LLM-generated profiles must be schema validated before simulation.

## Core concept 4 — Event/state engine

Each simulated customer has independent state:

```text
current node
attributes
event values
messages encountered
conversion state
traversal history
```

`engine.py` walks the compiled graph and records `ENTER` and `DROP_OFF` events.

A production implementation should use a virtual clock so a 30-day journey can execute in seconds without changing logical ordering.

## Core concept 5 — Conditions

`expressions.py` implements deterministic predicates:

```text
eq
ne
gt
gte
lt
in
```

This is deliberately deterministic. A model may propose values, but the journey condition evaluator should not ask an LLM whether `age > 25` is true.

## Core concept 6 — Parallel simulation

Customers are independent units of simulation and therefore naturally parallelizable.

Reference:

```text
asyncio.gather()
     +
semaphore
```

At large scale:

```text
Simulation API
   |
SQL + Outbox
   |
Kafka/Pulsar
   |
partitioned worker fleet
   |
event/traversal store
```

Partition by simulation/run/customer while preserving per-user ordering.

## Core concept 7 — Drop-off analysis

A user drops when no outgoing edge matches.

This can reveal:
- missing default branch;
- bad synthetic data;
- unexpected null;
- impossible condition combination;
- journey logic defect.

The analyzer reports aggregate drop-off rate.

## Core concept 8 — Fatigue detection

The reference analyzer flags repeated channel contact.

Production fatigue analysis should consider:

```text
channel
rolling time window
campaign/journey overlap
priority
customer preference
quiet hours
frequency caps
recent real contacts
```

Simulation policy and production enforcement are different things. Never imply a simulator has enforced a live policy unless it actually does.

## Core concept 9 — Conversion analysis

The engine marks traversal of a conversion node.

Production analysis can compute:

```text
conversion probability
time-to-conversion
path conversion
persona conversion
incremental lift hypotheses
drop-off before conversion
```

Simulation results are not causal evidence unless the underlying model/design supports causal inference.

## Core concept 10 — Policy validation

The reference policy flags message activity for a synthetic user with `consent=false`.

A mature policy engine can validate:
- consent assumptions;
- quiet hours;
- contact pressure;
- geographic restrictions;
- required approvals;
- forbidden channel/persona combinations;
- brand rules.

Policy simulation should clearly distinguish modeled rules from the actual live enforcement behavior of Adobe or another provider.

## Conflict detection

Cross-journey conflict detection requires multiple journeys.

Examples:

```text
same customer receives competing offers
two journeys update incompatible state
two messages arrive simultaneously
one journey suppresses another
shared budget is exceeded
```

Production architecture:

```text
Journey A ----\
Journey B -----+--> Timeline Merger --> Conflict Rules
Journey C ----/
```

The current single-journey code provides the traversal data model needed for this extension.

## Content simulation

A content simulator should render channel content against synthetic profile attributes.

```text
template
 + persona
 + decision/offer
 -> rendered variant
 -> validation
```

Checks can include:
- missing personalization;
- broken variables;
- invalid links;
- brand policy;
- length;
- accessibility;
- locale;
- unsafe content.

Do not send real email/SMS/push from a pure simulator by default.

## Virtual time

Production journey simulation should not `sleep(7 days)`.

Use:

```text
real time        virtual time
10:00            day 0
10:01            day 3
10:02            day 14
```

Maintain a priority queue ordered by simulated timestamp.

This makes waits, timeouts, contact pressure and event timing testable.

## Event generation

For event-triggered journeys:

```text
Synthetic User
    |
Synthetic Event Generator
    |
validated event payload
    |
virtual event bus
    |
journey state machine
```

Generation should derive required fields from the journey/event schema.

## Coverage engine

Coverage is one of the most important production features.

Metrics:

```text
node coverage
edge coverage
branch coverage
condition coverage
persona coverage
event coverage
content variant coverage
```

Algorithm:

```text
compile graph
enumerate feasible branches
identify uncovered paths
generate persona/event constraints
solve/generate candidate test users
run
repeat until target coverage or budget
```

For complex expressions, constraint solving can outperform naive random generation.

## Journey Agent integration

An agent can sit above deterministic simulation:

```text
Journey Agent
     |
understand journey
     |
generate simulation plan
     |
generate personas/events
     |
Simulation Engine
     |
structured results
     |
Agent explanation/recommendation
```

The agent should not fabricate execution results. Recommendations should consume structured simulator output.

## Optimization recommendation engine

Inputs:
- path coverage;
- drop-off;
- fatigue;
- conversion;
- policy findings;
- conflicts;
- latency/waits.

Output:
```text
finding
evidence
affected path
severity
recommended change
expected tradeoff
confidence/source
```

Recommendations should remain proposals until a user or governed automation changes a journey.

## Durable data model

Included SQL models:

### SimulationRun
Stores tenant, journey snapshot, status and summary.

### SimulatedUser
Stores persona/attributes and execution state.

### Traversal
Stores ordered node events.

### Finding
Stores structured issues/evidence.

Production additions:

```text
journey_versions
simulation_configs
event_payloads
content_variants
coverage_records
conflicts
recommendations
artifacts
task_attempts
outbox_events
audit_events
```

## State machine

Recommended run state:

```text
CREATED
  |
COMPILING
  |
GENERATING_USERS
  |
READY
  |
RUNNING
 / |  \
v  v   v
OK FAILED CANCELLED
 |
ANALYZING
 |
COMPLETED
```

Worker/task state should be separate from overall run state.

## Idempotency

Starting a simulation should support an idempotency key:

```text
tenant + journey version + simulation config + client key
```

This prevents accidental duplicate expensive runs.

The small reference API can be extended with the same durable idempotency pattern used by workflow systems.

## Reproducibility

Random synthetic generation complicates debugging.

Production runs should persist:

```text
random seed
journey version/hash
generator version
policy version
simulation-engine version
persona definitions
event definitions
```

A bug report should be reproducible.

## Determinism

Separate:
- deterministic graph execution;
- stochastic customer/event generation;
- stochastic decisioning/model behavior.

Persist seeds and decision inputs wherever feasible.

## Multi-tenancy

Tenant boundaries apply to:
- runs;
- journeys;
- personas;
- findings;
- artifacts;
- quotas;
- logs.

Never accept a client-supplied tenant identifier as trusted identity in production. Derive it from authenticated enterprise identity.

## Security

Threats:
- malicious journey expressions;
- prompt injection in content;
- oversized graphs;
- simulation resource exhaustion;
- sensitive synthetic data;
- accidental real sends;
- cross-tenant access;
- SSRF through external-action nodes;
- generated-code execution.

Mitigations:
- typed schema;
- graph size limits;
- expression allowlist;
- sandbox;
- quotas;
- egress denial by default;
- fake channel adapters;
- workload identity;
- data classification;
- audit.

## Safety boundary for channel actions

Simulation must not accidentally become production execution.

Recommended interface:

```text
ChannelPort
  |
  +-- SimulationEmailAdapter -> capture artifact
  +-- SimulationSMSAdapter   -> capture artifact
  +-- SimulationPushAdapter  -> capture artifact
```

Production credentials should not be mounted into simulation workers unless an explicitly governed proof-send feature requires them.

## Observability

Trace:

```text
simulation.create
simulation.compile
persona.generate
user.execute
node.evaluate
edge.select
finding.compute
report.build
```

Metrics:

```text
simulations_total
simulation_duration
users_simulated
nodes_evaluated
branch_coverage
dropoff_rate
findings_total
worker_queue_depth
worker_failures
```

Use OpenTelemetry and avoid customer PII in labels.

## Scale architecture

```text
API / Control Plane
        |
Distributed SQL/Postgres
        |
Transactional Outbox
        |
Kafka
        |
+-------+-------+-------+
|       |       |       |
Worker Worker Worker Worker
|       |       |       |
+-------+-------+-------+
        |
Traversal/Event Store
        |
Analysis Workers
        |
Report/Recommendation Store
```

Stateless API and workers scale horizontally.

## Partitioning

A useful key is:

```text
simulation_run_id + simulated_user_id
```

Events for one user must retain ordering.

Aggregate analysis can be parallel map/reduce.

## Backpressure

Limit:
- active simulations/tenant;
- users/run;
- concurrent users;
- nodes/user;
- generated content;
- artifacts;
- execution duration.

Reject or queue excess load instead of allowing unbounded fan-out.

## Failure recovery

Persist checkpoints such as:

```text
user
current node
virtual timestamp
attributes
event cursor
traversal sequence
```

A worker can resume rather than restart an expensive simulation.

## Exactly-once

Pure deterministic in-process simulation can be replayed safely.

But distributed persistence still requires idempotent writes.

Use:
```text
unique(run,user,sequence)
idempotent consumers
transactional outbox
```

## API

### Health

```bash
curl http://localhost:8000/health
```

### Run simulation

```bash
curl -X POST http://localhost:8000/v1/simulations \
  -H 'Content-Type: application/json' \
  -H 'x-api-key: change-me' \
  --data-binary @examples/journey.json
```

Response contains:
- generated users;
- per-user traversal;
- messages;
- conversion state;
- aggregate summary;
- findings.

## Full local run instructions

### Prerequisites

```text
Docker
Docker Compose
optional Python 3.11+
curl
```

### Configure

```bash
cp .env.example .env
```

### Build/start

```bash
docker compose build
docker compose up -d
docker compose ps
```

### Health

```bash
curl http://localhost:8000/health
```

### Execute sample

```bash
curl -X POST http://localhost:8000/v1/simulations \
 -H 'x-api-key: change-me' \
 -H 'Content-Type: application/json' \
 --data-binary @examples/journey.json
```

### Logs

```bash
docker compose logs -f api
docker compose logs -f postgres
docker compose logs -f redis
```

### Database

```bash
docker compose exec postgres psql -U postgres -d sim
```

### Stop

```bash
docker compose down
```

Delete local data intentionally:

```bash
docker compose down -v
```

## Host Python development

```bash
docker compose up -d postgres redis

python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Change `.env` hosts to `localhost`.

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://localhost:8000/docs
```

## Tests

```bash
pytest -q
ruff check .
```

Tests cover graph compilation and expression semantics.

Production suites should add:
- malformed graph;
- cycles;
- branch boundaries;
- nulls;
- large graph;
- concurrency;
- deterministic seed;
- fatigue;
- policy;
- virtual clock;
- recovery;
- tenant isolation;
- load tests.

## Production CI/CD

```text
lint
unit tests
property tests
graph fuzzing
integration tests
security scan
SBOM
container build
container scan/sign
staging simulation corpus
performance regression
progressive deploy
```

## Property-based testing

Journey engines are excellent candidates for property tests.

Examples:
```text
every traversal references an existing node
sequence is monotonic
a terminal user cannot execute another node
one condition evaluation cannot mutate profile state
same seed + same inputs => same deterministic result
```

## Graph fuzzing

Generate random valid/invalid graphs to detect:
- infinite execution;
- stack blowup;
- malformed edges;
- path explosion;
- expression crashes.

## Performance model

Approximate work:

```text
users × average nodes traversed
```

10,000 users × 30 nodes = 300,000 node evaluations.

Content rendering, model calls and external decisioning can dominate CPU graph evaluation.

## Path explosion

A journey with many branches can have exponentially many theoretical paths.

Do not enumerate all paths blindly.

Use:
- coverage budget;
- constraint solving;
- risk-weighted branch selection;
- pairwise testing;
- adaptive generation.

## Synthetic-data privacy

Synthetic does not automatically mean safe.

Avoid training/generating personas that reconstruct real individuals.

Use:
- statistical constraints;
- data minimization;
- privacy review;
- no raw production PII unless explicitly governed.

## Comparison with dry run/test mode

Conceptually:

```text
Simulation:
synthetic/temporary test entities, modeled execution

Test mode:
controlled test profiles through journey testing semantics

Dry run:
evaluate against real production audience/data while suppressing customer contact/state changes
```

Exact product behavior should follow current Adobe documentation.

## Adobe-aligned design observations

Current Adobe documentation describes:
- Quick and Manual simulation;
- simulated users;
- AI-generated users;
- generated event values;
- path/result inspection;
- Journey Agent integration.

The repository maps those concepts into a general distributed-systems architecture while adding portfolio-level extensions such as coverage optimization, policy analysis, fatigue detection, virtual time, durable workers and conflict analysis.

## Production-readiness checklist

Identity:
- enterprise OIDC/workload identity
- tenant derivation
- RBAC/ABAC

Data:
- migrations
- encryption
- retention
- synthetic-data policy

Engine:
- virtual clock
- bounded loops
- event scheduler
- deterministic seeds
- checkpoint/recovery
- cancellation

Scale:
- queue
- workers
- outbox
- idempotent events
- quotas
- backpressure

Analysis:
- coverage engine
- conflict engine
- fatigue windows
- drop-off attribution
- policy engine
- recommendation evidence

Security:
- no production channel credentials by default
- sandbox external actions
- expression allowlist
- SSRF defense
- secret manager
- SBOM/scanning

Operations:
- OTel
- dashboards
- SLOs
- alerts
- DR
- load/chaos tests

## Principal-level explanation

A strong explanation:

> I would compile the journey into a validated executable state machine, generate synthetic customers/events from branch constraints, execute each customer independently using a virtual clock, record an immutable traversal stream, and compute coverage, drop-off, fatigue, policy and conversion findings from structured execution data. Generative AI can help create personas/events and explain recommendations, but deterministic code remains authoritative for journey execution and validation. At scale I would persist the run before dispatch, fan out users through a durable event bus, preserve per-user ordering, checkpoint execution, make writes idempotent, and aggregate results asynchronously.

## What is not claimed

This project does not claim:
- Adobe internal implementation;
- exact AJO private APIs;
- parity with every Journey Optimizer activity;
- production readiness without enterprise-specific hardening.

It is a substantial executable **production-oriented reference architecture** intended to demonstrate how such a platform can be engineered.

## Next extensions

High-value additions:
1. virtual-time priority queue;
2. bounded loops/jumps;
3. constraint-based branch coverage;
4. Kafka worker fleet;
5. persistent traversal event store;
6. multi-journey conflict analyzer;
7. content renderer;
8. LLM persona/event generator with schema validation;
9. recommendation agent;
10. OpenTelemetry;
11. Kubernetes/Helm/Terraform;
12. AJO API adapter using documented APIs where available.

## Final architecture principle

```text
Generative AI
  -> proposes synthetic users/events/recommendations

Deterministic Simulator
  -> executes journey truth

Analysis Engine
  -> computes evidence

Policy Engine
  -> validates rules

Journey Agent
  -> explains and proposes optimization

Human / governed workflow
  -> decides what changes
```

That separation makes the system explainable, reproducible and safer than allowing an LLM to invent simulation outcomes.


# Extended Principal / Staff Engineering Guide

## 1. Product use cases

The engine can support several classes of simulation:

1. **Pre-publication branch validation** — verify that synthetic users reach intended nodes.
2. **Synthetic persona coverage** — create profiles that exercise otherwise rare branches.
3. **Event-driven journey testing** — synthesize start/intermediate event payloads.
4. **Regression testing** — compare journey version N with N+1 using the same seed and personas.
5. **Drop-off diagnosis** — identify paths that terminate because no condition matches.
6. **Contact-pressure analysis** — estimate repeated channel contacts in modeled timelines.
7. **Policy preflight** — evaluate modeled consent, regional, channel or business constraints.
8. **Multi-journey conflict analysis** — merge timelines from several journeys and identify collisions.
9. **Experiment preflight** — validate that treatments are reachable and instrumented.
10. **Journey Agent evidence generation** — give an AI agent structured results rather than asking it to invent outcomes.

## 2. Quick simulation architecture

```text
User selects Quick Simulation
        |
        v
Journey Snapshot
        |
        v
Compiler / Static Analyzer
        |
        +--> path/branch requirements
        |
        v
Synthetic Test Planner
        |
        +--> persona constraints
        +--> event constraints
        |
        v
Generator
        |
        +--> synthetic profiles
        +--> synthetic event values
        |
        v
Simulation Scheduler
        |
        v
Parallel Deterministic Runtime
        |
        v
Traversal + Findings
        |
        v
Journey Agent Explanation
```

The generator can be AI-assisted; the runtime should remain deterministic wherever business semantics are deterministic.

## 3. Manual simulation architecture

```text
Human
 |
 +--> creates/selects synthetic user
 +--> overrides profile attributes
 +--> supplies event payload
 +--> controls waits/test addresses
 |
 v
Validated Simulation Inputs
 |
 v
Runtime
 |
 v
Results Log / Traversal
```

Quick and Manual modes should converge on the same compiler/runtime so their execution semantics do not drift.

## 4. Journey snapshotting

Never simulate a mutable live object without versioning.

Persist:

```text
journey_id
journey_version
journey_hash
compiled_version
simulation_config
policy_version
generator_version
engine_version
random_seed
```

This makes results reproducible and allows exact regression comparison.

## 5. Compiler phases

A production compiler can use:

```text
Parse
  -> schema validation
  -> semantic validation
  -> reference resolution
  -> expression compilation
  -> graph validation
  -> static reachability analysis
  -> optimization
  -> executable plan
```

Static validation should catch defects before worker capacity is consumed.

## 6. Static analysis

Useful compile-time checks:

```text
unreachable node
missing default branch
dead end
invalid expression
unknown field
invalid event reference
impossible condition
unsupported simulation activity
unbounded cycle
missing channel configuration
```

Some checks are warnings rather than errors.

## 7. Bounded loops

The reference implementation rejects cycles. A production journey engine may need bounded re-entry/loop semantics.

Represent loops with:

```text
max_iterations
deadline
visited-state fingerprint
virtual-time budget
```

Never permit an unconstrained synthetic run to loop forever.

## 8. Virtual clock design

Use a min-heap:

```text
(timestamp, sequence, user_id, event)
```

Algorithm:

```text
pop earliest event
advance virtual clock
apply event
emit transitions
schedule future events
repeat
```

This permits deterministic simulation of days/weeks in seconds.

## 9. Time semantics

Model:

```text
timezone
DST
business hours
quiet hours
calendar date
relative waits
absolute waits
expiration
```

Persist timezone explicitly; never assume worker-local time.

## 10. Event scheduler

Example event types:

```text
USER_ENTER
WAIT_EXPIRED
EXTERNAL_EVENT
MESSAGE_RENDERED
MESSAGE_DELIVERED_MODEL
REACTION
CONVERSION
TIMEOUT
CANCEL
```

The scheduler should order equal timestamps deterministically with a sequence number.

## 11. Synthetic persona planner

Instead of random personas only:

```text
Journey graph
    |
extract branch predicates
    |
constraint builder
    |
candidate attribute assignments
    |
persona generator
```

For:

```text
country == IN
AND loyalty >= 4
AND consent == true
```

generate a persona satisfying all constraints.

## 12. Constraint solver integration

Complex conditions can be translated to a constraint solver such as Z3 in a future extension.

Benefits:
- branch-directed generation;
- boundary testing;
- contradiction detection;
- minimum persona set for coverage.

Keep unsupported functions outside the solver and fall back to guided generation.

## 13. Minimum test-set problem

Given branches B1...Bn, generate the smallest set of users that covers the desired branches.

This resembles set cover:

```text
candidate user -> branches covered
choose minimum-cost candidates covering target branches
```

A greedy approximation is often sufficient.

## 14. Coverage model

Track:

```text
node coverage
edge coverage
condition true/false coverage
path-prefix coverage
event coverage
content variant coverage
persona segment coverage
```

Coverage should be reported as evidence, not as a guarantee that all real-world behavior is correct.

## 15. Path explosion controls

Apply:

```text
max generated users
max branch depth
risk-weighted coverage
pairwise coverage
sampling
budget-aware search
```

Prefer testing high-risk actions/conditions first.

## 16. Synthetic event generation

Events need schema-driven generation:

```text
event schema
  |
required fields
  |
branch predicates
  |
constraints
  |
generated payload
  |
schema validation
```

Persist generated payloads with the simulation for replay.

## 17. Content rendering simulation

Channel node:

```text
profile + context + template + offer
             |
             v
       render sandbox
             |
             v
        content artifact
```

Validate:
- unresolved variables;
- invalid URLs;
- locale;
- accessibility;
- content size;
- policy;
- brand requirements.

## 18. Channel isolation

Simulation workers should use capture adapters:

```text
EmailCaptureAdapter
SMSCaptureAdapter
PushCaptureAdapter
WebhookCaptureAdapter
```

A capture adapter records intended action without delivering it.

If a product deliberately supports real test delivery, isolate it behind explicit permissions, allowlisted test destinations and visible UI warnings.

## 19. Multi-journey simulation

```text
Customer timeline
     |
+----+----+----+
|         |    |
Journey A B    C
|         |    |
+----+----+----+
     |
Timeline Merge
     |
Conflict Analyzer
```

This allows analysis of cross-journey pressure and contradictory actions.

## 20. Conflict taxonomy

Examples:

```text
CHANNEL_COLLISION
OFFER_CONFLICT
STATE_WRITE_CONFLICT
PRIORITY_CONFLICT
BUDGET_CONFLICT
SUPPRESSION_CONFLICT
TEMPORAL_CONFLICT
```

Every finding should contain evidence and affected journey/node IDs.

## 21. Fatigue engine

Model a sliding window:

```text
customer
channel
communication type
timestamps
```

Then calculate:

```text
contacts in 24h
contacts in 7d
contacts across journeys
minimum spacing
```

Do not claim parity with live product frequency capping unless the exact production rule is implemented.

## 22. Drop-off attribution

A useful drop-off record:

```json
{
  "node": "eligibility",
  "reason": "NO_MATCHING_EDGE",
  "evaluations": [
    {"condition":"tier == gold","result":false},
    {"condition":"tier == silver","result":false}
  ]
}
```

This is much more actionable than only returning a percentage.

## 23. Conversion modeling

Three modes:

```text
deterministic conversion node
probabilistic modeled conversion
external model/decisioning response
```

Keep them explicitly labeled.

A probabilistic simulation is not a forecast unless its probability model has been validated for that use.

## 24. Experiment simulation

For randomized experiments:

```text
stable hash(user, experiment, seed)
       |
       v
bucket
       |
       v
treatment
```

This gives reproducible assignment for an independent simulator.

If emulating a product whose simulation uses nondeterministic decisioning, represent that mode separately.

## 25. Recommendation agent contract

Input:

```json
{
  "coverage": {},
  "dropoffs": [],
  "conflicts": [],
  "policy_findings": [],
  "fatigue": [],
  "conversions": {}
}
```

Output should be schema constrained:

```json
{
  "recommendations": [
    {
      "finding_id": "...",
      "proposal": "...",
      "rationale": "...",
      "confidence": 0.0,
      "requires_human_approval": true
    }
  ]
}
```

The agent proposes; it does not silently publish.

## 26. Evidence grounding

Every recommendation should reference:

```text
simulation run
journey version
persona(s)
node(s)
traversal(s)
finding(s)
```

This enables an operator to verify why the recommendation exists.

## 27. Distributed execution model

```text
POST /simulation
     |
     v
Control Plane
     |
SQL transaction
  run + outbox
     |
     v
Event Bus
     |
     +---- partition 1 --> worker
     +---- partition 2 --> worker
     +---- partition 3 --> worker
     |
     v
Traversal Store
     |
     v
Aggregation Job
     |
     v
Findings / Report
```

## 28. Task granularity

Options:

```text
one task/run
one task/persona
one task/user batch
one task/path
```

A user batch is often a good compromise between queue overhead and parallelism.

## 29. Per-user ordering

All events for a single simulated user must be ordered.

Partition key:

```text
run_id:user_id
```

Cross-user ordering usually does not need to be global.

## 30. Transactional outbox

Creation:

```sql
BEGIN;
INSERT INTO simulation_runs (...);
INSERT INTO outbox_events (...);
COMMIT;
```

Publisher:

```text
read unpublished
publish
mark published
```

Consumers remain idempotent because publish and acknowledgement can fail independently.

## 31. Checkpointing

Checkpoint:

```text
run_id
user_id
node_id
virtual_time
profile_state
event_cursor
sequence
engine_version
```

Checkpoint at safe boundaries rather than every instruction.

## 32. Idempotent traversal writes

Recommended uniqueness:

```text
(run_id, user_id, sequence)
```

A worker retry cannot duplicate the same logical event.

## 33. Worker leases

For database-claimed work:

```text
lease_owner
lease_until
attempt
version
```

Use fencing/version checks if stale workers could write after losing a lease.

## 34. Cancellation

```text
RUNNING
  |
CANCEL_REQUESTED
  |
workers observe token
  |
CANCELLED
```

Analysis can optionally run over partial results.

## 35. Progress

Compute progress from durable units:

```text
completed users / total users
```

Do not derive authoritative progress solely from transient worker memory.

## 36. Result storage

Separate:
- run metadata -> SQL;
- traversals -> SQL/columnar/event store depending scale;
- large rendered content -> object storage;
- telemetry -> observability backend;
- semantic recommendation context -> optional vector store.

## 37. Analytics warehouse

For large historical analysis:

```text
simulation events
     |
stream/batch ETL
     |
warehouse/lakehouse
     |
trend dashboards
```

Questions:
- which node types cause most drop-off?
- which journey versions regress coverage?
- how often do policies fail?
- average simulation cost?

## 38. API surface for a mature service

```text
POST /v1/simulations
GET  /v1/simulations/{id}
POST /v1/simulations/{id}/cancel
GET  /v1/simulations/{id}/users
GET  /v1/simulations/{id}/traversals
GET  /v1/simulations/{id}/findings
GET  /v1/simulations/{id}/coverage
POST /v1/simulations/{id}/recommendations
POST /v1/journeys/validate
```

## 39. Authentication and authorization

Production:

```text
Enterprise IdP
    |
OIDC
    |
API Gateway
    |
Simulation Service
```

Permissions can include:

```text
simulation.read
simulation.run
simulation.cancel
simulation.manage_users
simulation.generate_ai
simulation.view_content
```

## 40. Audit model

Audit:

```text
who
tenant
journey/version
operation
timestamp
simulation ID
configuration hash
result
```

Do not log secrets or raw sensitive attributes unnecessarily.

## 41. Tenant quotas

Examples:

```text
active runs
users/run
runs/hour
generated users/day
LLM token budget
artifact bytes
retention
```

Quota errors should be explicit and observable.

## 42. Rate limiting

Apply limits to:
- API caller;
- tenant;
- AI generation;
- simulation creation;
- report generation.

Do not rate-limit internal worker progress using the same policy as external ingress.

## 43. Backpressure

When workers are saturated:

```text
accept + queue within quota
or
return overload/retry-after
```

Never create unbounded in-memory tasks.

## 44. Circuit breakers

External dependencies such as content renderers or decisioning services need:

```text
timeout
retry budget
circuit breaker
bulkhead
fallback behavior
```

Simulation should clearly label degraded/mocked results.

## 45. Observability fields

Structured log fields:

```text
trace_id
run_id
tenant_id
journey_hash
user_id (opaque)
node_id
worker_id
engine_version
```

Avoid profile attributes in logs.

## 46. SLO examples

Example engineering targets, not Adobe product claims:

```text
API availability: 99.9%
simulation acceptance p95: <500ms
worker start p95: <10s
durable result loss: 0 after acknowledged commit
```

Define separate SLOs for interactive and batch simulation.

## 47. Capacity calculation

If:

```text
10,000 users/run
25 nodes/user
40 runs/hour
```

then:

```text
10,000 × 25 × 40 = 10,000,000 node evaluations/hour
```

Add content/model/external-service cost separately.

## 48. Hot partitions

Avoid partitioning only by tenant if one tenant is huge.

Use:

```text
hash(run_id,user_id)
```

while retaining tenant metadata for authorization.

## 49. Data retention

Different artifacts need different TTLs:

```text
synthetic users
traversals
rendered content
audit
telemetry
recommendations
```

Retention must align with enterprise policy and product requirements.

## 50. Privacy

Treat simulated profile data as potentially sensitive.

Rules:
- do not copy real PII by default;
- generate synthetic identifiers;
- minimize attributes;
- encrypt at rest/in transit;
- enforce deletion;
- redact logs.

## 51. Threat model

Threats:
- cross-tenant access;
- graph bomb/path explosion;
- malicious expressions;
- prompt injection;
- generated PII;
- SSRF;
- accidental live send;
- artifact malware;
- resource exhaustion;
- poisoned recommendations.

## 52. Expression sandbox

Never use Python `eval()` on journey expressions.

Use:
- parsed AST;
- allowlisted operators/functions;
- execution limits;
- typed values.

The reference engine uses an explicit operator allowlist.

## 53. Resource controls

Reject:
- too many nodes;
- too many personas;
- oversized attributes;
- excessive expression depth;
- huge strings;
- too many events;
- excessive runtime steps.

## 54. LLM isolation

```text
LLM output
  |
JSON schema validation
  |
semantic validation
  |
policy
  |
deterministic simulator
```

Never treat free-form model output as executable journey code.

## 55. Prompt injection

Journey content itself can contain hostile instructions.

The recommendation agent should treat content as data.

System/tool authorization must not be changeable by text embedded in an email template.

## 56. Model evaluation

Evaluate persona/event generation on:
- schema validity;
- branch coverage;
- diversity;
- privacy;
- consistency;
- reproducibility where applicable;
- cost.

Evaluate recommendation agent on:
- evidence correctness;
- hallucination rate;
- actionability;
- human acceptance.

## 57. Caching

Cache:
- compiled journey by immutable hash;
- expression plans;
- static schemas.

Do not cache mutable policy indefinitely.

## 58. Compiler cache

```text
journey hash
   |
cache lookup
   |
compiled plan
```

Version cache keys with compiler version.

## 59. Regression testing

Run old/new journey against identical:

```text
personas
events
seed
policy
engine
```

Compare:
- path changes;
- conversion-node reach;
- new drop-offs;
- contact count;
- findings.

## 60. Golden simulation corpus

Maintain a corpus of representative journeys:
- simple linear;
- deep branching;
- event-driven;
- waits;
- randomized experiment;
- missing default;
- conflict-heavy;
- high-volume.

Run it in CI.

## 61. Chaos tests

Inject:
- worker crash;
- queue duplicate;
- DB failover;
- Redis loss;
- object-store timeout;
- analyzer crash;
- recommendation-model timeout.

Verify no durable corruption.

## 62. Disaster recovery

Define:
- RPO/RTO;
- backup;
- restore test;
- event replay;
- object-store recovery;
- regional failover.

## 63. Kubernetes topology

```text
Ingress
  |
API Deployment
  |
+-- SQL
+-- Redis
+-- Kafka
  |
Worker Deployments
  |
Analyzer Deployment
  |
Object Store
```

Use:
- HPA;
- PDB;
- topology spread;
- NetworkPolicy;
- workload identity;
- secrets manager.

## 64. Autoscaling

Worker autoscaling signal:

```text
queue lag
+
oldest task age
+
CPU
```

Queue lag is often more meaningful than CPU alone.

## 65. CI/CD pipeline

```text
ruff
pytest
property tests
graph fuzzing
integration
load smoke
SAST
dependency scan
SBOM
image scan/sign
staging corpus
progressive deploy
```

## 66. Schema migration

The reference uses `create_all()` for easy execution.

Production uses Alembic with expand/contract migrations.

Never couple deployment success to destructive schema migration.

## 67. Feature flags

Useful flags:
- new compiler;
- new persona generator;
- new analyzer;
- new recommendation model;
- virtual-clock implementation.

Flags need tenant/environment scope and audit.

## 68. Compatibility

Persist versions because a simulation created under engine v1 may behave differently under v2.

Do not silently reinterpret old results.

## 69. Operational dashboards

Dashboards:
- active simulations;
- queue lag;
- duration percentiles;
- users/sec;
- node evaluations/sec;
- failure reason;
- coverage;
- analyzer latency;
- AI generation latency/cost.

## 70. Alert examples

Alert:
- queue oldest age > threshold;
- worker failure spike;
- DB saturation;
- simulation failure ratio;
- artifact-store errors;
- generation invalid-schema spike.

## 71. Incident runbook

1. determine affected tenant/runs;
2. stop new high-cost submissions if necessary;
3. preserve durable state;
4. quarantine failing worker/version;
5. drain/replay safe work;
6. reconcile partial runs;
7. communicate degraded semantics;
8. restore and verify;
9. postmortem.

## 72. Production launch checklist

Before real production:
- real enterprise auth;
- tenant isolation tests;
- Alembic;
- durable queue;
- outbox;
- virtual clock;
- cancellation;
- checkpointing;
- OTel;
- secret manager;
- sandboxed actions;
- quotas;
- load tests;
- DR;
- security review;
- privacy review.

## 73. Why SQL + Redis + Kafka + object storage

```text
SQL
authoritative run/config/result metadata

Redis
ephemeral cache/limits

Kafka
durable asynchronous fan-out/events

Object storage
large content/artifacts
```

Using one datastore for every concern creates unnecessary tradeoffs.

## 74. Why not execute the real journey engine directly?

A simulation system needs:
- isolation;
- speed;
- synthetic data;
- virtual time;
- controlled side effects;
- reproducibility.

Sharing semantics with production is valuable, but blindly executing live side effects is unsafe.

## 75. Shared semantics strategy

Best architecture:

```text
Journey DSL
   |
Shared compiler/semantic library
   |
+-- production runtime
+-- simulation runtime
```

This reduces semantic drift while allowing different side-effect adapters.

## 76. Applications beyond marketing

The same engine pattern applies to:
- onboarding workflows;
- support escalation;
- loan/application flows;
- healthcare workflow testing;
- notification orchestration;
- SaaS lifecycle automation.

Domain policy and privacy requirements differ.

## 77. Principal-level design tradeoffs

### In-memory vs distributed
In-memory is ideal for fast small simulations. Distributed execution is needed for large runs, expensive rendering/models and durable long-running jobs.

### Random generation vs constraint generation
Random is cheap but wastes coverage. Constraint-directed generation is more expensive but targets branches.

### Exact production parity vs safe modeling
Parity improves confidence; isolation protects users. Share deterministic semantics but replace side effects with simulation adapters.

### Synchronous vs asynchronous API
Synchronous is convenient for tiny runs. Production scale needs async run IDs, polling/streaming and cancellation.

## 78. questions this project demonstrates

- design a large-scale workflow simulator;
- test every branch of a customer journey;
- build synthetic user generation;
- simulate time-dependent workflows;
- prevent accidental external effects;
- parallelize state-machine execution;
- ensure deterministic replay;
- build an AI recommendation layer without hallucinating results;
- scale to millions of simulated transitions;
- design multi-tenant simulation SaaS.

## 79. End-to-end enterprise architecture

```text
                    Journey Authoring
                          |
                          v
                  Versioned Journey DSL
                          |
                          v
                Validation / Compilation
                          |
                +---------+---------+
                |                   |
                v                   v
          Coverage Planner     Policy Preflight
                |                   |
                +---------+---------+
                          |
                          v
               Synthetic Data Planner
                          |
                 +--------+--------+
                 |                 |
                 v                 v
              Personas           Events
                 |                 |
                 +--------+--------+
                          |
                          v
                  Simulation Control
                          |
                  SQL + Outbox/Event Bus
                          |
              +-----------+-----------+
              |           |           |
              v           v           v
           Worker      Worker      Worker
              |           |           |
              +-----------+-----------+
                          |
                    Traversal Store
                          |
             +------------+-------------+
             |            |             |
             v            v             v
          Coverage     Conflict       Policy
          Analyzer     Analyzer       Analyzer
             |            |             |
             +------------+-------------+
                          |
                          v
                    Evidence Store
                          |
                          v
                     Journey Agent
                          |
                          v
              Optimization Proposals
                          |
                          v
                Human/Governed Change
```

## 80. Final engineering rule

The most important rule is:

```text
AI generates hypotheses and explanations.
The simulator generates execution evidence.
Policy determines what is allowed.
Humans/governed automation decide what changes.
```

This separation keeps a sophisticated AI-assisted journey platform reproducible, auditable and operationally safe.
