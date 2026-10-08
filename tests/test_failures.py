def test_one_certificate_failure_does_not_stop_other_certificates(client, monkeypatch):

    from app.services import job_processor

    original_generator = job_processor.generate_certificate

    def fake_generator(
        recipient_name,
        event_name,
        event_date,
        output_path
    ):

        if recipient_name == "Fail Person":
            raise Exception("Simulated certificate generation failure")

        return original_generator(
            recipient_name,
            event_name,
            event_date,
            output_path
        )

    monkeypatch.setattr(
        job_processor,
        "generate_certificate",
        fake_generator
    )

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
                    "name": "Fail Person",
                    "email": "fail@example.com"
                },
                {
                    "name": "Ananya Singh",
                    "email": "ananya@example.com"
                }
            ]
        }
    )

    assert response.status_code == 201

    job_id = response.json()["job_id"]

    status_response = client.get(
        f"/jobs/{job_id}"
    )

    assert status_response.status_code == 200

    data = status_response.json()

    assert data["total"] == 3
    assert data["successful"] == 2
    assert data["failed"] == 1
    assert data["progress"] == 100.0
    assert data["status"] == "COMPLETED_WITH_ERRORS"

    statuses = {
        certificate["recipient_name"]:
        certificate["status"]
        for certificate in data["certificates"]
    }

    assert statuses["Ishan Goel"] == "SUCCESS"
    assert statuses["Fail Person"] == "FAILED"
    assert statuses["Ananya Singh"] == "SUCCESS"