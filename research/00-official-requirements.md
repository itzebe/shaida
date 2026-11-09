# Phase 0 — Official Competition Requirements

**Competition:** Rise Networks **#AI4Elections Hackathon 2026–2027**
**Programme:** https://ai4elections.risenetworks.org/
**Official public repository:** https://github.com/Rise-Networks-AI-Labs/-AI4Elections-Hackathon
**Official concept document (PDF):** `Concept_Doc_AI4Elections_by_Rise_Networks_in_Collaboration_with_INEC_and_Partners.pdf`
**Captured:** 2026-11-09

> Source hierarchy used: (1) the official website, (2) the official public GitHub repository
> (`docs/01_technical_briefs/*`, `docs/03_onboarding/onboarding_guide.md`, `README.md`,
> `docs/05_templates/*`, `data/synthetic/*`), and (3) the official concept-document PDF.
> Secondary publications were used only to supplement and are marked as such.

---

## 1. Verified programme facts

| Item | Official value | Source |
|---|---|---|
| Organiser | Rise Networks (Rise Human and Education Development Networks LTD/GTE) | Website, PDF |
| Named collaborators | INEC; ICIR; Google; Microsoft; Meta; NITHUB (UNILAG); CITAD; CLEEN Foundation; Tap Initiative; IPC; Legal Naija; ABU; FUTA. Support: MacArthur Foundation, Luminate | Website FAQ, PDF |
| Programme window | October 2026 – February 2027 | PDF §9 |
| Applications open | 22 October 2026 | PDF §9, onboarding guide |
| **Application deadline** | **12 November 2026, 11:59 PM WAT** | Website, PDF §9 |
| Application screening / shortlisting | 13–16 November 2026 | Onboarding guide §1 |
| Onboarding & kick-off | 18–19 November 2026 | Onboarding guide §1 |
| Ideation / bootcamp / mentor matching | 23–27 November 2026 | Onboarding guide §1 |
| **Prototype development, testing, submission, documentation** | **28 November – 13 December 2026** | Onboarding guide §1 |
| **Prototype submission deadline** | **13 December 2026** | `README.md`; general rules |
| Demo Day / live judging | 15–16 December 2026 | Onboarding guide §1 |
| Grand finale / award presentation | 16 December 2026 | PDF §9, onboarding guide |
| Prize pool | ₦10,000,000 | PDF §11 |
| 1st — Grand Prize (Overall Champion) | ₦4,000,000 | PDF §11 |
| 2nd — Runner-up | ₦2,500,000 | PDF §11 |
| 3rd — Second Runner-up | ₦1,500,000 | PDF §11 |
| 4 Special Innovation Awards | ₦500,000 each | PDF §11 |
| Winning team size for overall prize | Counts as one of the three final winning teams | PDF §7 |
| Post-hackathon | #AI4Elections Development Hub (2–4 teams, 8–12 weeks virtual) + Community of Practice | PDF §13 |

> **Critical correction.** The mission brief stated the application deadline as the operative deadline and
> proposed a **two-minute** demo. The official rules are explicit: the **application** closes 12 Nov 2026,
> but the **prototype + documentation package is due 13 December 2026**, and the **demo video is "3 minutes
> max"** (`docs/01_technical_briefs/00_general_challenge_rules.md`). This project therefore targets a
> **≤3-minute** demo. The application itself is submitted by the user by 12 Nov 2026.

---

## 2. The five official tracks

Source: `docs/01_technical_briefs/track{1..5}_*.md` and the website "Hackathon Tracks" section.

