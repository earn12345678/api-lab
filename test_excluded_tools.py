import pytest


# With 0, 1 or 2 tools excluded, the recommended pizza uses an allowed tool.
@pytest.mark.parametrize(
    "blocked",
    [[], ["Pizza cutter"], ["Scissors"], ["Knife", "Pizza cutter"]],
    ids=["none", "one-cutter", "one-scissors", "two-tools"],
)
def test_exclusion_list_is_respected(api, auth, blocked):
    result = api.post("/api/pizza", headers=auth, json={"excludedTools": blocked})
    assert result.status_code == 200
    assert result.json()["pizza"]["tool"] not in blocked


# Documented issue: excluding all three tools gives HTTP 500 instead of 400.
@pytest.mark.xfail(
    strict=True,
    reason="Defect 1: API crashes when every cutting tool is excluded",
)
def test_all_cutters_excluded_has_a_clear_error(api, auth):
    result = api.post(
        "/api/pizza",
        headers=auth,
        json={"excludedTools": ["Knife", "Pizza cutter", "Scissors"]},
    )
    assert result.status_code == 400
    assert result.json().get("error")
