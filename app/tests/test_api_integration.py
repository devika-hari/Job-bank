# =============================================================================
# Integration tests — exercise real HTTP endpoints through FastAPI TestClient.
# =============================================================================



def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_job_crud_flow(client):
    # Create
    create_resp = client.post(
        "/api/jobs",
        json={
            "role": "Analytics Engineer",
            "company_name": "Snow Co",
            "application_status": "Applied",
            "recruiter_name": "Alex Recruiter",
            "recruiter_email": "alex@example.com",
        },
    )
    assert create_resp.status_code == 201
    job_id = create_resp.json()["id"]

    # Read
    get_resp = client.get(f"/api/jobs/{job_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["company_name"] == "Snow Co"

    # Update
    update_resp = client.put(
        f"/api/jobs/{job_id}",
        json={"application_status": "Rejected", "rejection_reason": "Went with internal hire"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["rejection_reason"] == "Went with internal hire"

    # Search by company
    search_resp = client.get("/api/search/jobs/by-company", params={"company": "Snow"})
    assert search_resp.status_code == 200
    assert search_resp.json()["total"] >= 1

    # Delete
    delete_resp = client.delete(f"/api/jobs/{job_id}")
    assert delete_resp.status_code == 204

    # Confirm gone
    missing_resp = client.get(f"/api/jobs/{job_id}")
    assert missing_resp.status_code == 404


def test_interview_and_question_with_tags(client):
    job_resp = client.post(
        "/api/jobs",
        json={"role": "DE", "company_name": "Data Inc", "application_status": "In Progress"},
    )
    job_id = job_resp.json()["id"]

    interview_resp = client.post(
        f"/api/jobs/{job_id}/interviews",
        json={"round_number": 1, "round_status": "Completed", "interviewer_names": "Sam"},
    )
    assert interview_resp.status_code == 201
    interview_id = interview_resp.json()["id"]

    question_resp = client.post(
        f"/api/interviews/{interview_id}/questions",
        json={
            "question_text": "Explain CTE vs subquery",
            "notes": "Mention readability",
            "tags": ["SQL", "Python"],
        },
    )
    assert question_resp.status_code == 201

    search_resp = client.get(
        "/api/search/questions/by-tags",
        params={"tags_csv": "SQL,Python"},
    )
    assert search_resp.status_code == 200
    assert search_resp.json()["total"] >= 1


def test_search_jobs_by_company_and_role(client):
    client.post(
        "/api/jobs",
        json={"role": "Data Engineer", "company_name": "FindMe Ltd", "application_status": "Applied"},
    )
    client.post(
        "/api/jobs",
        json={"role": "Analyst", "company_name": "Other Co", "application_status": "Applied"},
    )

    by_company = client.get("/api/search/jobs", params={"company": "FindMe"})
    assert by_company.status_code == 200
    assert by_company.json()["total"] == 1
    assert by_company.json()["items"][0]["company_name"] == "FindMe Ltd"

    by_role = client.get("/api/search/jobs", params={"role": "Analyst"})
    assert by_role.status_code == 200
    assert by_role.json()["total"] == 1

    combined = client.get("/api/search/jobs", params={"company": "FindMe", "role": "Data"})
    assert combined.status_code == 200
    assert combined.json()["total"] == 1


def test_recruiter_search(client):
    client.post(
        "/api/jobs",
        json={
            "role": "AE",
            "company_name": "Acme",
            "recruiter_name": "Jordan",
            "recruiter_email": "jordan@acme.com",
        },
    )
    resp = client.get("/api/search/recruiters/by-company", params={"company": "Acme"})
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1
    assert resp.json()["items"][0]["recruiter_name"] == "Jordan"
