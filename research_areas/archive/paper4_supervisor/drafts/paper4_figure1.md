# Figure 1 — M-Form Architecture

Caption: Deterministic governance separates generation from evaluation in the M-Form architecture. Solid lines are deterministic enforcement boundaries; dashed lines are probabilistic agent outputs. The principal interacts only at genesis (contract signing) and State D (human gates). All intermediate governance is deterministic Python with no learned parameters.

## Mermaid source

```mermaid
graph TD
    subgraph Principal Layer
        P["<b>Principal</b><br/>(Human)"]
    end

    subgraph Deterministic Governance Layer
        direction TB
        G["<b>Genesis Artifact</b><br/>Write-scope boundary<br/>Success condition<br/>Token budget"]
        SM["<b>State Machine</b><br/>A1 → A2 → B → C → D"]
        WS["<b>Write-Scope Guard</b><br/>Pre/post diff comparison<br/>Fail-closed on violation"]
        V["<b>Deterministic Verifier</b><br/>Typed assertions<br/>No learned parameters"]
    end

    subgraph Agent Layer
        direction LR
        A1["<b>Architect</b><br/>(LLM Agent)<br/>Proposes spec"]
        A2["<b>Skeptic</b><br/>(LLM Agent)<br/>Pressure-tests spec"]
        B["<b>Builder</b><br/>(LLM Agent)<br/>Implements artifact"]
    end

    P -->|"Signs contract<br/>(one-time)"| G
    G -->|"Defines scope"| SM
    SM -->|"Routes turn"| A1
    SM -->|"Routes turn"| A2
    SM -->|"Routes turn"| B
    A1 -.->|"Staged output"| WS
    A2 -.->|"Staged output"| WS
    B -.->|"Staged output"| WS
    WS -->|"Scope OK"| SM
    WS -->|"Scope violation"| D["<b>State D</b><br/>Human Gate"]
    SM -->|"Implementation"| V
    V -->|"PASS"| SM
    V -->|"FAIL"| SM
    D -->|"Resolve"| P

    style P fill:#f9f,stroke:#333,stroke-width:2px
    style G fill:#ffd,stroke:#333,stroke-width:2px
    style SM fill:#ddf,stroke:#333,stroke-width:2px
    style WS fill:#fdd,stroke:#333,stroke-width:2px
    style V fill:#dfd,stroke:#333,stroke-width:2px
    style D fill:#fdd,stroke:#333,stroke-width:2px
    style A1 fill:#eee,stroke:#999,stroke-dasharray: 5 5
    style A2 fill:#eee,stroke:#999,stroke-dasharray: 5 5
    style B fill:#eee,stroke:#999,stroke-dasharray: 5 5
```

## Text description (for manuscript)

The system has three layers:

1. **Principal Layer.** The human signs a genesis artifact (an immutable contract specifying write-scope boundary, success condition, and token budget) and resolves human gates at State D. The principal does not participate in intermediate states.

2. **Deterministic Governance Layer.** Four components with no learned parameters:
   - *State machine* routes turns between agents (A1 → A2 → B → C → D)
   - *Write-scope guard* computes a repository diff before and after each agent invocation; any unauthorized modification triggers a fail-closed transition to State D
   - *Deterministic verifier* checks typed assertions (contains_phrase, contains_citation, has_subsection, absent_phrase) against the implementation artifact; PASS advances the state, FAIL returns to the builder
   - *Genesis artifact* defines the enforcement floor before execution begins

3. **Agent Layer.** Language model agents (Architect, Skeptic, Builder) operate within contracted scope. Their outputs are probabilistic. They cannot modify the governance layer, access files outside their read bundle, or advance their own state. All agent output passes through the write-scope guard before the state machine accepts it.

The enforcement boundary between layers 2 and 3 is the paper's central structural claim: it is deterministic, fail-closed, and cannot be softened by model output.
