SUBMITTER = {"X-User-Id": "1"}
REVIEWER = {"X-User-Id": "2"}
OTHER_SUBMITTER = {"X-User-Id": "3"}


def test_submitter_creates_pending_submission(client):
    response = client.post(
        "/api/submissions",
        json={"title": "Q3 report", "body": "Numbers"},
        headers=SUBMITTER,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "pending"
    assert body["submitter_id"] == 1
    assert body["reviewer_note"] is None


def test_blank_title_is_rejected(client):
    response = client.post(
        "/api/submissions",
        json={"title": "   ", "body": "Numbers"},
        headers=SUBMITTER,
    )

    assert response.status_code == 422


def test_reviewer_cannot_create_submission(client):
    response = client.post(
        "/api/submissions",
        json={"title": "Nope", "body": "Not allowed"},
        headers=REVIEWER,
    )

    assert response.status_code == 403


def test_submitter_lists_only_own_submissions(client):
    client.post(
        "/api/submissions",
        json={"title": "Mine", "body": "A"},
        headers=SUBMITTER,
    )
    client.post(
        "/api/submissions",
        json={"title": "Theirs", "body": "B"},
        headers=OTHER_SUBMITTER,
    )

    response = client.get("/api/submissions", headers=SUBMITTER)

    assert response.status_code == 200
    assert [item["title"] for item in response.json()] == ["Mine"]


def test_reviewer_lists_pending_submissions(client):
    client.post(
        "/api/submissions",
        json={"title": "Mine", "body": "A"},
        headers=SUBMITTER,
    )
    client.post(
        "/api/submissions",
        json={"title": "Theirs", "body": "B"},
        headers=OTHER_SUBMITTER,
    )

    response = client.get("/api/submissions?status=pending", headers=REVIEWER)

    assert response.status_code == 200
    assert {item["title"] for item in response.json()} == {"Mine", "Theirs"}


def test_reviewer_approves_and_submitter_sees_new_status(client):
    created = client.post(
        "/api/submissions",
        json={"title": "Q3 report", "body": "Numbers"},
        headers=SUBMITTER,
    )
    submission_id = created.json()["id"]

    approved = client.patch(
        f"/api/submissions/{submission_id}",
        json={"status": "approved", "note": " looks good "},
        headers=REVIEWER,
    )

    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"
    assert approved.json()["reviewer_note"] == "looks good"

    listed = client.get("/api/submissions", headers=SUBMITTER)
    assert listed.json()[0]["status"] == "approved"


def test_deciding_again_conflicts(client):
    created = client.post(
        "/api/submissions",
        json={"title": "Q3 report", "body": "Numbers"},
        headers=SUBMITTER,
    )
    submission_id = created.json()["id"]
    client.patch(
        f"/api/submissions/{submission_id}",
        json={"status": "approved"},
        headers=REVIEWER,
    )

    again = client.patch(
        f"/api/submissions/{submission_id}",
        json={"status": "rejected"},
        headers=REVIEWER,
    )

    assert again.status_code == 409


def test_submitter_cannot_decide(client):
    created = client.post(
        "/api/submissions",
        json={"title": "Q3 report", "body": "Numbers"},
        headers=SUBMITTER,
    )

    response = client.patch(
        f"/api/submissions/{created.json()['id']}",
        json={"status": "rejected"},
        headers=SUBMITTER,
    )

    assert response.status_code == 403


def test_missing_submission_returns_not_found(client):
    response = client.patch(
        "/api/submissions/999",
        json={"status": "approved"},
        headers=REVIEWER,
    )

    assert response.status_code == 404


def test_unknown_user_is_unauthorized(client):
    response = client.get("/api/submissions", headers={"X-User-Id": "99"})

    assert response.status_code == 401
