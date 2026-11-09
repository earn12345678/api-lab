# A successful POST must include the saved rating's id and values.
def test_add_five_star_rating(api, auth, pizza_id):
    payload = {"pizza_id": pizza_id, "stars": 5}
    response = api.post("/api/ratings", headers=auth, json=payload)
    assert response.status_code == 201
    saved = response.json()
    try:
        assert saved["stars"] == payload["stars"]
        assert saved["pizza_id"] == payload["pizza_id"]
        assert type(saved["id"]) is int
    finally:
        # Do not leave this new rating on the shared server.
        api.delete(f"/api/ratings/{saved['id']}", headers=auth)


# The owner should be able to read their stored rating again.
def test_get_saved_rating(api, auth, rating):
    response = api.get(f"/api/ratings/{rating['id']}", headers=auth)
    assert response.status_code == 200
    assert response.json() == rating


# Editing a rating from 3 stars to 4 stars should save the new value.
def test_change_saved_rating(api, auth, rating):
    response = api.put(
        f"/api/ratings/{rating['id']}", headers=auth, json={"stars": 4}
    )
    assert response.status_code == 200
    assert response.json()["stars"] == 4


# After deleting the owner's rating, another GET should return 404.
def test_remove_saved_rating(api, auth, rating):
    path = f"/api/ratings/{rating['id']}"
    deleted = api.delete(path, headers=auth)
    assert deleted.status_code == 204
    assert api.get(path, headers=auth).status_code == 404
