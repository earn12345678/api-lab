import requests

from conftest import API_URL


# The practice token lets us read the three possible cutting tools.
def test_available_cutters():
    response = requests.get(
        f"{API_URL}/api/tools",
        headers={"Authorization": "token abcdef0123456789"},
        timeout=20,
    )
    assert response.status_code == 200
    assert response.json()["tools"] == ["Knife", "Pizza cutter", "Scissors"]
