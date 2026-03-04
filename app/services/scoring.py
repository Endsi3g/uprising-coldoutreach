"""ICP and Heat scoring engine."""

from __future__ import annotations


# ── Target ICP keywords ─────────────────────────────────────────────────────
# Boost for industries that match typical B2B contractor targets.
HIGH_VALUE_INDUSTRIES = {
    "contractor",
    "plumber",
    "plumbing",
    "electrician",
    "roofer",
    "roofing",
    "hvac",
    "renovation",
    "construction",
    "landscaping",
    "painting",
    "remodeling",
    "general contractor",
    "entrepreneur général",
    "entrepreneur",
    "excavation",
    "demolition",
    "flooring",
    "paving",
    "masonry",
}

HIGH_VALUE_CITIES = {
    "laval",
    "montreal",
    "montréal",
    "longueuil",
    "toronto",
    "ottawa",
    "quebec",
    "québec",
    "gatineau",
    "sherbrooke",
}


def compute_icp_score(
    industry: str | None = None,
    city: str | None = None,
    website: str | None = None,
    phone: str | None = None,
    email: str | None = None,
    google_rating: float | None = None,
    tags: list[str] | None = None,
) -> int:
    """Return a 0-100 score based on lead data quality and ICP fit.

    Scoring breakdown:
    - Industry match:    0-30 pts
    - City match:        0-15 pts
    - Has website:       +10 pts
    - Has phone:         +10 pts
    - Has email:         +15 pts
    - Google rating >=4: +10 pts
    - Tag match bonus:   +10 pts
    """
    score = 0

    # Industry
    if industry:
        lower = industry.lower()
        if any(kw in lower for kw in HIGH_VALUE_INDUSTRIES):
            score += 30
        else:
            score += 10  # at least categorised

    # City
    if city:
        if city.lower().strip() in HIGH_VALUE_CITIES:
            score += 15
        else:
            score += 5

    # Contact info completeness
    if website:
        score += 10
    if phone:
        score += 10
    if email:
        score += 15

    # Google rating
    if google_rating is not None and google_rating >= 4.0:
        score += 10

    # Tags
    if tags:
        tag_lower = {t.lower() for t in tags}
        if tag_lower & HIGH_VALUE_INDUSTRIES:
            score += 10

    return min(score, 100)


def compute_heat_score(
    emails_sent: int = 0,
    emails_opened: int = 0,
    emails_clicked: int = 0,
    replies: int = 0,
    stage_name: str | None = None,
) -> int:
    """Return a 0-100 engagement heat score.

    Scoring breakdown:
    - Opened an email:       +15 per (max 30)
    - Clicked a link:        +15 per (max 30)
    - Replied:               +25 per (max 50)
    - In 'Hot' stage:        +20
    - In 'Booked' stage:     +30
    """
    score = 0

    score += min(emails_opened * 15, 30)
    score += min(emails_clicked * 15, 30)
    score += min(replies * 25, 50)

    if stage_name:
        sl = stage_name.lower()
        if sl == "hot":
            score += 20
        elif sl == "booked":
            score += 30

    return min(score, 100)
