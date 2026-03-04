"""Test Apify integration — mock HTTP responses, verify normalization."""

from unittest.mock import MagicMock, patch

import pytest

from app.services.apify import normalize_place, start_google_maps_run


MOCK_APIFY_RUN_RESPONSE = {
    "data": {
        "id": "run123",
        "status": "RUNNING",
        "defaultDatasetId": "dataset456",
    }
}

MOCK_PLACE_ITEM = {
    "title": "Plomberie Express Laval",
    "phone": "+15141234567",
    "website": "https://plomberie-laval.ca",
    "url": "https://maps.google.com/?cid=12345",
    "address": "123 Boul des Laurentides, Laval, QC",
    "city": "Laval",
    "countryCode": "CA",
    "location": {"lat": 45.55, "lng": -73.75},
    "categories": ["Plumber", "Emergency Plumbing"],
    "totalScore": 4.5,
}


def test_normalize_place():
    result = normalize_place(MOCK_PLACE_ITEM)
    assert result["company_name"] == "Plomberie Express Laval"
    assert result["phone"] == "+15141234567"
    assert result["website"] == "https://plomberie-laval.ca"
    assert result["google_maps_url"] == "https://maps.google.com/?cid=12345"
    assert result["city"] == "Laval"
    assert result["country"] == "CA"
    assert result["lat"] == 45.55
    assert result["lng"] == -73.75
    assert result["industry"] == "Plumber"
    assert "Plumber" in result["tags"]
    assert "Emergency Plumbing" in result["tags"]


def test_normalize_place_missing_fields():
    result = normalize_place({"title": "No Info Biz"})
    assert result["company_name"] == "No Info Biz"
    assert result["phone"] is None
    assert result["website"] is None
    assert result["industry"] is None
    assert result["tags"] == []


@patch("app.services.apify.httpx.post")
def test_start_google_maps_run(mock_post):
    mock_resp = MagicMock()
    mock_resp.json.return_value = MOCK_APIFY_RUN_RESPONSE
    mock_resp.raise_for_status = MagicMock()
    mock_post.return_value = mock_resp

    result = start_google_maps_run("plumber", "Laval, QC", max_items=10)
    assert result["id"] == "run123"
    assert result["defaultDatasetId"] == "dataset456"
    mock_post.assert_called_once()
