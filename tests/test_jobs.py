def test_create_job(client):

    response = client.post(
        "/jobs",
        json={
            "event_name": "Python Workshop",
            "event_date": "2026-10-08",
            "recipients": [
                {
                    "name": "Ishan Goel",
                    "email": "ishan@example.com"
                },
                {
                    "name": "Rahul Sharma",
                    "email": "rahul@example.com"
                }
            ]
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert "job_id" in data
    assert data["status"] == "COMPLETED"
    assert data["total"] == 2

def test_job_status(client):

    create_response = client.post(
        "/jobs",
        json={
            "event_name": "Python Workshop",
            "event_date": "2026-10-08",
            "recipients": [
                {
                    "name": "Ishan Goel",
                    "email": "ishan@example.com"
                }
            ]
        }
    )

    job_id = create_response.json()["job_id"]

    response = client.get(
        f"/jobs/{job_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["job_id"] == job_id
    assert data["total"] == 1
    assert data["successful"] == 1
    assert data["failed"] == 0
    assert data["progress"] == 100.0
    assert data["status"] == "COMPLETED"

def test_certificate_retrieval(client):

    response = client.post(
        "/jobs",
        json={
            "event_name": "Python Workshop",
            "event_date": "2026-10-08",
            "recipients": [
                {
                    "name": "Ishan Goel",
                    "email": "ishan@example.com"
                }
            ]
        }
    )

    assert response.status_code == 201

    job_id = response.json()["job_id"]

    status_response = client.get(
        f"/jobs/{job_id}"
    )

    data = status_response.json()

    certificate_id = data["certificates"][0]["id"]

    certificate_response = client.get(
        f"/certificates/{certificate_id}"
    )

    assert certificate_response.status_code == 200

    assert certificate_response.headers[
        "content-type"
    ].startswith("application/pdf")

    assert certificate_response.content[:4] == b"%PDF"