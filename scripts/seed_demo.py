#!/usr/bin/env python
"""Seed the running SHAIDA service with a small, clearly-synthetic demo dataset.

Purpose: give a reviewer (or a judge) something meaningful to look at without anyone having to
type reports by hand. Every record here is invented for demonstration and is labelled as such;
none of it is real election data.

Usage::

    python scripts/seed_demo.py [base_url]
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"

# (category, narrative, state, lga, pu_id, reporter_type, severity, latitude, longitude)
REPORTS = [
    (
        "logistics_delay",
        "Materials for the unit had not arrived by 09:15. About 180 people were waiting in the open with no shade.",
        "Ogun",
        "Abeokuta North",
        "DEMO-00001",
        "observer",
        2,
        7.1557,
        3.3451,
    ),
    (
        "queue_management",
        "A single queue served three polling units, so the line did not move for over an hour.",
        "Ogun",
        "Abeokuta North",
        "DEMO-00002",
        "citizen",
        1,
        None,
        None,
    ),
    (
        "queue_management",
        "One queue was serving several units and the line barely moved all morning.",
        "Ogun",
        "Abeokuta North",
        "DEMO-00003",
        "citizen",
        1,
        None,
        None,
    ),
    (
        "queue_management",
        "The queue for three units was merged and people waited more than an hour.",
        "Ogun",
        "Abeokuta North",
        "DEMO-00004",
        "observer",
        2,
        None,
        None,
    ),
    (
        "equipment_failure",
        "The BVAS at this unit stopped accepting accreditation at 10:40 and was not replaced for two hours.",
        "Kano",
        "Nassarawa",
        "DEMO-00010",
        "party_agent",
        3,
        12.0022,
        8.5919,
    ),
    (
        "accessibility_barrier",
        "A wheelchair user could not reach the polling area because the only route is a steep step with no ramp.",
        "Enugu",
        "Nsukka",
        "DEMO-00020",
        "observer",
        2,
        6.8567,
        7.3958,
    ),
    (
        "information_gap",
        "Many voters did not know which unit they were assigned to and there was no list posted at the entrance.",
        "Kaduna",
        "Kaduna North",
        "DEMO-00030",
        "citizen",
        1,
        None,
        None,
    ),
    (
        "intimidation",
        "Men who were not officials were standing close to the queue telling elderly voters how to vote and following them.",
        "Rivers",
        "Port Harcourt",
        "DEMO-00040",
        "observer",
        4,
        None,
        None,
    ),
    (
        "positive_practice",
        "The presiding officer set up a separate shaded queue for elderly and pregnant voters, which worked well.",
        "Lagos",
        "Ikeja",
        "DEMO-00050",
        "observer",
        0,
        None,
        None,
    ),
    (
        "result_sheet_issue",
        "The figures on the posted result sheet do not add up to the accredited voter count written beside them.",
        "Oyo",
        "Ibadan North",
        "DEMO-00060",
        "party_agent",
        3,
        7.3878,
        3.8964,
    ),
    (
        "result_upload_delay",
        "The unit closed at 15:00 but the result sheet was still not uploaded to the portal four hours later.",
        "Oyo",
        "Ibadan North",
        "DEMO-00061",
        "observer",
        2,
        None,
        None,
    ),
    (
        "misinformation_claim",
        "A voice note is going round saying accreditation was cancelled in this area, which is not what people at the unit saw.",
        "Kano",
        "Nassarawa",
        "DEMO-00011",
        "citizen",
        2,
        0.0,
        0.0,
    ),
]


def post(path: str, payload: dict) -> dict:
    request = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return {"error": exc.read().decode("utf-8"), "status": exc.code}


def main() -> int:
    created = 0
    for index, (
        category,
        narrative,
        state,
        lga,
        pu_id,
        reporter_type,
        severity,
        lat,
        lon,
    ) in enumerate(REPORTS):
        payload = {
            "category": category,
            "narrative": narrative,
            "state_name": state,
            "lga": lga,
            "pu_id": pu_id,
            "reporter_type": reporter_type,
            "channel": "seed",
            "severity_reported": severity,
        }
        # A couple of coordinates that are deliberately not (0,0), which is what the
        # misinformation entry uses to mean "no location given".
        if lat not in (None, 0.0) and lon not in (None, 0.0):
            payload["latitude"] = lat
            payload["longitude"] = lon
        result = post("/v1/reports", payload)
        if "error" in result:
            print(f"  [{index + 1}] FAILED {category}: {result['error'][:120]}")
        else:
            created += 1
            print(f"  [{index + 1}] {result['id']} {category} -> {result['priority_band']}")

    # Run the deterministic checks on the organisers' own pack so the results view is populated.
    loaded = post("/v1/results/load-official", {})
    if "error" in loaded:
        print(f"  official pack: FAILED {loaded['error'][:120]}")
    else:
        print(
            f"  official pack: {loaded['ingested']} records checked, {loaded['flagged']} flagged "
            f"({loaded['flag_rate']:.1%})"
        )

    # Record one human decision so the review trail is visible.
    listing = urllib.request.urlopen(f"{BASE}/v1/reports?limit=1", timeout=30)
    first = json.loads(listing.read().decode("utf-8"))["reports"]
    if first:
        result = post(
            f"/v1/reports/{first[0]['id']}/review",
            {
                "reviewer": "demo-reviewer",
                "decision": "referred_to_cso",
                "reason": "Logged and passed to the CSO desk for a welfare follow-up.",
                "note": "Seeded demonstration decision.",
            },
        )
        print(f"  review recorded: {'ok' if 'error' not in result else result['error'][:80]}")

    print(f"\n{created} demonstration reports created (all synthetic).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
