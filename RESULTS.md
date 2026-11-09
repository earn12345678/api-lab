# API Lab Results

ITCS386 - Week 11 API Testing  
Observed on: 09 November 2026, 04:30 UTC

## Part 0

- Step 0.1 - Pizza names: **18** (HTTP 200).
- Step 0.3 - `/api/tools` without a token: **HTTP 401**, `authentication failed`.
- Step 0.4 - Vegetarian pizza: **The Mammoth Funghi** (HTTP 200).
- Step 0.12 - I did not do the no-session experiment because it was optional.
- Step 0.16 - Number of excluded tools: **0, 1, 2, and 3**. The last block is the one no pizza can satisfy.

## Defect report

- **Title:** Excluding every cutting tool makes the API return a server error.
- **Request:** `POST /api/pizza` with a token from a new test account and JSON `{"excludedTools": ["Knife", "Pizza cutter", "Scissors"]}`.
- **Expected:** HTTP 400 and a JSON error explaining that there is no possible pizza.
- **Actual:** **HTTP 500**, empty body.
- **Severity:** Medium. The request is impossible, but the API treats it as a server error and gives no helpful message.

The strict `xfail` in `test_excluded_tools.py` keeps this issue visible until the server is fixed.

## Part A

**Step A2 - Invalid values for creating a rating**

| Input | HTTP status | Error from the server |
|---|---:|---|
| 3.5 stars | 400 | `json: cannot unmarshal number 3.5 into Go struct field Rating.stars of type int` |
| "3" as text | 400 | `json: cannot unmarshal string into Go struct field Rating.stars of type int` |
| missing stars | 400 | `number of stars must be between 1 and 5 (inclusive)` |
| nonexistent pizza | 400 | `pizza ID 999999999 not found` |

**Step A4 - Trying to use another person's rating**

I made a rating as one account and sent these requests with a different account:

| Other user's request | HTTP status | Response error | Owner still has the 3-star rating? |
|---|---:|---|---|
| GET | 404 | `not found` | Yes |
| PUT | 400 | `rating ID 18604 not found` | Yes |
| DELETE | 400 | `rating ID 18604 not found` | Yes |

The original rating was cleaned up with HTTP 204.

## Part B - Reflection

**1.** A real API test can find incorrect response codes, JSON problems, or a problem between the web server and its stored data. Tests with stubs don't go through those real connections. Unit tests still matter because they're faster and make it easier to check one function at a time.

**2.** Each test makes a fresh username, so I don't accidentally use another student's data. I also only write ratings with my own login token. I would follow the same idea in Project 2, using separate test orders or bookings and cleaning up my own records.

**3.** I used one `requests.Session` to keep the cookie from the server. QuickPizza has more than one backend, so without that cookie the login request might go to a server that doesn't know the account I just registered. I skipped the optional no-session runs.

**4.** The **3 excluded tools** block showed the problem. A 500 with no message is not useful to an application because it doesn't tell the customer how to fix their request. A 400 with a JSON message would be better. I kept it as strict `xfail` to check for a fix later.

**5.** The characteristics have 3, 4, 2 and 3 blocks. Base choice coverage needs **9 tests**: `1 + 2 + 3 + 1 + 2 = 9`. Every combination would need **72**: `3 × 4 × 2 × 3 = 72`.

**6.** The other account got **404 for GET, 400 for PUT and 400 for DELETE**. I expected all of them to be blocked, usually with 403 or 404. They were all rejected and the owner's 3-star rating stayed the same. The 400 responses could be clearer, but I don't have evidence of an access-control failure here.

**7.** With the made-up 16-character token I got **HTTP 200**, and the response contained 50 ratings. That looks like an authentication problem: a random token should not be enough to read ratings. On a real service, this could leak customer data. I tested GET only, so I can't say if writes are possible.

**8.** API tests are good for checking exact HTTP statuses and JSON fields. A browser test can check something different, like whether the page displays the data properly and whether the buttons actually work for the user.

## Full pytest run

```bash
python -m pytest -v --html=report.html --self-contained-html
```

Result from saved terminal output: **32 passed, 1 xfailed, 1 warning in 64.36s.**

The HTML report is `report.html` and was generated after the full test run completed.