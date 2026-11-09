"""Shared fixtures for the QuickPizza exercises."""

import uuid

import pytest
import requests

API_URL = "https://quickpizza.grafana.com"


class PizzaSession(requests.Session):
    """Allow tests to call /api/... while keeping the load balancer cookies."""

    def request(self, method, url, **kwargs):
        kwargs.setdefault("timeout", 20)
        return super().request(method, API_URL + url, **kwargs)


@pytest.fixture(scope="session")
def api():
    with PizzaSession() as client:
        yield client


def create_account(api):
    """Register a different made-up account and return its Authorization header."""
    details = {
        "username": f"lab-{uuid.uuid4().hex[:12]}",
        "password": "Pizza-2026",
    }
    created = api.post("/api/users", json=details)
    assert created.status_code == 201, created.text

    logged_in = api.post("/api/users/token/login", json=details)
    assert logged_in.status_code == 200, logged_in.text
    token = logged_in.json()["token"]
    return {"Authorization": f"token {token}"}


@pytest.fixture
def auth(api):
    return create_account(api)


@pytest.fixture
def other_auth(api):
    return create_account(api)


@pytest.fixture
def pizza_id(api, auth):
    response = api.post("/api/pizza", headers=auth, json={})
    assert response.status_code == 200, response.text
    return response.json()["pizza"]["id"]


@pytest.fixture
def rating(api, auth, pizza_id):
    """Provide a 3-star rating and clean it up unless a test already deleted it."""
    response = api.post(
        "/api/ratings", headers=auth, json={"pizza_id": pizza_id, "stars": 3}
    )
    assert response.status_code == 201, response.text
    saved_rating = response.json()
    try:
        yield saved_rating
    finally:
        # A DELETE test will already have removed its own rating.
        api.delete(f"/api/ratings/{saved_rating['id']}", headers=auth)
