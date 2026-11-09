"""Collect the observations requested by the lab without using anyone else's data.

Run this on your own machine after the full pytest command. It writes RESULTS.md
from real API responses; it does not make up a test summary or fake a pass.
"""

import datetime as dt
import re
import sys
import uuid
from pathlib import Path

import requests

BASE = "https://quickpizza.grafana.com"
TIMEOUT = 20
PUBLIC = {"Authorization": "token abcdef0123456789"}
FAKE = {"Authorization": "token 0000000000000000"}
TOOLS = ["Knife", "Pizza cutter", "Scissors"]
ROOT = Path(__file__).parent


def call(session, method, path, **kwargs):
    response = session.request(method, BASE + path, timeout=TIMEOUT, **kwargs)
    return response


def require_status(response, code, label):
    if response.status_code != code:
        raise RuntimeError(
            f"{label}: expected HTTP {code}, got {response.status_code}: {response.text[:300]}"
        )
    return response


def register(session):
    user = {
        "username": "lab-" + uuid.uuid4().hex[:12],
        "password": "Pizza-2026",
    }
    require_status(call(session, "POST", "/api/users", json=user), 201, "register")
    logged_in = require_status(
        call(session, "POST", "/api/users/token/login", json=user), 200, "login"
    )
    return {"Authorization": "token " + logged_in.json()["token"]}


def error_text(response):
    if response.status_code == 500 and not response.content:
        return "empty body"
    try:
        obj = response.json()
    except ValueError:
        return "non-JSON response: " + repr(response.text[:100])
    if "error" in obj:
        return str(obj["error"])
    return str(obj)[:200]


def test_summary():
    output = ROOT / "pytest_output.txt"
    if not output.exists():
        return "Not recorded here yet. Run pytest and save its terminal output first."
    text = output.read_text(encoding="utf-8-sig", errors="replace")
    matches = re.findall(r"(\d+) passed, (\d+) xfailed in ([0-9.]+)s", text)
    if matches:
        passed, xfailed, duration = matches[-1]
        return f"{passed} passed, {xfailed} xfailed in {duration}s"
    return "The saved pytest output does not contain a completed pass/xfail summary."


