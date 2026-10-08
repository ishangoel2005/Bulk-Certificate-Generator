import os
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Job, Certificate
from app.services.certificate_generator import generate_certificate


GENERATED_DIRECTORY = "generated_certificates"


def process_job(job_id: int, db: Session):
    """
    Process all certificates belonging to one job.

    Each certificate is handled independently so that
    one failure does not stop the remaining certificates.
    """

    job = db.query(Job).filter(Job.id == job_id).first()

    if job is None:
        return

    try:
        job.status = "PROCESSING"
        db.commit()

        certificates = (
            db.query(Certificate)
            .filter(Certificate.job_id == job_id)
            .all()
        )

        for certificate in certificates:

            try:
                certificate.status = "PROCESSING"
                db.commit()

                filename = (
                    f"certificate_{job.id}_{certificate.id}.pdf"
                )

                output_path = os.path.join(
                    GENERATED_DIRECTORY,
                    filename
                )

                generate_certificate(
                    recipient_name=certificate.recipient_name,
                    event_name=job.event_name,
                    event_date=job.event_date,
                    output_path=output_path
                )

                certificate.status = "SUCCESS"
                certificate.file_path = output_path
                certificate.error_message = None

                job.successful += 1

                db.commit()

            except Exception as exc:

                certificate.status = "FAILED"
                certificate.error_message = str(exc)

                job.failed += 1

                db.commit()

        if job.failed == 0:
            job.status = "COMPLETED"
        else:
            job.status = "COMPLETED_WITH_ERRORS"

        job.completed_at = datetime.utcnow()

        db.commit()

    except Exception as exc:

        job.status = "FAILED"
        job.completed_at = datetime.utcnow()

        db.commit()