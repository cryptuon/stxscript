# StxScript Roadmap

StxScript is a TypeScript-inspired transpiler that emits audit-ready Clarity for the Stacks blockchain. This document sets out the vision, the milestones, and — most importantly — the **cheapest path to production** for a project of this kind.

> For the completed development history (phases 1–10, v0.3.0), see [`docs/roadmap.md`](docs/roadmap.md). This file is forward-looking and market-oriented.

## Vision

Bitcoin is maturing into a settlement layer for real economic activity — Bitcoin DeFi, real-world assets (RWA), atomic composability, and Bitcoin-secured L2s. Stacks brings expressive, decidable smart contracts to Bitcoin through Clarity. The scarce resource is not the chain; it is developers who can write correct Clarity.

StxScript's role is **chain abstraction for authoring**: give the large TypeScript developer base an ergonomic, statically typed on-ramp to Clarity, without adding any runtime you have to trust. The compiled Clarity is what teams deploy and auditors read. Success looks like a TypeScript-fluent team shipping a reviewed Stacks contract to mainnet faster than they could have by learning Clarity from scratch — with the generated output good enough to hand to an auditor unchanged.

Design commitments:

- **Compile-time only.** Nothing StxScript-specific runs on-chain. Output is plain Clarity.
- **Readable, reviewable output.** Generated `.clar` is the source of truth. If a human can't audit it, the transpiler failed.
- **Honest coverage.** We document what is and isn't supported rather than implying 100% Clarity parity.

## Cheapest path to production

**For a developer tool, "production" is not a deployed server — it is a published, installable transpiler that reliably takes a real StxScript contract from Stacks testnet to mainnet, with output a team is willing to ship.** The cheapest credible path is therefore about *distribution + trust*, not infrastructure.

### What "production" means here

1. A **published package** developers can install in one command (PyPI is already the primary target; an npm wrapper widens reach to the JS ecosystem StxScript serves).
2. A **working testnet → mainnet flow**: transpile → `clarinet check` → deploy to Stacks testnet → deploy to mainnet, documented end to end.
3. Output that **an auditor can review as-is**.

### Cheapest path (do these, in order)

1. **Publish the package.** `stxscript` targets [PyPI](https://pypi.org/project/stxscript/); keep releases current and versioned. Cost: near zero — it's packaging, not hosting.
2. **Target Stacks directly, lean on existing tooling.** Emit Clarity that flows straight into Clarinet and the standard Stacks deploy path. Do not build a runtime, a chain, or hosted infra — the "backend" is Bitcoin/Stacks, which already exists.
3. **Ship the trust artifacts** (below). For a transpiler, credibility *is* the product; these cost engineering time, not money.

There is deliberately no server to run, no database, no cloud bill. The entire production surface is a package registry entry plus documentation — which is why a transpiler is one of the cheapest classes of blockchain tooling to take to production.

### Production-viability checklist

These are the concrete artifacts that make the transpiler trustworthy enough for real value on mainnet:

| Artifact | Why it gates production | Status |
|----------|-------------------------|--------|
| **Clarity feature-coverage matrix** | Users must know exactly which Clarity constructs are supported vs. where to hand-write | Partial — publish an explicit matrix |
| **Output-equivalence / audit review** | Generated Clarity must be provably behavior-equivalent to intent and readable by auditors | Ongoing — needs documented review of generated patterns |
| **Test suite** | Regression safety for the transpiler itself | 146 tests passing; expand to golden-file output tests |
| **Documentation** | Getting-started, language guide, testnet→mainnet deploy walkthrough | Present; add explicit deploy path |
| **Versioning** | Semantic versioning so downstream contracts pin a known compiler | In place (0.3.0); formalize SemVer + changelog |

## Milestones

### Now (v0.3.x) — Distribution & honesty

- [ ] Keep PyPI releases current; document install/upgrade
- [ ] Publish an explicit **Clarity feature-coverage matrix** (supported / partial / drop-to-Clarity)
- [ ] Golden-file output tests: lock generated Clarity for canonical contracts
- [ ] End-to-end **testnet → mainnet deploy walkthrough** in docs
- [ ] Formal SemVer policy + changelog

### Next — Ecosystem fit

- [ ] npm wrapper / distribution to reach the JS/TS developer base directly
- [ ] Tighter **Clarinet integration** (invoke check/deploy from the StxScript CLI)
- [ ] Source maps for debugging generated Clarity back to StxScript
- [ ] Expand Clarity built-in coverage guided by the coverage matrix gaps

### Later — Depth for Bitcoin DeFi / RWA teams

- [ ] Package registry for sharing StxScript modules/traits
- [ ] Patterns/library for common Bitcoin DeFi + RWA contract shapes
- [ ] Incremental compilation for large projects
- [ ] Output-equivalence tooling to support third-party audits

## Non-goals

- **Not a runtime or a chain.** StxScript adds nothing to on-chain trust assumptions.
- **Not a formal verifier.** Static typing and linting, not correctness proofs.
- **Not 100% Clarity coverage as a promise.** We grow coverage transparently; hand-written Clarity is always the escape hatch.

---

*See also: [README.md](README.md) · [docs/roadmap.md](docs/roadmap.md) (development history) · [Stacks](https://www.stacks.co/) · [Clarity](https://docs.stacks.co/docs/clarity/)*
