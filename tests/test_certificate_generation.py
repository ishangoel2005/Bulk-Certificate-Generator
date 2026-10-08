def test_certificate_generation(tmp_path):

    from app.services.certificate_generator import generate_certificate

    output_file = tmp_path / "certificate.pdf"

    result = generate_certificate(
        recipient_name="Ishan Goel",
        event_name="Python Workshop",
        event_date="2026-10-08",
        output_path=str(output_file)
    )

    assert result == str(output_file)
    assert output_file.exists()
    assert output_file.stat().st_size > 0