| # | Official track title | Focus |
|---|---|---|
| 1 | AI and Electoral Information Integrity | Detect/assess/respond to AI-generated or manipulated electoral information; synthetic media, impersonation, misleading content, especially Nigerian languages and WhatsApp-like channels |
| 2 | Electoral Data Intelligence | Responsible AI on **authorised, public or synthetic** electoral data; data quality, document processing, logistics, anomaly surfacing **for human review** |
| 3 | Inclusive and Multilingual Civic Tech | Remove barriers: language, disability, digital literacy, distance, low connectivity |
| 4 | Electoral Cybersecurity and Resilience | **Defensive** tools, **authorised simulations**, privacy-preserving designs, resilience/failover, awareness, threat models |
| 5 | Election Observation and Citizen Accountability | Structured observation reporting, incident documentation, civic feedback, public-information access, with safeguards for observers and citizens |

The website's "Who should participate" section lists 10 participant profiles (students, developers, cybersecurity professionals, researchers, startups, electoral experts, designers, linguists, policy professionals, emerging innovators) — reinforcing that **multidisciplinary, non-technical framing is valued**.

---

## 3. Published judging rubric (weights)

Source: PDF §12 and `00_general_challenge_rules.md`. The website FAQ states the same factors qualitatively.

| Criterion | Weight |
|---|---|
| Technical functionality and innovation | 25% |
| Electoral relevance and practical usefulness | 20% |
| Cybersecurity, privacy and responsible AI | 20% |
| Inclusion, accessibility and multilingual capability | 15% |
| Scalability, sustainability and feasibility | 15% |
| Demonstration and documentation | 5% |
| **Total** | **100%** |

Plus a **hard exclusion rule**: *"Projects presenting critical security, privacy, safety or legal concerns may be excluded from awards or further testing, regardless of their technical score."*

Judging council: six senior professionals — a legal expert, a data/AI expert, a civil society expert, a media leader, an INEC official, and a cybersecurity expert. Conflicts of interest must be disclosed; judges do not score teams they mentored.

---

## 4. Eligibility (official)

| Rule | Detail |
|---|---|
| Nationality / age | **Nigerian origin**, **≥18 years** as at the deadline date |
| Team size | **Minimum 2, maximum 4** persons. Individual applicants may be team-matched by organisers |
| Registration | Every member registers individually and must be identified as part of the same team **before the registration deadline** |
| Membership freeze | Team membership **cannot change** after the hackathon begins |
| Judging unit | Team entries judged as a **single entry**; awards paid to the team collectively |
| Academia pathway | ≥1 faculty lead + student/post-grad researcher + HOD approval letter from an accredited Nigerian institution |
| Start-up/org pathway | Valid CAC registration; ≥60% of team resident in Nigeria; government ID for all members |
| Individual pathway | Valid government ID (+ ID of any affiliated organisation) |
| Language | Applications **in English only** |
| Geography | Broad participation across the six geopolitical zones encouraged; targeted outreach to women, PWDs, underserved communities |

**Explicitly ineligible:** idea-only proposals; decks; presentations; research papers; applications in any language other than English; non-Nigerian applicants; mock-ups; and **projects that have already received any form of grant, award or recognition in other previous competitions.**

---

## 5. Mandatory non-negotiables (all tracks)

Source: `docs/01_technical_briefs/00_general_challenge_rules.md`.

1. **Nonpartisan.** No campaign tech, voter persuasion, microtargeting, or manipulation of participation.
2. **No live systems.** No testing of, or access to, live electoral systems or institutional infrastructure. **Disqualifying.**
3. **Data:** synthetic, public, or explicitly authorised only. Prefer anonymised/aggregated. **No scraping of personal data.**
4. **Human oversight.** Tools flag, assist, or inform. They do **not** declare results, decide eligibility, or auto-sanction people.
5. **Working prototype required.** Idea-only decks, mock-ups, slide-only entries are ineligible.
6. **Document limits and safeguards.** Every submission states what it cannot do and what is needed before further testing.
7. **Winning is not approval** for operational deployment.

