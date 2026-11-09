import uuid


def make_user():
    return {"username": f"lab-{uuid.uuid4().hex[:12]}", "password": "Pizza-2026"}


# Registering a name twice should not create two accounts.
def test_username_cannot_be_reused(api):
    person = make_user()
    assert api.post("/api/users", json=person).status_code == 201
    repeated = api.post("/api/users", json=person)
    assert repeated.status_code == 400
    assert repeated.json() == {"error": "username already taken"}


# An incorrect password should fail login.
def test_login_with_bad_password(api):
    person = make_user()
    assert api.post("/api/users", json=person).status_code == 201
    attempted = api.post(
        "/api/users/token/login",
        json={"username": person["username"], "password": "wrong-password"},
    )
    assert attempted.status_code == 401
    assert attempted.json()["error"] == "authentication failed"


# A blank username should be rejected before registration.
def test_user_needs_a_name(api):
    response = api.post(
        "/api/users", json={"username": "", "password": "Pizza-2026"}
    )
    assert response.status_code == 400
    assert response.json()["error"] == "username field is empty"
