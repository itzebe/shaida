# User guide

SHAIDA has six screens. Each answers one question. This guide walks each user through the one that
is theirs.

> The rule that governs every screen: **SHAIDA flags. It does not judge.** Nothing here tells you
> what happened, who is guilty, or who won.

---

## 1. If you are a citizen or an observer — *File a report*

Open the app. It works offline after the first load.

1. **Choose a category** — logistics delay, result-sheet issue, intimidation, accessibility
   barrier, misinformation, and so on. Pick the closest; a reviewer can reclassify.
2. **Describe what you saw.** Write only what you personally observed or were told. Do not name
   private individuals. There is a 2,000-character limit.
3. **Add a state** (required) and, if you know them, an LGA, ward or polling-unit code. These are
   optional and are public identifiers, not personal data.
4. **Say who is reporting** — citizen, observer, party agent, or official. This is a *role*, not an
   identity. No name, phone number or account is stored, and there is no field for one.
5. **Say how serious it seemed** — or leave it as *"not sure / leave it to the reviewer"*. Leaving
   it blank is fine; the system will suggest one or abstain, and either way a human decides.
6. **Attach evidence** (optional). A photo or scan is **hashed on your device before upload**, so
   you can later prove exactly what you submitted.
7. **Location is off by default.** If you enable it, coordinates are rounded to about one kilometre
   and never published. **For reports involving intimidation or violence, consider leaving it
   blank.**
8. **Press *Record and hash this report*.**

You receive a **receipt**: a reference (`rep-…`) and a content hash. **Keep both.** They are how you,
or anyone, can later prove the record was not altered.

What happens next: the report is stored with no identity, linked into an append-only log, and queued
for a human reviewer. SHAIDA will not contact the police, INEC or anyone else on its own.

---

## 2. If you are a reviewer — *Reviewer queue*

This is your worklist.

- **Reports are ordered by harm**, not by arrival time. The score is a published weighted sum
  (severity 0.35, sensitivity 0.20, reach 0.20, evidence 0.10, procedural 0.10, freshness 0.05),
  and each item shows every contribution, so you can see exactly why it is where it is.
- **Filter** by priority band, review state or category.
- **Duplicates are grouped.** Reports describing the same thing appear as one item with a count, so
  you see one entry instead of fifty.
- **Every item is a question.** *Open record* shows the full detail; *Record a decision* is where
  you act.
- **A decision requires a reason.** The form will not accept one without the other. Your decision
  and reason are written into the tamper-evident log.

What the queue will never do: it will not tell you a report is true, and it will not close anything
on its own.

---

## 3. If you are checking results — *Result checks*

Deterministic checks over result records, in two deliberate tiers.

- **Structural findings** are arithmetic contradictions that cannot both be true on a correct
  sheet — for example, accredited voters exceeding the register, or valid votes plus rejected not
  equalling accredited. These are computed, not inferred.
- **Advisory findings** are statistical hints — round-number patterns, digit patterns, turnout
  outliers. They are labelled advisory and never carry structural weight, because they over-fire.
- **Every finding lists plausible innocent explanations to rule out first** — a transcription
  error, a misread faint form, two rows merged by mistake. Read those before you conclude anything.
- **Show arithmetic certificate** displays the figures and the imbalance so you can re-check the
  arithmetic yourself, with a pen.

Toggle *All records* to see the clean ones too. *Run checks on the official synthetic pack* loads
the organisers' 900-unit dataset.

---

## 4. If you are a fact-checker — *Claim matching*

1. **Paste the claim exactly as it reached you** — including the Pidgin, the typos, the mixed
   language. The matcher is built for that.
2. Press *Find the closest archived claim*, or tap an example.

You get a shortlist of similar archived claims, each with its **prior human label**, language and
channel. The tool shows you what a human already concluded about a similar claim. **It does not
label anything itself.**

If nothing is similar enough, it says so and tells you to treat the claim as new and route it to a
human. If the best match is weak, it shows you the candidate **and** tells you it is below its
confidence floor — so you decide, not the tool.

---

## 5. If you are auditing — *Integrity*

- **Re-verify now** re-computes the audit chain from the stored data. It does not trust the writer.
  If any entry had been edited or removed, verification fails and points at the entry.
- The **most recent audit entries** table shows the sequence, the action, the subject, the actor,
  the payload hash and the chain hash.
- **Aggregates** are published only above a privacy floor. Cells below it are **suppressed
  entirely**, never rounded, so an individual report cannot be recovered by subtraction. The page
  shows the floor and the number of suppressed cells.

---

## 6. If you are asking "what does this not do?" — *About and limits*

Read this screen. It states, in the application itself:

- what SHAIDA is, and what it will not do;
- the published triage weights, signal by signal;
- the five supported languages, **and the honest note that the Hausa, Yoruba and Igbo strings are
  first-pass translations that have not yet been reviewed by native speakers**;
- the data and models in use;
- the **six conditions** that must be met before any real use;
- the statement that **this prototype is not approved for operational electoral deployment**, and
  that winning a competition would not change that.

---

## 7. Accessibility and languages

- The interface is keyboard-operable with visible focus rings, meets WCAG 2.2 AA (verified by an
  automated axe-core audit across every page and two viewports), and has touch targets sized for
  mobile use.
- It works on a 320 px-wide screen with no horizontal scrolling.
- Interface strings and reviewer explanations are available in English, Nigerian Pidgin, Hausa,
  Yoruba and Igbo.

---

## 8. If something goes wrong

- **A report will not submit** — check the narrative is under 2,000 characters and that a state is
  selected. The form tells you what is wrong.
- **The page will not load offline** — the app shell caches after the first successful load; if you
  have never loaded it, you need connectivity once.
- **A check shows nothing** — load the official synthetic pack first, or submit result records via
  `POST /v1/results/check`.

Remember throughout: **a flag is a question. You are the one who answers it.**
