"""Duplicate detection and clustering for incoming reports.

When 200 people report the same broken BVAS, a reviewer should see *one* item with a count,
not 200 items. Clustering is a large part of the measurable "reviewer workload saved" that
the official Track 1 and Track 5 success criteria ask for ("alerts per 1,000 records",
"time-to-triage saved for a reviewer").

The algorithm is deterministic and dependency-free: a report joins an existing cluster when
its character-n-gram Jaccard similarity to the cluster's representative exceeds a threshold
*and* the category matches. Determinism matters because reviewers must be able to reproduce
why two reports were grouped.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from .text import jaccard


@dataclass
class Cluster:
    cluster_id: str
    representative: str
    category: str
    member_ids: list[str] = field(default_factory=list)
    texts: list[str] = field(default_factory=list)

    @property
    def size(self) -> int:
        return len(self.member_ids)


class Clusterer:
    """Greedy, deterministic, threshold-based clustering."""

    def __init__(self, threshold: float = 0.55) -> None:
        self.threshold = threshold
        self.clusters: dict[str, Cluster] = {}
        self._counter = 0

    def assign(self, report_id: str, category: str, narrative: str) -> tuple[str, int]:
        """Return ``(cluster_id, cluster_size_after_assignment)``."""
        best: Cluster | None = None
        best_score = 0.0
        for cluster in self.clusters.values():
            if cluster.category != category:
                continue
            score = jaccard(cluster.representative, narrative)
            if score > best_score:
                best, best_score = cluster, score

        if best is not None and best_score >= self.threshold:
            best.member_ids.append(report_id)
            best.texts.append(narrative)
            return best.cluster_id, best.size

        self._counter += 1
        cluster_id = f"clu-{self._counter:05d}"
        self.clusters[cluster_id] = Cluster(
            cluster_id=cluster_id,
            representative=narrative,
            category=category,
            member_ids=[report_id],
            texts=[narrative],
        )
        return cluster_id, 1

    def size_of(self, cluster_id: str) -> int:
        cluster = self.clusters.get(cluster_id)
        return cluster.size if cluster else 0

    def summary(self) -> list[dict[str, object]]:
        return sorted(
            (
                {
                    "cluster_id": c.cluster_id,
                    "category": c.category,
                    "size": c.size,
                    "example": c.representative[:120],
                }
                for c in self.clusters.values()
            ),
            key=lambda item: -int(item["size"]),
        )
