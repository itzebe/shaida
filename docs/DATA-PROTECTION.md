# Data protection

SHAIDA is designed so that the strongest data-protection guarantee is the simplest one: **most of
the sensitive data is never collected.** This document describes the design against the Nigeria
Data Protection Act 2023, and states plainly what has and has not been done.

---

## 1. The design principle

> Collect nothing that could identify a reporter, because a report about intimidation is dangerous
> to its author.

This is enforced by the **schema**, not by policy. There is no column for a name, phone number,
email address, account identifier or IP address. `test_no_reporter_identity_is_stored` creates a
report and asserts that no identity field exists in the stored record.

## 2. Data inventory

| Data | Collected? | Purpose | Safeguard |
|---|---|---|---|
| Reporter name | **No** | — | no field exists |
| Phone / email / account | **No** | — | no field exists |
| IP address | **No** | — | not stored |
| Reporter *role* (citizen / observer / party agent / official) | Yes | interpret the report; not an identifier | a role, not a person |
| Narrative text | Yes | the substance of the report | length-bounded, validated at the boundary |
| Evidence file (photo/scan/audio/video) | Hashed and stored | prove the record was not altered | SHA-256 computed **on the device** before upload |
| Precise latitude/longitude | **Off by default** | optional location context | coarsened to ~1 km; never returned exactly |
| Polling-unit code | Optional | link a report to a unit | a public identifier, not a person |
| Aggregates | Derived | situational awareness | k-anonymity floor (default 5); suppressed entirely, never rounded |
| Reviewer handle + reason | Yes | accountability for a human decision | a handle, not a private individual's name |

## 3. NDPA 2023 principles, mapped

| Principle | How SHAIDA addresses it |
|---|---|
| **Lawfulness, fairness, transparency** | No personal data is collected, so no lawful basis is needed for processing it. The interface states in plain language what is and is not collected. |
| **Purpose limitation** | Report data is used to route the report to a human reviewer. There is no secondary use — no analytics, no profiling, no advertising, no partisan use. |
| **Data minimisation** | Enforced by the schema. Identity is not minimised; it is absent. |
| **Accuracy** | The system distinguishes what a reporter asserts from what a rule computes, and never presents one as the other. Findings carry the innocent explanations that may make them wrong. |
| **Storage limitation** | **Not claimed.** The store is a prototype SQLite file. No retention or deletion policy is asserted, because asserting one without a live deployment would be dishonest. A defined retention and deletion policy is a **precondition** for real use. |
| **Integrity and confidentiality** | Evidence is hashed at capture; the audit log is a hash chain re-verified from stored data; direct-database tampering is proven caught by test. |
| **Accountability** | Every human decision is recorded with a reason, in the same tamper-evident log. |

## 4. Specific protections

### 4.1 Sensitive reporting

Categories that can endanger a person — `intimidation`, `voter_intimidation`,
`violence_or_threat` — change **handling**, never the verdict:

- the report is marked sensitive and routed for stricter handling;
- the interface advises leaving location blank for such reports;
- SHAIDA never contacts the police, INEC or any authority on its own, and says so on the receipt.

Being a victim of intimidation is not evidence of wrongdoing, and the system does not treat it as
such.

### 4.2 Aggregation

Aggregates are published only above a **k-anonymity floor** (default 5). Cells below the floor are
**suppressed entirely, never rounded** — because rounding leaks: a suppressed-looking zero plus a
known total can recover the individual. The Integrity page displays the floor and the suppression
count openly.

### 4.3 Location

Precise coordinates are off by default. When used, they are coarsened to approximately one kilometre
before storage, and are never returned exactly (`test_coordinates_are_coarsened_and_never_returned_exactly`).

### 4.4 Evidence

The hash is computed **on the reporter's device** before upload, so the reporter can prove what they
submitted even if the service were compromised. The content hash covers only the original evidence
and is deliberately **excluded from derived metadata**
(`test_content_hash_excludes_derived_metadata`) so that an AI-derived field can never alter the
evidence hash.

## 5. Data subject rights

Because no personal data is collected, the rights of access, rectification, erasure, portability and
objection have no data to attach to for a reporter. A reviewer handle is the only identifier-like
value, and it is a role handle, not a natural person's record.

This is a deliberate design position: **the cleanest way to protect a data subject is to hold no
data about them.**

## 6. What has not been done

Stated plainly, because a claim of compliance without these would be false:

1. **No DPIA has been performed.** A Data Protection Impact Assessment under the NDPA 2023 is a
   **precondition for real use**, not a completed step.
2. **No retention or deletion policy exists**, because there is no live deployment for one to apply
   to.
3. **No NDPC registration** or filing has been made; none is applicable to a prototype with no
   personal data and no deployment.
4. **No data-processing agreement with a CSO operator** exists. A written agreement is a precondition
   for any pilot.
5. **No independent security or privacy audit** has been carried out.

## 7. Third-party services and transfers

**None.** The prototype makes no outbound network call. There is no analytics provider, no CDN, no
model API, no telemetry. Nothing leaves the machine it runs on. There is therefore no cross-border
transfer to assess.

## 8. Conditions before any real use

The following are required before this system is used with any real report:

1. a DPIA under the NDPA 2023, with a documented lawful basis and a retention/deletion policy;
2. an independent security and privacy review of the API and the hash chain;
3. a written agreement with any operating civil-society organisation, including breach-notification
   procedures;
4. an ethics review covering sensitive reporting and vulnerable reporters;
5. a legal review against electoral law and defamation risk.

Until then, the position is the one stated on every page of the application: SHAIDA is a working
prototype, it flags and does not judge, and it is not approved for operational electoral
deployment.