def make_report(observed):
    timestamp = observed["timestamp"]
    a4 = observed["permissions"]
    read, update, delete = (a4[key]["status"] for key in ("GET", "PUT", "DELETE"))
    owner_ok = all(entry["owner_unchanged"] for entry in a4.values())
    auth_status = observed["fake_token_status"]
    fake_body = observed["fake_token_description"]

    if all(400 <= x <= 499 for x in (read, update, delete)) and owner_ok:
        q6 = (
            f"The other account got **{read} for GET, {update} for PUT and {delete} for DELETE**. "
            "I expected all of them to be blocked, usually with 403 or 404. "
            "They were all rejected and the owner's 3-star rating stayed the same. "
            "The 400 responses could be clearer, but I don't have evidence of an access-control failure here."
        )
    else:
        q6 = (
            f"The other account got **{read}, {update}, {delete}** for GET, PUT and DELETE. "
            f"Owner unchanged after all three: **{owner_ok}**. "
            "This needs further investigation because a different user should not be able to use the owner's rating."
        )

    if auth_status == 200:
        q7 = (
            f"With the made-up 16-character token I got **HTTP 200**, and {fake_body}. "
            "That looks like an authentication problem: a random token should not be enough to read ratings. "
            "On a real service, this could leak customer data. I tested GET only, so I can't say if writes are possible."
        )
    else:
        q7 = (
            f"The made-up token returned **HTTP {auth_status}** ({fake_body}). "
            "I only made a read request, as requested. I would expect an invalid token to be rejected."
        )

    errors = observed["invalid_errors"]
    rows = "\n".join(
        f"| {name} | {response.status_code} | `{error_text(response)}` |"
        for name, response in errors.items()
    )
    owner_rows = "\n".join(
        f"| {method} | {info['status']} | `{info['error']}` | "
        f"{'Yes' if info['owner_unchanged'] else 'No'} |"
        for method, info in a4.items()
    )

    defect = observed["defect"]
    defect_text = "empty body" if not defect.content else repr(defect.text[:150])
    if defect.status_code == 500 and not defect.content:
        defect_severity = "Medium. The request is impossible, but the API treats it as a server error and gives no helpful message."
    else:
        defect_severity = "Medium (review this based on the actual behavior)."

    return f"""# API Lab Results

ITCS386 - Week 11 API Testing  
Observed on: {timestamp}

## Part 0

- Step 0.1 - Pizza names: **{observed['names_count']}** (HTTP {observed['names_status']}).
- Step 0.3 - `/api/tools` without a token: **HTTP {observed['tools_status']}**, `{observed['tools_error']}`.
- Step 0.4 - Vegetarian pizza: **{observed['vegetarian_name']}** (HTTP {observed['vegetarian_status']}).
- Step 0.12 - I did not do the no-session experiment because it was optional.
- Step 0.16 - Number of excluded tools: **0, 1, 2, and 3**. The last block is the one no pizza can satisfy.

## Defect report

- **Title:** Excluding every cutting tool makes the API return a server error.
- **Request:** `POST /api/pizza` with a token from a new test account and JSON `{{"excludedTools": ["Knife", "Pizza cutter", "Scissors"]}}`.
- **Expected:** HTTP 400 and a JSON error explaining that there is no possible pizza.
- **Actual:** **HTTP {defect.status_code}**, {defect_text}.
- **Severity:** {defect_severity}

The strict `xfail` in `test_excluded_tools.py` keeps this issue visible until the server is fixed.

## Part A

**Step A2 - Invalid values for creating a rating**

| Input | HTTP status | Error from the server |
|---|---:|---|
{rows}

**Step A4 - Trying to use another person's rating**

I made a rating as one account and sent these requests with a different account:

| Other user's request | HTTP status | Response error | Owner still has the 3-star rating? |
|---|---:|---|---|
{owner_rows}

The original rating was cleaned up with HTTP {observed['cleanup_status']}.

## Part B - Reflection

**1.** A real API test can find incorrect response codes, JSON problems, or a problem between the web server and its stored data. Tests with stubs don't go through those real connections. Unit tests still matter because they're faster and make it easier to check one function at a time.

**2.** Each test makes a fresh username, so I don't accidentally use another student's data. I also only write ratings with my own login token. I would follow the same idea in Project 2, using separate test orders or bookings and cleaning up my own records.

**3.** I used one `requests.Session` to keep the cookie from the server. QuickPizza has more than one backend, so without that cookie the login request might go to a server that doesn't know the account I just registered. I skipped the optional no-session runs.

**4.** The **3 excluded tools** block showed the problem. A 500 with no message is not useful to an application because it doesn't tell the customer how to fix their request. A 400 with a JSON message would be better. I kept it as strict `xfail` to check for a fix later.

**5.** The characteristics have 3, 4, 2 and 3 blocks. Base choice coverage needs **9 tests**: `1 + 2 + 3 + 1 + 2 = 9`. Every combination would need **72**: `3 × 4 × 2 × 3 = 72`.

**6.** {q6}

**7.** {q7}

**8.** API tests are good for checking exact HTTP statuses and JSON fields. A browser test can check something different, like whether the page displays the data properly and whether the buttons actually work for the user.

## Full pytest run

```powershell
python -m pytest -v --html=report.html --self-contained-html
```

Result from saved terminal output: **{observed['pytest_summary']}**.

The HTML report is `report.html` (only if the full test command has finished).
"""


