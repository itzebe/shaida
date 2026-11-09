# Demo storyboard — SHAIDA

**Target length:** ≤ 3 minutes (official limit, `00_general_challenge_rules.md`).
**Planned runtime:** ~2 min 50 s.
**Footage:** real screen capture of the running application. No mock-ups, no simulated API
responses, no fake data presented as live.

---

## The story in one line

A result sheet that does not add up, and a citizen who cannot prove what they saw — solved by a tool
that proves provenance, checks the arithmetic anyone could check, and refuses to declare a verdict.

## Shot list

| # | Time | Screen | What happens on screen | What the narration says | Why it is in the demo |
|---|---|---|---|---|---|
| 1 | 0:00–0:18 | *File a report* (top) | Page loads. The footer line is visible: *"flags only · no verdicts"* | The problem: an election day produces thousands of photos, voice notes and claims — and no way to prove any of them is unaltered | Establishes the real problem in the first 10 seconds |
| 2 | 0:18–0:50 | *File a report* (form) | Narrative typed; category chosen; **location left blank**; the draft commitment hash appears live as the text changes | SHAIDA collects no name, no phone, no account — there is no field for one. Evidence is hashed on the device, before upload | Shows privacy by architecture, not by policy |
| 3 | 0:50–1:10 | *File a report* (receipt) | Submit. The **receipt** appears: reference `rep-…`, priority band, content `sha256` | The reporter gets a reference and a hash — proof, later, that the record was not altered | The core evidence-integrity moment |
| 4 | 1:10–1:45 | *Result checks* | The official synthetic pack is loaded. A flagged record is opened. Two **structural** findings and one **advisory** finding are shown, each with innocent explanations. *Show arithmetic certificate* is expanded | Structural findings are arithmetic contradictions that cannot both be true. Advisory findings are statistical hints, labelled as such. Every finding lists the innocent explanations to rule out first | Shows deterministic verification that flags and does not judge |
| 5 | 1:45–2:10 | *Reviewer queue* | The queue is harm-ordered. Duplicate reports appear as one item with a count. *Record a decision* is opened and the reason field is shown as required | Reports are ordered by harm, with a published weighted score. A reviewer must record a decision and a reason — and that is written to the audit log | Shows human oversight is mandatory, not optional |
| 6 | 2:10–2:32 | *Claim matching* | A Pidgin claim is pasted; a shortlist of archived claims appears with **prior human labels** | The matcher returns what a human already concluded about a similar claim. It has no truth model, and it abstains when unsure | Shows multilingual robustness and the no-verdict rule |
| 7 | 2:32–2:48 | *Integrity* | *Re-verify now* re-computes the chain. The entry table appears. The aggregate panel shows cells **suppressed** below the privacy floor | Anyone can re-verify the log from the stored data. Aggregates are suppressed below a privacy floor, never rounded | Shows tamper-evidence and privacy floor |
| 8 | 2:48–2:58 | *About and limits* | Scroll to *"What it does not do"* and the conditions-before-use list | SHAIDA flags. It does not judge. It is not approved for operational deployment | Ends on the honest limitation, which is the point |

## Visual and audio treatment

- **Capture:** 1440 × 900 browser viewport, 25 fps, recorded from the real `vite preview` build with
  the real FastAPI backend running.
- **Cursor:** visible; interactions are real clicks and real typing.
- **Captions:** burned in, bottom-centred, high contrast, synced to the narration.
- **Narration:** calm, factual, second-person-neutral. No hype. No claim that the tool decides
  anything.
- **Motion:** only real UI transitions. No zoom effects, no transitions added in editing.

## What the demo deliberately does **not** do

- No simulated success: every screen shown is driven by the real backend, and the data is either the
  organisers' synthetic pack or clearly-synthetic demo reports (`DEMO-*` codes).
- No claim of real election data.
- No claim that SHAIDA detects fraud or declares a result — the opposite is shown.
