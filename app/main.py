from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Certificate, Job
from app.schemas import JobCreate, JobResponse, CertificateSummary
from app.services.job_processor import process_job


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bulk Certificate Generator",
    description="Backend API for bulk certificate generation",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Bulk Certificate Generator API is running"
    }


@app.post("/jobs", status_code=201)
def create_job(
    request: JobCreate,
    db: Session = Depends(get_db)
):
    job = Job(
        event_name=request.event_name,
        event_date=request.event_date,
        status="PENDING",
        total=len(request.recipients),
        successful=0,
        failed=0
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    for recipient in request.recipients:

        certificate = Certificate(
            job_id=job.id,
            recipient_name=recipient.name,
            recipient_email=str(recipient.email),
            status="PENDING"
        )

        db.add(certificate)

    db.commit()

    # Process the job immediately.
    # Each certificate is still handled independently
    # inside process_job().
    process_job(job.id, db)

    return {
        "job_id": job.id,
        "status": job.status,
        "total": job.total
    }


@app.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    certificates = (
        db.query(Certificate)
        .filter(Certificate.job_id == job_id)
        .all()
    )

    completed_count = job.successful + job.failed

    if job.total == 0:
        progress = 0.0
    else:
        progress = round(
            (completed_count / job.total) * 100,
            2
        )

    certificate_data = []

    for certificate in certificates:

        certificate_data.append(
            CertificateSummary(
                id=certificate.id,
                recipient_name=certificate.recipient_name,
                recipient_email=certificate.recipient_email,
                status=certificate.status,
                error_message=certificate.error_message
            )
        )

    return JobResponse(
        job_id=job.id,
        status=job.status,
        total=job.total,
        successful=job.successful,
        failed=job.failed,
        progress=progress,
        certificates=certificate_data
    )


@app.get("/certificates/{certificate_id}")
def get_certificate(
    certificate_id: int,
    db: Session = Depends(get_db)
):
    certificate = (
        db.query(Certificate)
        .filter(Certificate.id == certificate_id)
        .first()
    )

    if certificate is None:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found"
        )

    if certificate.status != "SUCCESS":
        raise HTTPException(
            status_code=409,
            detail="Certificate has not been successfully generated"
        )

    if not certificate.file_path:
        raise HTTPException(
            status_code=404,
            detail="Certificate file not found"
        )

    return FileResponse(
        path=certificate.file_path,
        media_type="application/pdf",
        filename=f"certificate_{certificate.id}.pdf"
    )