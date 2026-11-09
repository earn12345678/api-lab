import pytest


RANGE_MESSAGE = "number of stars must be between 1 and 5 (inclusive)"


# Base choice: normal rating, integer 3, a real pizza, and an owner token.
def test_standard_rating_input(api, auth, pizza_id):
    response = api.post(
        "/api/ratings", headers=auth, json={"pizza_id": pizza_id, "stars": 3}
    )
    assert response.status_code == 201
    saved = response.json()
    try:
        assert saved["stars"] == 3
        assert saved["pizza_id"] == pizza_id
    finally:
        api.delete(f"/api/ratings/{saved['id']}", headers=auth)


# C1: both sides of the accepted 1-to-5 range must be refused.
@pytest.mark.parametrize("bad_stars", [0, 6], ids=["too-low", "too-high"])
def test_rating_outside_allowed_range(api, auth, pizza_id, bad_stars):
    response = api.post(
        "/api/ratings", headers=auth, json={"pizza_id": pizza_id, "stars": bad_stars}
    )
    assert response.status_code == 400
    assert response.json()["error"] == RANGE_MESSAGE


# C2: the integer field must not accept a decimal or a string, or be omitted.
@pytest.mark.parametrize(
    "stars, expected_error",
    [
        (3.5, "json: cannot unmarshal number 3.5 into Go struct field Rating.stars of type int"),
        ("3", "json: cannot unmarshal string into Go struct field Rating.stars of type int"),
        (None, RANGE_MESSAGE),
    ],
    ids=["decimal", "text", "missing"],
)
def test_invalid_stars_format(api, auth, pizza_id, stars, expected_error):
    payload = {"pizza_id": pizza_id}
    if stars is not None:
        payload["stars"] = stars
    response = api.post("/api/ratings", headers=auth, json=payload)
    assert response.status_code == 400
    assert response.json()["error"] == expected_error


# C3: a pizza ID that doesn't exist cannot receive a rating.
def test_pizza_id_not_found(api, auth):
    response = api.post(
        "/api/ratings", headers=auth, json={"pizza_id": 999999999, "stars": 3}
    )
    assert response.status_code == 400
    assert response.json()["error"] == "pizza ID 999999999 not found"


# C4: without a token, a client is not allowed to create ratings.
def test_rating_without_authorization(api, pizza_id):
    response = api.post("/api/ratings", json={"pizza_id": pizza_id, "stars": 3})
    assert response.status_code == 401
    assert response.json()["error"] == "authentication failed"


# C4: a token that is too short also fails authentication.
def test_rating_with_short_token(api, pizza_id):
    response = api.post(
        "/api/ratings",
        headers={"Authorization": "token short"},
        json={"pizza_id": pizza_id, "stars": 3},
    )
    assert response.status_code == 401
    assert response.json()["error"] == "authentication failed"
