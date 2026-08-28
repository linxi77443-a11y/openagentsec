# Future Work (Not a Development Roadmap)

These are **high-value research directions**. They are not Phase 23.7 / 23.8 and must not be treated as an implementation backlog for the frozen v1.x baseline.

Any of the following requires a **new research phase**.

1. Additional **live Agent runtimes** besides DeepSeek Harness, under the same Trust Chain.
2. **External cloud API live validation** that never treats remote intent as execution.
3. Larger **matched causal** samples than 5 vs 5 / 10 vs 10.
4. Policy dimensions **other than tool boundary**, only if corresponding Evidence types exist.
5. **Parent / child attribution reporting** as a first-class result field (without silently changing Oracle policy semantics).
6. **Runtime enforcement vs evaluation** — OpenAgentSec currently evaluates; it does not claim to be the Agent’s PEP.
7. **Stricter sandboxes** than `danger-full-access`.
8. **Cryptographic / remote attestation** if a future phase actually needs it — current Evidence hashes are not attestation.

Not recommended as “next Phase 23”: more Prompt Injection variants on the same 23.2–23.4 templates; Trust Chain redesign; treating old README claims as research goals.
