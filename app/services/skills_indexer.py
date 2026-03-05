"""Skills indexer service — scans the skills/ directory and builds a searchable index.

This is a 100% zero-dependency implementation using only stdlib:
- Parses YAML frontmatter from SKILL.md files using simple regex
- TF-IDF-inspired keyword scoring for skill search
- Caches index to disk as JSON
"""

from __future__ import annotations

import json
import logging
import math
import os
import re
from pathlib import Path

logger = logging.getLogger(__name__)

# Locate project root (2 levels up from this file: app/services/ → app/ → root)
_PROJECT_ROOT = Path(__file__).parent.parent.parent
SKILLS_DIR = _PROJECT_ROOT / "skills"
INDEX_CACHE = _PROJECT_ROOT / "data" / "skills_index.json"


def _parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from a SKILL.md file."""
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    fm_text = match.group(1)
    result = {}
    for line in fm_text.splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            result[key.strip()] = val.strip().strip('"')
    return result


def build_index() -> list[dict]:
    """Scan skills directory and return list of skill descriptors."""
    if not SKILLS_DIR.exists():
        logger.warning(f"Skills directory not found: {SKILLS_DIR}")
        return []

    skills = []
    for skill_md in SKILLS_DIR.rglob("SKILL.md"):
        try:
            content = skill_md.read_text(encoding="utf-8", errors="ignore")
            fm = _parse_frontmatter(content)
            # Get skill folder name as fallback for name
            skill_name = fm.get("name") or skill_md.parent.name
            description = fm.get("description") or ""
            # Body text (after frontmatter) for richer search
            body = re.sub(r"^---.*?---\s*", "", content, count=1, flags=re.DOTALL).strip()
            skills.append(
                {
                    "name": skill_name,
                    "slug": skill_md.parent.name,
                    "description": description,
                    "path": str(skill_md.relative_to(_PROJECT_ROOT).as_posix()),
                    "body_preview": body[:500],
                }
            )
        except Exception as e:
            logger.debug(f"Could not parse {skill_md}: {e}")

    logger.info(f"Indexed {len(skills)} skills from {SKILLS_DIR}")
    return skills


def save_index(skills: list[dict]) -> None:
    """Persist the index to disk."""
    INDEX_CACHE.parent.mkdir(parents=True, exist_ok=True)
    INDEX_CACHE.write_text(json.dumps(skills, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"Skills index saved to {INDEX_CACHE}")


def load_index() -> list[dict]:
    """Load index from cache, or rebuild from disk if cache is missing."""
    if INDEX_CACHE.exists():
        try:
            return json.loads(INDEX_CACHE.read_text(encoding="utf-8"))
        except Exception:
            pass
    skills = build_index()
    if skills:
        save_index(skills)
    return skills


def _tokenize(text: str) -> list[str]:
    """Simple lowercase word tokenizer."""
    return re.findall(r"[a-z0-9]+", text.lower())


def search_skills(query: str, top_n: int = 5) -> list[dict]:
    """Search skills using TF-IDF-inspired keyword scoring.

    Returns up to top_n skills ranked by relevance.
    """
    skills = load_index()
    if not skills:
        return []

    query_tokens = set(_tokenize(query))
    if not query_tokens:
        return skills[:top_n]

    scored = []
    num_docs = len(skills)

    # Precompute IDF for each query token
    idf: dict[str, float] = {}
    for token in query_tokens:
        docs_containing = sum(
            1 for s in skills
            if token in _tokenize(s["name"] + " " + s["description"] + " " + s["body_preview"])
        )
        idf[token] = math.log((num_docs + 1) / (docs_containing + 1)) + 1.0

    for skill in skills:
        doc_text = (skill["name"] + " " + skill["slug"] + " " + skill["description"] + " " + skill["body_preview"])
        doc_tokens = _tokenize(doc_text)
        if not doc_tokens:
            continue

        # Term frequency component
        tf_sum = 0.0
        for token in query_tokens:
            tf = doc_tokens.count(token) / len(doc_tokens)
            tf_sum += tf * idf.get(token, 1.0)

        # Bonus for exact slug/name match
        slug_bonus = 2.0 if any(t in skill["slug"].lower() for t in query_tokens) else 0.0
        name_bonus = 3.0 if any(t in skill["name"].lower() for t in query_tokens) else 0.0

        score = tf_sum + slug_bonus + name_bonus
        if score > 0:
            scored.append((score, skill))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [s for _, s in scored[:top_n]]
