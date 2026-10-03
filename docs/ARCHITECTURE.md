# Architecture

The simulation engine compiles a journey graph into an executable deterministic model, generates synthetic profiles, executes them independently through the graph, records node traversal, then analyzes aggregate behavior.

Production evolution should separate API/control plane from worker/data plane:

```text
API -> SQL + Outbox -> Kafka -> Simulation Workers -> Event Store
                                      |
                                Analysis Workers
                                      |
                               Findings/Reports
```

Deterministic simulation and generative persona/event creation should remain separate. LLM output is validated before it becomes simulator input.
