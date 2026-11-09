# Impact and scalability

*Honest throughout: we distinguish what is demonstrated from what is projected, and we do not
invent user numbers, pilots or partnerships.*

---

## 1. Who benefits, and how

| Beneficiary | Change in their situation | Evidence that it works |
|---|---|---|
| **Citizen reporter** | Can report an incident with no identity and still hold proof that their record was not altered | End-to-end browser run: file → on-device hash → receipt → appears in queue → chain verifies |
| **Observer / CSO monitor** | Scarce reviewer attention goes to the riskiest reports first, with duplicates grouped | Triage lift **+2.08**; clustering 400 → 17 (**upper bound**, see §4) |
| **Reviewer** | Every item carries a reason and a list of innocent explanations to rule out; every decision is auditable | Required-decision-and-reason enforced and tested; per-item explanation tested |
| **Fact-checker** | A received claim can be shortlisted against an archive with prior human labels, in mixed language | Claim matcher top-3 **86.7 %**; Pidgin handling tested |
| **Election administrator / auditor** | Can re-verify that a record was not altered, from the stored data | `GET /v1/integrity/audit` re-computes the chain; tamper tests prove detection |

## 2. Impact mechanism — why this changes an outcome

The impact is not "better dashboards". It is that **three specific failures stop happening**:

1. **Evidence stops degrading.** A report's integrity survives the network, because the hash is
   taken at capture and the log is chained. A claim about a result sheet can be tied to an
   unaltered record.
2. **Deterministic contradictions get surfaced before allegations.** A contradiction the arithmetic
   proves is separated from an opinion someone holds — and the finding comes with the innocent
   explanations, so a transcription error is not mistaken for misconduct.
3. **Attention is allocated by harm, not arrival order.** The reports that endanger people reach a
   human first.

## 3. Scalability — the honest engineering assessment

| Dimension | Current state | What scaling actually requires |
|---|---|---|
| Storage | single-instance SQLite | a server database with replication; the access layer is already isolated in `storage.py` |
| Compute | rule engine at ~9 000–9 600 records/s single-threaded | the rule engine is embarrassingly parallel; the bottleneck would be the store, not the rules |
| Concurrency | untested | load testing at national scale is a **stated precondition**, not a claim |
| Evidence blobs | hashed and stored locally | object storage with lifecycle rules; the hash is what matters, so blobs can be tiered |
| Multi-tenancy | none | a real deployment needs operator authentication and per-tenant scoping (noted as a gap in `SECURITY-AND-PRIVACY.md` §A3) |
| Offline | app shell cached by a service worker that never caches API responses | unchanged; this is a strength at low connectivity |

**What scales naturally:** the deterministic core (pure functions over records), the hash chain
(append-only), the triage model (a published weighted sum), and the offline-first frontend.

**What does not scale as built:** the single-file store and the absence of tenancy. Both are
deliberate prototype simplifications, both are named, and neither is hidden behind a claim.

## 4. The clustering number, stated correctly

Clustering reduces 400 synthetic reports to 17 clusters — a 95.8 % reduction. **This is an upper
bound.** The official synthetic incident pack is machine-generated and unusually repetitive, so
near-duplicate grouping succeeds far better than it would on real reports, which vary enormously in
wording. The figure demonstrates that the *mechanism* works. It does not predict real savings, and
we do not present it as one.

## 5. Sustainability

- **Cost of running:** zero. No paid API, no cloud service, no model download, no credential. The
  prototype runs on a laptop.
- **Dependencies:** FastAPI, Uvicorn, Pydantic, scikit-learn, pytest (backend); React + Vite
  (frontend). All open source, all mainstream, all pinned.
- **Maintenance burden:** low and concentrated. The deterministic core is small and fully tested;
  the assistive layer retrains from loaded data on every start, so there is no model artefact to
  manage.
- **Path to a real deployment:** a CSO-operated instance in a controlled sandbox, which is what the
  roadmap in [`PRODUCT.md`](PRODUCT.md) §14 describes, gated on the conditions in
  [`SAFETY-AND-LIMITATIONS.md`](SAFETY-AND-LIMITATIONS.md) §5.

## 6. What would make the impact real, and is not yet done

These are **prerequisites**, not achievements:

1. A pilot with a real CSO, in a sandbox, on synthetic or consented data.
2. A human-factors study measuring reviewer agreement and time saved — **we have not measured this**,
   and every impact claim above is therefore about *mechanism*, not *outcome*.
3. Linguistic fairness evaluation on Hausa, Yoruba and Igbo incident text.
4. Legal and data-protection review under the NDPA 2023, including a DPIA.
5. Load testing at national scale.

Until those exist, the honest statement of impact is: **the mechanism is built and verified on
synthetic data; the real-world outcome is unmeasured.**

## 7. National relevance

The design targets the conditions that actually exist in Nigerian elections: low-end phones,
intermittent connectivity, mixed-language communication, sensitive reporting that endangers
reporters, and a small number of organisations carrying an enormous verification load. It works
offline, it asks for no identity, it speaks five languages at the interface, and it is designed to
be operated by a civil-society organisation rather than by an institution — which is exactly the
actor with the most to gain and the least infrastructure.
