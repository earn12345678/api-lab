# A new account must not see ratings left by another account.
def test_new_account_has_empty_ratings(api, auth):
    response = api.get("/api/ratings", headers=auth)
    assert response.status_code == 200
    assert response.json().get("ratings") == []
