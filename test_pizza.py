import requests

from conftest import API_URL


PUBLIC_HEADER = {"Authorization": "token abcdef0123456789"}


# A vegetarian order should not contain a meat ingredient.
def test_order_vegetarian_pizza():
    response = requests.post(
        f"{API_URL}/api/pizza",
        headers=PUBLIC_HEADER,
        json={"mustBeVegetarian": True},
        timeout=20,
    )
    assert response.status_code == 200
    pizza = response.json()["pizza"]
    assert pizza["name"]
    assert pizza["ingredients"]
    assert all(item["vegetarian"] for item in pizza["ingredients"])


# Recommendations require an Authorization header.
def test_order_without_login_token():
    response = requests.post(
        f"{API_URL}/api/pizza", json={"mustBeVegetarian": True}, timeout=20
    )
    assert response.status_code == 401
    assert response.json()["error"] == "authentication failed"
