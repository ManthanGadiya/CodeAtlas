"""Evaluation harness tests — Option A hardening (Evaluation_Framework §27-29, §71-72)."""

import pytest

from app.evaluation.baselines import baseline_random, baseline_static, compare_brier
from app.evaluation.metrics import brier_score, calibration_bins, ece, learning_gain


class TestBrier:
    def test_perfect_predictions_zero(self):
        assert brier_score([0.0, 1.0, 1.0, 0.0], [0, 1, 1, 0]) == 0.0

    def test_random_half_is_quarter(self):
        assert brier_score([0.5, 0.5, 0.5, 0.5], [0, 1, 0, 1]) == pytest.approx(0.25)

    def test_worst_is_one(self):
        assert brier_score([1.0, 0.0], [0, 1]) == 1.0

    def test_rejects_out_of_range(self):
        with pytest.raises(ValueError):
            brier_score([1.5], [1])
        with pytest.raises(ValueError):
            brier_score([0.5], [2])

    def test_rejects_mismatched_length(self):
        with pytest.raises(ValueError):
            brier_score([0.5, 0.5], [1])


class TestCalibration:
    def test_bins_cover_predictions(self):
        preds = [0.1, 0.2, 0.8, 0.9]
        outcomes = [0, 0, 1, 1]
        bins = calibration_bins(preds, outcomes, n_bins=2)
        assert len(bins) == 2
        assert bins[0]["count"] == 2
        assert bins[1]["count"] == 2

    def test_ece_perfect_is_zero(self):
        preds = [0.0, 0.0, 1.0, 1.0]
        outcomes = [0, 0, 1, 1]
        assert ece(preds, outcomes) == 0.0

    def test_ece_worst_nonzero(self):
        preds = [0.0, 0.0, 1.0, 1.0]
        outcomes = [1, 1, 0, 0]
        assert ece(preds, outcomes) > 0.5


class TestLearningGain:
    def test_gain_positive(self):
        g = learning_gain(0.3, 0.6)
        assert g["absolute"] == pytest.approx(0.3)
        assert g["normalized"] == pytest.approx(0.3 / 0.7, rel=1e-3)

    def test_gain_no_headroom(self):
        g = learning_gain(1.0, 1.0)
        assert g["normalized"] == 0.0


class TestBaselines:
    def test_random_in_range(self):
        preds = baseline_random(10, seed=1)
        assert len(preds) == 10
        assert all(0 <= p <= 1 for p in preds)

    def test_static_repeats(self):
        assert baseline_static(0.7, 3) == [0.7, 0.7, 0.7]

    def test_compare_brier_model_better(self):
        outcomes = [1, 0, 1, 0]
        model = [0.9, 0.1, 0.8, 0.2]
        baseline = [0.5, 0.5, 0.5, 0.5]
        comp = compare_brier(model, baseline, outcomes)
        assert comp["model_better"] is True
        assert comp["delta"] > 0


class TestEvaluationAPI:
    def test_health(self, client):
        resp = client.get("/api/evaluation/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_report_requires_auth(self, client):
        assert client.get("/api/evaluation/report").status_code == 401

    def test_report_empty_before_evidence(self, client):
        client.post(
            "/api/auth/register",
            json={"email": "eval1@example.com", "password": "strongPass123!"},
        )
        resp = client.get("/api/evaluation/report")
        assert resp.status_code == 200
        data = resp.json()
        assert data["n"] == 0
        assert data["brier"] is None

    def test_report_after_submits(self, client, db_session, runner_fake):
        from app.problems.seed import seed_problems

        seed_problems(db_session)
        client.post(
            "/api/auth/register",
            json={"email": "eval2@example.com", "password": "strongPass123!"},
        )
        # Submit a problem to create history
        client.post(
            "/api/problems/two-sum/submit",
            json={"code": "def two_sum(nums, target): return [0,1]"},
        )
        client.post(
            "/api/problems/two-sum/submit",
            json={"code": "def two_sum(nums, target): return []"},
        )
        resp = client.get("/api/evaluation/report")
        assert resp.status_code == 200
        data = resp.json()
        assert data["n"] >= 2
        assert 0 <= data["brier"] <= 1
        assert "calibration" in data
        assert "comparison" in data
