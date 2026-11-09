# Demo narration — SHAIDA

**Target:** ≤ 3 minutes. **Planned:** ~2 min 50 s.
Read at a calm, measured pace. Each block below is timed to the matching shot in
[`storyboard.md`](storyboard.md).

---

### Shot 1 — The problem (0:00–0:18)

> On election day in Nigeria, thousands of photos, voice notes and claims are captured. Within
> hours, most of them cannot be trusted. An image is forwarded, re-compressed and re-posted, and by
> the time anyone wants to act on it, there is no way to prove that *this* file is what was
> captured at *that* time. And the arithmetic that anyone could check by hand — on the result sheet
> itself — is almost never checked.

### Shot 2 — Privacy by architecture (0:18–0:50)

> SHAIDA starts with a report. There is no field for a name, no phone number, no account. Not
> minimised — absent. Watch the draft commitment hash change as I type: the evidence is hashed on
> this device, before anything is uploaded. And location is off by default. For a report about
> intimidation, that matters: the safest data is the data you never collect.

### Shot 3 — A receipt you can prove with (0:50–1:10)

> I submit. SHAIDA returns a reference and a content hash. That hash is how this reporter — or
> anyone — can later prove the record was not altered. It is also linked into an append-only log
> that anyone can re-verify. The report now waits for a human. SHAIDA will not contact the police,
> INEC, or anyone else on its own.

### Shot 4 — Deterministic checks that flag, never judge (1:10–1:45)

> Now the result sheet. These checks are arithmetic, not opinion. *Structural* findings cannot both
> be true on a correct sheet — here, accredited voters exceed the registered voters, and the
> sheet's own totals do not close. *Advisory* findings are statistical hints, labelled as such,
> because they over-fire. And every finding ships with the innocent explanations a reviewer should
> rule out first: a transcription error, a misread faint form, two rows merged by mistake. The
> arithmetic certificate lets anyone re-check it by hand. SHAIDA does not conclude that anything is
> wrong. It shows a reviewer what does not add up.

### Shot 5 — Human review is mandatory (1:45–2:10)

> The reviewer queue is ordered by harm, not by arrival time, using a published weighted score that
> shows every contribution. Duplicates are grouped, so a reviewer sees one item with a count
> instead of fifty entries. And to close a report, a reviewer must record a decision *and a
> reason*. That decision goes into the same tamper-evident log. There is no automated decision
> path in this system.

### Shot 6 — Claims, in the language they arrive in (2:10–2:32)

> A claim arrives in Pidgin. SHAIDA shortlists similar archived claims and shows what a human
> already concluded about them. It does not label anything itself — it has no truth model. When the
> closest match is weak, it says so and tells the reviewer to decide.

### Shot 7 — Integrity anyone can check (2:32–2:48)

> The audit log is a hash chain. Re-verifying re-computes it from the stored data — it does not
> trust the writer. If any entry were edited or removed, this would fail and point at the entry.
> Aggregates are published only above a privacy floor: small cells are suppressed entirely, never
> rounded, so no individual report can be recovered.

### Shot 8 — The point (2:48–2:58)

> SHAIDA flags. It does not judge. It declares no result, accuses no person, and exposes no
> reporter. That is the whole design: a tool may help people check evidence — but it must never
> decide an electoral question for them.

---

## Narration notes for the presenter

- **Pace:** ~145 words per minute. Total narration is ~470 words, which fits the runtime with room
  for the pauses described.
- **Emphasis:** the phrases *"does not judge"*, *"not minimised — absent"*, and *"no automated
  decision path"* carry the differentiation. Slow slightly on each.
- **Tone:** factual, not triumphant. The strongest claim in the video is a refusal.
- **Do not** say the tool detects fraud, finds anomalies "in the election", or improves accuracy —
  none of which it does or claims.

## Honest limitations to state if asked (not in the video, for the Q&A)

- The evaluation is on synthetic data; real-world accuracy is unmeasured.
- The assistive model is untested on non-English incident text.
- No human-factors study of reviewer agreement has been run.
- The prototype is not load-tested at national scale.
