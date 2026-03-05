"""MCP Skills API — Model Context Protocol compatible skill discovery endpoints.

Allows any MCP-compatible client (or the AI agent itself) to:
 - List all indexed skills
 - Search for the best skill for a given task description
 - Fetch the full content of a specific skill
 - Trigger a re-index of the skills directory
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse
from pathlib import Path

from app.services.skills_indexer import (
    build_index,
    load_index,
    save_index,
    search_skills,
    SKILLS_DIR,
    _PROJECT_ROOT,
)

router = APIRouter(prefix="/mcp", tags=["MCP Skills"])


@router.get("/skills", summary="List all indexed skills")
def list_skills():
    """Return the complete list of available skills with name, description, and path."""
    skills = load_index()
    return {
        "total": len(skills),
        "skills": [
            {"name": s["name"], "slug": s["slug"], "description": s["description"], "path": s["path"]}
            for s in skills
        ],
    }


@router.get("/find", summary="Find best skills for a task description")
def find_skills(
    task: str = Query(..., description="Natural language description of the task you want to accomplish"),
    top: int = Query(5, ge=1, le=20, description="Number of skills to return"),
):
    """Search the skills index and return the top-N most relevant skills for the given task.

    Example: GET /mcp/find?task=build+a+fastapi+REST+API&top=5
    """
    if not task.strip():
        raise HTTPException(400, "task query parameter must not be empty")
    results = search_skills(task.strip(), top_n=top)
    return {
        "query": task,
        "total_found": len(results),
        "skills": [
            {
                "name": s["name"],
                "slug": s["slug"],
                "description": s["description"],
                "path": s["path"],
                "preview": s.get("body_preview", "")[:200],
            }
            for s in results
        ],
    }


@router.get("/apply/{skill_slug}", summary="Get full content of a specific skill", response_class=PlainTextResponse)
def apply_skill(skill_slug: str):
    """Return the full SKILL.md content for a given skill slug (folder name).

    Example: GET /mcp/apply/fastapi-pro
    """
    skill_path = SKILLS_DIR / skill_slug / "SKILL.md"
    if not skill_path.exists():
        # Try case-insensitive search
        matches = [d for d in SKILLS_DIR.iterdir() if d.is_dir() and d.name.lower() == skill_slug.lower()]
        if matches:
            skill_path = matches[0] / "SKILL.md"
        if not skill_path.exists():
            raise HTTPException(404, f"Skill '{skill_slug}' not found in index")
    return skill_path.read_text(encoding="utf-8", errors="replace")


@router.post("/reindex", summary="Re-scan the skills directory and rebuild the index")
def reindex_skills():
    """Trigger a full re-scan of the skills/ directory.

    Use this after adding new skills to refresh the search index.
    """
    skills = build_index()
    save_index(skills)
    return {"status": "ok", "indexed": len(skills), "message": "Skills index rebuilt successfully"}
