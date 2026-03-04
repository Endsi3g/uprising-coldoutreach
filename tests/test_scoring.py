"""Test ICP scoring engine."""

import pytest

from app.services.scoring import compute_heat_score, compute_icp_score


class TestICPScore:
    def test_high_value_plumber_laval(self):
        score = compute_icp_score(
            industry="Plumber",
            city="Laval",
            website="https://plomberie.ca",
            phone="+15141234567",
            email="info@plomberie.ca",
        )
        # 30 (industry) + 15 (city) + 10 (website) + 10 (phone) + 15 (email) = 80
        assert score == 80

    def test_unknown_industry_unknown_city(self):
        score = compute_icp_score(
            industry="Restaurant",
            city="Rimouski",
        )
        # 10 (categorised) + 5 (city) = 15
        assert score == 15

    def test_no_data(self):
        score = compute_icp_score()
        assert score == 0

    def test_max_score_capped(self):
        score = compute_icp_score(
            industry="General Contractor",
            city="Montreal",
            website="https://site.com",
            phone="+15141234567",
            email="a@b.com",
            google_rating=4.8,
            tags=["Contractor", "Renovation"],
        )
        assert score == 100

    def test_tags_bonus(self):
        base = compute_icp_score(industry="Other", city="Other")
        with_tags = compute_icp_score(industry="Other", city="Other", tags=["Plumber"])
        assert with_tags > base


class TestHeatScore:
    def test_no_engagement(self):
        assert compute_heat_score() == 0

    def test_opened(self):
        score = compute_heat_score(emails_opened=1)
        assert score == 15

    def test_clicked(self):
        score = compute_heat_score(emails_clicked=2)
        assert score == 30

    def test_replied(self):
        score = compute_heat_score(replies=1)
        assert score == 25

    def test_hot_stage_bonus(self):
        score = compute_heat_score(emails_opened=1, stage_name="Hot")
        assert score == 35  # 15 + 20

    def test_max_capped(self):
        score = compute_heat_score(
            emails_opened=10, emails_clicked=10, replies=10, stage_name="Booked"
        )
        assert score == 100