def main():
    print("Checking QuickPizza. This uses new test accounts and only cleans up its own rating.")
    with requests.Session() as session:
        names = require_status(call(session, "GET", "/api/names"), 200, "names")
        tools = call(session, "GET", "/api/tools")
        veg = require_status(
            call(session, "POST", "/api/pizza", headers=PUBLIC, json={"mustBeVegetarian": True}),
            200,
            "vegetarian pizza",
        )

        # The only request sent with the fake token is a GET.
        fake = call(session, "GET", "/api/ratings", headers=FAKE)
        try:
            fake_data = fake.json()
            if isinstance(fake_data.get("ratings"), list):
                fake_info = f"the response contained {len(fake_data['ratings'])} ratings"
            else:
                fake_info = "the response was " + str(fake_data)[:120]
        except ValueError:
            fake_info = "the response body was " + repr(fake.text[:120])

        owner_auth = register(session)
        defect = call(
            session, "POST", "/api/pizza", headers=owner_auth,
            json={"excludedTools": TOOLS}
        )
        actual_pizza = require_status(
            call(session, "POST", "/api/pizza", headers=owner_auth, json={}),
            200, "pizza for ratings",
        ).json()["pizza"]["id"]

        invalid_inputs = {
            "3.5 stars": {"pizza_id": actual_pizza, "stars": 3.5},
            '"3" as text': {"pizza_id": actual_pizza, "stars": "3"},
            "missing stars": {"pizza_id": actual_pizza},
            "nonexistent pizza": {"pizza_id": 999999999, "stars": 3},
        }
        invalid_errors = {
            name: call(session, "POST", "/api/ratings", headers=owner_auth, json=body)
            for name, body in invalid_inputs.items()
        }

        made = require_status(
            call(session, "POST", "/api/ratings", headers=owner_auth,
                 json={"pizza_id": actual_pizza, "stars": 3}),
            201, "owner rating"
        ).json()
        path = f"/api/ratings/{made['id']}"

        permissions = {}
        cleanup_status = None
        try:
            other_auth = register(session)
            for method in ("GET", "PUT", "DELETE"):
                arguments = {"headers": other_auth}
                if method == "PUT":
                    arguments["json"] = {"stars": 1}
                response = call(session, method, path, **arguments)
                owner_check = call(session, "GET", path, headers=owner_auth)
                permissions[method] = {
                    "status": response.status_code,
                    "error": error_text(response),
                    "owner_unchanged": (
                        owner_check.status_code == 200
                        and owner_check.json().get("stars") == 3
                    ),
                }
        finally:
            # Always delete only the rating just created by this script.
            cleanup_status = call(session, "DELETE", path, headers=owner_auth).status_code

    observed = {
        "timestamp": dt.datetime.now(dt.timezone.utc).strftime("%d %B %Y, %H:%M UTC"),
        "names_count": len(names.json()["names"]),
        "names_status": names.status_code,
        "tools_status": tools.status_code,
        "tools_error": error_text(tools),
        "vegetarian_status": veg.status_code,
        "vegetarian_name": veg.json()["pizza"]["name"],
        "fake_token_status": fake.status_code,
        "fake_token_description": fake_info,
        "defect": defect,
        "invalid_errors": invalid_errors,
        "permissions": permissions,
        "cleanup_status": cleanup_status,
        "pytest_summary": test_summary(),
    }
    report = make_report(observed)
    target = ROOT / "RESULTS.md"
    target.write_text(report, encoding="utf-8")
    print("Saved", target)
    print("Names:", observed["names_count"])
    print("Vegetarian pizza:", observed["vegetarian_name"])
    print("Other-user GET/PUT/DELETE:", [permissions[k]["status"] for k in ("GET", "PUT", "DELETE")])
    print("Made-up token GET:", fake.status_code)
    print("Test summary:", observed["pytest_summary"])


if __name__ == "__main__":
    try:
        main()
    except (requests.RequestException, RuntimeError, KeyError, ValueError) as exc:
        print("Could not finish collecting results:", exc, file=sys.stderr)
        print("Existing RESULTS.md was not replaced; please check your connection and try the failed step later.", file=sys.stderr)
        sys.exit(1)