Track-specific **red lines** relevant to this project:
- **Track 1:** no auto-removal or public labelling of individuals' speech as false without human review; no political-opinion profiling; no creation of deceptive content.
- **Track 2:** no fraud accusations; no predicting winners for persuasion; no re-identifying individuals; no unauthorised results data. Pitfall: **base-rate fallacy** (rare anomalies + imperfect detector = many false alarms).
- **Track 3:** no invented electoral rules/dates; no advice that could disenfranchise; no collecting disability data without consent and need. Target: **zero unsupported answers**.
- **Track 4:** no scanning/probing/exploiting/load-testing any live system; no malware; no credential harvesting; no social-engineering real people. **Any unauthorised access attempt = immediate disqualification.**
- **Track 5:** no publishing unverified accusations naming individuals; no collecting reporter identity by default; no location precision that endangers observers; no partisan use.

---

## 6. Minimum submission package (due 13 December 2026)

Source: `00_general_challenge_rules.md`.

| Item | Requirement |
|---|---|
| Working prototype | Runs from the repo following the README; demo link or reproducible setup |
| Repository | Public repo forked from the hackathon template; open licence chosen by the team |
| Problem statement | Which brief, which user, which pain (≤1 page) |
| Methodology | Approach, data used, evaluation method |
| Evidence | Metrics with test-set description, screenshots/recording, failure cases |
| Model / System Card | `docs/05_templates/MODEL_CARD.md` |
| Safety and Limitations | `docs/05_templates/SAFETY_AND_LIMITATIONS.md` |
| Data Sheet | `docs/05_templates/DATASHEET.md` (any dataset created/used) |
| Demo video | **3 minutes max** |

---

## 7. IP, licensing, data protection and responsible AI

| Topic | Official position |
|---|---|
| IP | "IP terms will be published before the competition"; teams encouraged to use open licences; confirm in the participant agreement (`onboarding_guide.md` §8) |
| Repository licence | **Code: MIT**; **Documentation and synthetic data: CC BY 4.0** (unless stated otherwise) |
| Data protection | Compliance with applicable data-protection legislation (incl. **NDPA 2023**) and the Competition's data-governance requirements is **mandatory** where personal data is involved |
| Responsible AI | Responsible AI, privacy, cybersecurity and human-oversight requirements apply across all tracks |
| Third-party tools/APIs | Permitted subject to rules, licences, data-protection requirements and disclosure of material third-party tools |
| AI assistance | Must be disclosed in docs (`CONTRIBUTING_AND_CODE_STYLE.md`) |
| Deployment | Prototypes "should not be assumed to be eligible for deployment in critical 2027 election systems"; evaluation should occur in a controlled sandbox with synthetic/anonymised/public data and no connection to production electoral systems |
| Compute | Microsoft Azure credits may be provided "subject to applicable terms and allocation limits" — **not guaranteed** |

---

## 8. Compliance matrix

`Requirement | Official evidence | Product implication | Verification method | Status`

