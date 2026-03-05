"""Tests for the MCP Skills API endpoints."""

import pytest


class TestMCPSkillsEndpoints:
    def test_list_skills_returns_ok(self, client):
        """GET /mcp/skills should return 200 with a total count and skills list."""
        resp = client.get("/mcp/skills")
        assert resp.status_code == 200
        data = resp.json()
        assert "total" in data
        assert "skills" in data
        assert isinstance(data["skills"], list)

    def test_list_skills_structure(self, client):
        """Each skill entry should have name, slug, description, and path."""
        resp = client.get("/mcp/skills")
        skills = resp.json()["skills"]
        if skills:  # Only validate if skills directory is present
            first = skills[0]
            assert "name" in first
            assert "slug" in first
            assert "description" in first
            assert "path" in first

    def test_find_skills_returns_results(self, client):
        """GET /mcp/find?task=... should return relevant skills."""
        resp = client.get("/mcp/find", params={"task": "build a fastapi api", "top": 3})
        assert resp.status_code == 200
        data = resp.json()
        assert "query" in data
        assert "total_found" in data
        assert "skills" in data
        assert isinstance(data["skills"], list)
        assert len(data["skills"]) <= 3

    def test_find_skills_empty_query(self, client):
        """Empty task query should return 400."""
        resp = client.get("/mcp/find", params={"task": "   "})
        assert resp.status_code == 400

    def test_find_skills_missing_task(self, client):
        """Missing task param should return 422."""
        resp = client.get("/mcp/find")
        assert resp.status_code == 422

    def test_apply_skill_not_found(self, client):
        """GET /mcp/apply/<nonexistent> should return 404."""
        resp = client.get("/mcp/apply/this-skill-does-not-exist-xyz")
        assert resp.status_code == 404

    def test_reindex_endpoint(self, client):
        """POST /mcp/reindex should succeed and return indexed count."""
        resp = client.post("/mcp/reindex")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "indexed" in data

    def test_find_skills_top_limit(self, client):
        """top param should be capped at 20 by validation."""
        resp = client.get("/mcp/find", params={"task": "python", "top": 21})
        assert resp.status_code == 422  # FastAPI validation error

    def test_find_skills_roundtrip(self, client):
        """Results from find should be apply-able (path field is valid)."""
        resp = client.get("/mcp/find", params={"task": "docker deployment", "top": 1})
        results = resp.json()["skills"]
        if results:
            slug = results[0]["slug"]
            path = results[0]["path"]
            assert slug  # non-empty slug
            assert "SKILL.md" in path
