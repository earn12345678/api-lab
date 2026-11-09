import pytest


# Boundary check: 0 and 6 fail; 1 and 5 are valid and must be saved.
@pytest.mark.parametrize(
    "new_stars, expected_status",
    [(0, 400), (1, 200), (5, 200), (6, 400)],
    ids=["zero", "minimum", "maximum", "six"],
)
def test_update_star_boundaries(api, auth, rating, new_stars, expected_status):
    url = f"/api/ratings/{rating['id']}"
    response = api.put(url, headers=auth, json={"stars": new_stars})
    assert response.status_code == expected_status

    if expected_status == 200:
        assert response.json()["stars"] == new_stars
        expected_saved_value = new_stars
    else:
        assert response.json()["error"] == "number of stars must be between 1 and 5 (inclusive)"
        expected_saved_value = 3

    check = api.get(url, headers=auth)
    assert check.status_code == 200
    assert check.json()["stars"] == expected_saved_value