| # | Requirement | Official evidence | Product implication | Verification method | Status |
|---|---|---|---|---|---|
| R1 | Nonpartisan; no persuasion/microtargeting | `00_general_challenge_rules.md` §1 | No candidate/party features; no voter targeting; neutral language | Code review + feature audit; no party/candidate entities in schema | Met |
| R2 | No live/institutional system access (disqualifying) | `00_general_challenge_rules.md` §2 | All data synthetic/public; no network calls to INEC/IReV/BVAS | Grep for external hosts; offline test run; documented in Safety doc | Met |
| R3 | Only synthetic/public/authorised data; no personal-data scraping | `00_general_challenge_rules.md` §3 | Use official synthetic pack + self-generated synthetic data only | Datasheet; dataset provenance; no PII fields | Met |
| R4 | Human oversight; tools flag only, never declare results | `00_general_challenge_rules.md` §4; Track 2 red lines | Deterministic checks emit **flags**; AI drafts explanations; reviewer decides; no fraud verdicts | Review queue in app; UI copy audit; tests asserting no "fraud/winner" output | Met |
| R5 | Working prototype (not mock-ups) | `00_general_challenge_rules.md` §5 | Real FastAPI backend + React PWA with persistent storage | End-to-end test; run instructions; live demo URL | Met |
| R6 | Document limits and safeguards | `00_general_challenge_rules.md` §6 | `SAFETY_AND_LIMITATIONS.md`; in-app "what this does not do" | Doc review | Met |
| R7 | Winning ≠ deployment approval | `00_general_challenge_rules.md` §7 | Explicit disclaimer in app + docs | Doc/UI review | Met |
| R8 | Track alignment (choose a brief) | `docs/01_technical_briefs/track{1..5}` | Primary: Track 5 (5B/5C) + Track 2 (2A/2D) + Track 4 (4B/4D); multilingual per Track 3 | Map each feature to a brief item in README | Met |
| R9 | Public repo + open licence | General rules; README | MIT licence + CC BY 4.0 for docs/data | `LICENSE` present; repo public | Met |
| R10 | Problem statement ≤1 page | General rules | `docs/PROBLEM-STATEMENT.md` | Length check | Met |
| R11 | Methodology | General rules | `docs/AI-METHODOLOGY.md`, `evaluation/DATASET-METHODOLOGY.md` | Doc review | Met |
| R12 | Evidence: metrics + test-set description + failure cases | General rules | `evaluation/RESULTS.md`, `evaluation/TEST-CASES.md` | Reproducible command in `RESULTS.md` | Met |
| R13 | Model/System Card | `MODEL_CARD.md` template | `docs/MODEL-CARD.md` | Template completeness check | Met |
| R14 | Safety & Limitations | `SAFETY_AND_LIMITATIONS.md` template | `docs/SAFETY-AND-LIMITATIONS.md` | Template completeness check | Met |
| R15 | Data Sheet | `DATASHEET.md` template | `evaluation/DATASHEET.md` | Template completeness check | Met |
| R16 | Demo video ≤3 min | General rules | ≤3-min MP4 + storyboard + narration | Video duration probe (`ffprobe`) | Met (see demo) |
| R17 | NDPA 2023 data-protection compliance | PDF §6/§12; onboarding §8 | Data minimisation, consent, k-anonymity, retention, deletion, no reporter identity by default | `docs/DATA-PROTECTION.md`; tests for anonymisation | Met |
| R18 | Responsible-AI safeguards | PDF §6/§12 | Abstention, uncertainty, explainability, human review, no fabricated data | `docs/RESPONSIBLE-AI.md`; calibration tests | Met |
| R19 | Disclosure of AI-tool assistance | `CONTRIBUTING_AND_CODE_STYLE.md` | README "AI assistance" section | README review | Met |
| R20 | Only English applications; user submits | PDF §7 | Docs in English; applicant personal details left blank | `docs/COMPETITION-APPLICATION.md` | Met (user completes) |
| R21 | No prior grants/awards for the project | PDF §7 | Project is newly built for this competition | Declaration in README | Met |
| R22 | Demonstration with real app, no fake data | Mission + general rules §5 | Demo recorded against the running local app | Recording + run log | Met |
| R23 | No unauthorised security testing | Track 4 scope | Security features are defensive only; self-testing only | Code review; scope doc | Met |
| R24 | Accessibility (WCAG 2.2 AA expected) | Track 3; design constitution | Mobile-first, keyboard, contrast, labels, alt text, reduced-motion | Automated axe audit + manual checks | Met |
| R25 | Multilingual capability | Track 3 | en/pcm/ha/yo/ig interface strings | Per-language UI test | Met |

---

## 9. Assumptions and open items

- **Demo video length:** official = 3 min max. (Mission brief said 2 min "subject to confirmation" — superseded.)
- **Final submission deadline time** on 13 Dec 2026 is "to be confirmed by organisers" (onboarding §6).
- **IP terms** are promised "before the competition" and are not yet published; this project uses MIT + CC BY 4.0, which is the repository default.
- **Cloud credits** are not guaranteed; the entire prototype is therefore designed to run on **free, local, open-source** infrastructure with no paid dependency and no API key required.
- **Judging rubric** is published and stable across the PDF and the technical briefs.
