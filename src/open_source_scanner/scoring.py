from __future__ import annotations

from datetime import UTC, datetime

from open_source_scanner.models import FeedbackStatus, Opportunity, ScoreBreakdown, ScoringConfig


def score_opportunity(
    opportunity: Opportunity,
    config: ScoringConfig,
    now: datetime | None = None,
    feedback_status: FeedbackStatus = "new",
) -> ScoreBreakdown:
    current_time = now or datetime.now(tz=UTC)
    reasons: list[str] = []
    penalties: list[str] = []
    total = 0

    popularity_weight = config.weights.get("repo_popularity", 0)
    if opportunity.stars >= 1000:
        total += popularity_weight
        reasons.append(f"popular repository: {opportunity.stars} stars (+{popularity_weight})")
    elif opportunity.stars >= 100:
        partial = popularity_weight // 2
        total += partial
        reasons.append(f"moderately popular repository: {opportunity.stars} stars (+{partial})")

    age_days = max((current_time - opportunity.pushed_at).days, 0)
    if age_days <= 30:
        weight = config.weights.get("recent_activity", 0)
        total += weight
        reasons.append(f"recent activity: pushed {age_days} days ago (+{weight})")
    elif age_days > 180:
        penalty = config.penalties.get("stale_repo", 0)
        total += penalty
        penalties.append(f"stale repository: pushed {age_days} days ago ({penalty})")

    if opportunity.packaging_signals:
        weight = config.weights.get("packaging_fit", 0)
        total += weight
        reasons.append(
            f"packaging fit signals: {', '.join(opportunity.packaging_signals)} (+{weight})"
        )

    license_id = opportunity.license_spdx_id.casefold() if opportunity.license_spdx_id else None
    if license_id in config.preferred_licenses:
        weight = config.weights.get("license_fit", 0)
        total += weight
        reasons.append(f"preferred license: {license_id} (+{weight})")
    elif license_id in config.caution_licenses:
        penalty = config.penalties.get("restrictive_license", 0)
        total += penalty
        penalties.append(f"caution license: {license_id} ({penalty})")
    else:
        penalty = config.penalties.get("unknown_license", 0)
        total += penalty
        penalties.append(f"unknown license ({penalty})")

    if not opportunity.archived and opportunity.open_issues <= 50:
        weight = config.weights.get("low_friction", 0)
        total += weight
        reasons.append(f"low friction: {opportunity.open_issues} open issues (+{weight})")

    if feedback_status in {"saved", "watch", "package"}:
        weight = config.weights.get("feedback_bonus", 0)
        total += weight
        reasons.append(f"feedback bonus: {feedback_status} (+{weight})")

    if opportunity.archived:
        penalty = config.penalties.get("archived_repo", 0)
        total += penalty
        penalties.append(f"archived repository ({penalty})")

    if len(opportunity.description.strip()) < 20:
        penalty = config.penalties.get("weak_description", 0)
        total += penalty
        penalties.append(f"weak description: fewer than 20 characters ({penalty})")

    return ScoreBreakdown(total=max(total, 0), reasons=reasons, penalties=penalties)
