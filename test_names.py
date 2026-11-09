import requests

from conftest import API_URL


# The name list should be available and contain Margherita.
def test_pizza_names_are_available():
    response = requests.get(f"{API_URL}/api/names", timeout=20)
    assert response.status_code == 200
    names = response.json()["names"]
    assert isinstance(names, list)
    assert "Margherita" in names
