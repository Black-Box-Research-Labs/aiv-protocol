"""
aiv/svp/lib/rating.py

Automated ELO rating engine for SVP verifiers.
Reads SVP session data and generates RatingEvents per RATING_POINTS map.
Implements svp-rating component per SVP-SUITE-SPEC-V1.0-CANONICAL §9.
"""

from __future__ import annotations

import json
from pathlib import Path

from .models import (
    RATING_POINTS,
    RatingEvent,
    SVPSession,
    SVPStatus,
    VerifierRating,
)


def score_session(session: SVPSession) -> list[RatingEvent]:
    """Generate rating events from a completed (or partial) SVP session.

    Scoring rules:
    - Probe findings with is_confirmed_bug=True → bug_caught_{severity}
    - Falsification scenarios checked+falsified → bug_caught_medium
    - Falsification scenarios checked+result != confirmed → false_positive
      (only when the scenario itself was wrong, not the claim)
    - Ownership commit with high docstring quality → ownership_high_quality
    - Session fully complete → svp_completed bonus
    """
    events: list[RatingEvent] = []
    vid = session.verifier_id
    pr = session.pr_number
    repo = session.repository

    # --- Bugs caught from probe findings ---
    if session.probe:
        for finding in session.probe.findings:
            if finding.is_confirmed_bug:
                event_type = f"bug_caught_{finding.severity.value}"
                points = RATING_POINTS.get(event_type, 0)
                if points:
                    events.append(
                        RatingEvent(
                            verifier_id=vid,
                            event_type=event_type,
                            points=points,
                            pr_number=pr,
                            repository=repo,
                            description=(f"Confirmed bug in {finding.file_path}: {finding.description[:80]}"),
                        )
                    )

    # --- Falsification scenario results ---
    if session.probe:
        for scenario in session.probe.falsification_scenarios:
            if not scenario.checked:
                continue
            if scenario.result == "falsified":
                # Verifier correctly identified a false claim — reward
                points = RATING_POINTS["bug_caught_medium"]
                events.append(
                    RatingEvent(
                        verifier_id=vid,
                        event_type="bug_caught_medium",
                        points=points,
                        pr_number=pr,
                        repository=repo,
                        description=(f"Falsified {scenario.claim_id}: {scenario.scenario[:60]}"),
                    )
                )
            elif scenario.result == "inconclusive":
                # No penalty, no reward — ambiguous result
                pass

            # Penalize scenarios that were themselves wrong (hallucinated,
            # wrong count, untestable).  Scored independently of result.
            if scenario.false_positive:
                fp_points = RATING_POINTS["false_positive"]
                events.append(
                    RatingEvent(
                        verifier_id=vid,
                        event_type="false_positive",
                        points=fp_points,
                        pr_number=pr,
                        repository=repo,
                        description=(f"False positive scenario {scenario.claim_id}: {scenario.scenario[:60]}"),
                    )
                )

    # --- Ownership quality ---
    if session.ownership_commit is not None:
        score = session.ownership_commit.docstring_quality_score
        if score >= 80:
            points = RATING_POINTS["ownership_high_quality"]
            events.append(
                RatingEvent(
                    verifier_id=vid,
                    event_type="ownership_high_quality",
                    points=points,
                    pr_number=pr,
                    repository=repo,
                    description=f"High-quality ownership commit (score={score}%)",
                )
            )

    # --- SVP completion bonus ---
    if session.status == SVPStatus.COMPLETE:
        points = RATING_POINTS["svp_completed"]
        events.append(
            RatingEvent(
                verifier_id=vid,
                event_type="svp_completed",
                points=points,
                pr_number=pr,
                repository=repo,
                description="SVP session completed with all phases.",
            )
        )

    return events


def calculate_rating(
    verifier_id: str,
    sessions: list[SVPSession],
) -> tuple[VerifierRating, list[RatingEvent]]:
    """Calculate a verifier's ELO rating from all their sessions.

    Returns the final rating and the full event log.
    """
    rating = VerifierRating(verifier_id=verifier_id)
    all_events: list[RatingEvent] = []

    for session in sessions:
        if session.verifier_id != verifier_id:
            continue
        events = score_session(session)
        for event in events:
            rating.apply_event(event)
        all_events.extend(events)

    rating.total_reviews = len([s for s in sessions if s.verifier_id == verifier_id])
    rating.bugs_caught = len([e for e in all_events if e.event_type.startswith("bug_caught")])
    rating.false_positives = len([e for e in all_events if e.event_type == "false_positive"])

    return rating, all_events


# ------------------------------------------------------------------ #
# Persistence
# ------------------------------------------------------------------ #

RATINGS_FILE = Path(".svp") / "ratings.json"


def load_ratings() -> dict[str, VerifierRating]:
    """Load all verifier ratings from disk."""
    if not RATINGS_FILE.exists():
        return {}
    data = json.loads(RATINGS_FILE.read_text(encoding="utf-8"))
    return {vid: VerifierRating.model_validate(r) for vid, r in data.items()}


def save_ratings(ratings: dict[str, VerifierRating]) -> None:
    """Persist verifier ratings to disk."""
    RATINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = {vid: r.model_dump(mode="json") for vid, r in ratings.items()}
    RATINGS_FILE.write_text(
        json.dumps(data, indent=2, default=str) + "\n",
        encoding="utf-8",
    )


def load_all_sessions() -> list[SVPSession]:
    """Load all SVP sessions from the .svp/ directory."""
    svp_dir = Path(".svp")
    if not svp_dir.exists():
        return []
    sessions: list[SVPSession] = []
    for p in sorted(svp_dir.glob("session-pr*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            sessions.append(SVPSession.model_validate(data))
        except Exception:
            continue
    return sessions
