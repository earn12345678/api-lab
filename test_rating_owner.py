# Another logged-in user must not be able to view the owner's rating.
def test_second_user_cannot_view_rating(api, auth, other_auth, rating):
    path = f"/api/ratings/{rating['id']}"
    forbidden = api.get(path, headers=other_auth)
    assert 400 <= forbidden.status_code < 500
    saved = api.get(path, headers=auth)
    assert saved.status_code == 200
    assert saved.json()["stars"] == rating["stars"]


# Another logged-in user must not be able to change the owner's rating.
def test_second_user_cannot_edit_rating(api, auth, other_auth, rating):
    path = f"/api/ratings/{rating['id']}"
    forbidden = api.put(path, headers=other_auth, json={"stars": 1})
    assert 400 <= forbidden.status_code < 500
    saved = api.get(path, headers=auth)
    assert saved.status_code == 200
    assert saved.json()["stars"] == rating["stars"]


# Another logged-in user must not be able to delete the owner's rating.
def test_second_user_cannot_remove_rating(api, auth, other_auth, rating):
    path = f"/api/ratings/{rating['id']}"
    forbidden = api.delete(path, headers=other_auth)
    assert 400 <= forbidden.status_code < 500
    saved = api.get(path, headers=auth)
    assert saved.status_code == 200
    assert saved.json()["stars"] == rating["stars"]
