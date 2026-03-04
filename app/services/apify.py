"""Apify Google Maps scraping client."""

from __future__ import annotations

import time

import httpx

from app.core.config import settings

APIFY_BASE = "https://api.apify.com/v2"
ACTOR_ID = "compass~crawler-google-places"


async def start_google_maps_run(
    query: str,
    location: str,
    max_items: int = 200,
    language: str = "fr",
) -> dict:
    """Start an Apify Google Places crawl and return the run metadata."""
    url = f"{APIFY_BASE}/acts/{ACTOR_ID}/runs"
    headers = {"Authorization": f"Bearer {settings.APIFY_TOKEN}"}
    payload = {
        "searchStringsArray": [f"{query} {location}"],
        "maxCrawledPlacesPerSearch": max_items,
        "language": language,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload, headers=headers, timeout=30.0)
    resp.raise_for_status()
    return resp.json().get("data", resp.json())


async def get_run_status(run_id: str) -> dict:
    """Get run status from Apify."""
    url = f"{APIFY_BASE}/actor-runs/{run_id}"
    headers = {"Authorization": f"Bearer {settings.APIFY_TOKEN}"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers, timeout=15.0)
    resp.raise_for_status()
    return resp.json().get("data", resp.json())


async def get_dataset_items(dataset_id: str, limit: int = 1000) -> list[dict]:
    """Fetch items from an Apify dataset."""
    url = f"{APIFY_BASE}/datasets/{dataset_id}/items"
    headers = {"Authorization": f"Bearer {settings.APIFY_TOKEN}"}
    params = {"limit": limit, "format": "json"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers, params=params, timeout=60.0)
    resp.raise_for_status()
    return resp.json()


import asyncio

async def poll_until_complete(run_id: str, timeout_seconds: int = 600, poll_interval: int = 10) -> dict:
    """Block until the run finishes or timeout. Return final run data."""
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        run_data = await get_run_status(run_id)
        status = run_data.get("status", "")
        if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            return run_data
        await asyncio.sleep(poll_interval)
    return {"status": "TIMED-OUT"}


def normalize_place(item: dict) -> dict:
    """Convert an Apify Google Places item to our Lead field dict."""
    # Extract first category as industry
    categories = item.get("categories", item.get("category", []))
    if isinstance(categories, str):
        categories = [categories]

    industry = categories[0] if categories else None
    tags = categories[:5] if categories else []

    return {
        "company_name": item.get("title") or item.get("name") or "Unknown",
        "phone": item.get("phone") or item.get("phoneUnformatted"),
        "website": item.get("website"),
        "google_maps_url": item.get("url"),
        "address": item.get("address") or item.get("street"),
        "city": item.get("city"),
        "country": item.get("countryCode") or item.get("country"),
        "lat": item.get("location", {}).get("lat") if isinstance(item.get("location"), dict) else item.get("lat"),
        "lng": item.get("location", {}).get("lng") if isinstance(item.get("location"), dict) else item.get("lng"),
        "industry": industry,
        "tags": tags,
    }
