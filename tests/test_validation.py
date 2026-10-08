def test_empty_recipients_are_rejected(client):

    response = client.post(
        "/jobs",
        json={
            "event_name": "Python Workshop",
            "event_date": "2026-10-08",
            "recipients": []
        }
    )

    assert response.status_code == 422


def test_invalid_email_is_rejected(client):

    response = client.post(
        "/jobs",
        json={
            "event_name": "Python Workshop",
            "event_date": "2026-10-08",
            "recipients": [
                {
                    "name": "Ishan Goel",
                    "email": "not-an-email"
                }
            ]
        }
    )

    assert response.status_code == 422


def test_empty_name_is_rejected(client):

    response = client.post(
        "/jobs",
        json={
            "event_name": "Python Workshop",
            "event_date": "2026-10-08",
            "recipients": [
                {
                    "name": "",
                    "email": "ishan@example.com"
                }
            ]
        }
    )

    assert response.status_code == 422