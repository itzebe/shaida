# Problem statement

*≤1 page, as the official rules require.*

---

## The problem

Three failures recur across Nigerian elections, and they compound each other.

**1. Evidence cannot be trusted later.** A citizen photographs a result sheet. An observer records
a voice note about intimidation. Within hours the image is forwarded, screenshotted, re-compressed
and re-posted. By the time anyone wants to act on it, there is no way to prove that *this* file is
what was captured at *that* time. A screenshot cannot prove it was not edited. A hash that nobody
recorded at capture cannot prove anything afterwards. The evidence exists; its integrity does not
survive contact with the network.

**2. The checkable arithmetic is not checked.** An EC8A result sheet contains its own internal
arithmetic: the register figure, accredited voters, rejected ballots, per-party tallies. When those
numbers do not close — when accredited voters exceed the register, or valid votes plus rejected do
not equal accredited — that is a **deterministic contradiction**, true or false regardless of
anyone's opinion. It is computable in microseconds. Yet it is rarely computed systematically
*before* allegations are made, because the checking is manual, tedious and unbounded. The result is
that allegations are made without the one piece of evidence that is unambiguous, and genuine
transcription errors are mistaken for misconduct.

**3. Reviewer attention is the scarce resource, and it is allocated badly.** A civil-society
hotline on election day receives thousands of messages. Many are duplicates of the same event. Many
are low-value. A small number describe intimidation, violence or a serious procedural breach and
need attention within the hour. A first-come-first-served queue spends its first hours on whatever
arrived first, not on what matters most. The organisations best placed to respond are the ones
least able to read everything.

## Who experiences it

| Who | How the problem lands on them |
|---|---|
| **The citizen who reports** | Their report is either ignored or, worse, exposes them — because reporting tools collect names and precise GPS by default, and an intimidation report that identifies its author endangers its author |
| **The observer or CSO monitor** | Buried in volume; cannot triage by harm; cannot prove later that a report was unaltered |
| **The fact-checker or journalist** | Receives a claim already circulating and cannot quickly tell whether it is a re-worded version of something already checked |
| **The reviewer** | Given a flat list with no reasoning and no priority, and asked to decide without a documented basis |
| **The public** | Sees claims and counter-claims with no way to check either, which corrodes trust regardless of what actually happened |

## Why existing approaches are insufficient

- **IReV** publishes results but is an institutional record; it does not give a citizen a
  verifiable copy of their own evidence, and it is not a triage system.
- **Observation coalitions and PVT** are methodologically strong but sample-level and
  human-mediated; they do not provide unit-level evidence hygiene or a privacy-preserving reporting
  primitive.
- **Fact-checking platforms** are editorial and capacity-bound; they cannot be everywhere, and they
  operate after a claim has spread.
- **Generic reporting forms** collect identity by default and do nothing about evidence integrity,
  triage or accountability.
- **"AI election tools"** — chatbots and classifiers — typically *declare*: they label a claim
  false or imply a unit is fraudulent. The competition's own briefs forbid exactly this, because an
  unaccountable model output laundered into an accusation is a public harm.

## The gap SHAIDA fills

Not more data, and not another model. **Provenance, deterministic verification, privacy and
accountable human review, in one workflow** — so that evidence can be proven unaltered, arithmetic
can be checked by anyone, scarce attention goes to the riskiest reports first, and no tool ever
declares a verdict on a person or an election.

## What success looks like

A citizen files a report with no identity, offline, and holds a hash that proves it was not
altered. An observer's queue is ordered by harm, with duplicates grouped and each item carrying a
reason. A reviewer records a decision and a reason that is written to a log anyone can re-verify.
And the system, at every point, has said nothing about who won or who is guilty.
