# Bulk Certificate Generator

> A FastAPI-based backend application that generates PDF certificates in bulk from a single request.

## Overview

**Bulk Certificate Generator** is a backend API designed to generate certificates for multiple recipients from a single request.

The application accepts an event name, event date and a list of recipients. It validates the input, generates one certificate per recipient using a predefined template, tracks generation status, handles individual certificate failures without stopping the remaining certificates and provides an API to retrieve generated certificates.

## Key Features

* **Bulk Certificate Generation** - Generate certificates for multiple recipients using a single API request.
* **Input Validation** - Validates recipient names, email addresses, event name, event date and recipient limits.
* **PDF Certificate Generation** - Generates individual PDF certificates using ReportLab.
* **Job Tracking** - Tracks the overall status and progress of each generation job.
* **Individual Status Tracking** - Tracks the status of every generated certificate.
* **Failure Isolation** - A failed certificate does not stop the generation of other certificates.
* **Certificate Retrieval** - Allows successfully generated certificates to be downloaded through an API endpoint.
* **Automated Testing** - Includes tests for job creation, validation, certificate generation, progress tracking, failure handling and certificate retrieval.

## Tech Stack

### Backend

* Python
* FastAPI

### Database

* SQLite
* SQLAlchemy

### Validation

* Pydantic

### Certificate Generation

* ReportLab

### Testing

* Pytest
* HTTPX

## Project Structure

```text
bulk-certificate-generator/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   └── services/
│       ├── __init__.py
│       ├── certificate_generator.py
│       └── job_processor.py
│
├── generated_certificates/
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_jobs.py
│   ├── test_validation.py
│   ├── test_certificate_generation.py
│   └── test_failures.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

## Architecture

```text
                         Client
                           |
                           | POST /jobs
                           v
                  ┌──────────────────┐
                  │     FastAPI      │
                  └────────┬─────────┘
                           |
                           v
                  ┌──────────────────┐
                  │ Pydantic         │
                  │ Validation       │
                  └────────┬─────────┘
                           |
                           v
                  ┌──────────────────┐
                  │   Create Job     │
                  └────────┬─────────┘
                           |
                           v
                  ┌──────────────────┐
                  │ Create           │
                  │ Certificates     │
                  └────────┬─────────┘
                           |
                           v
                  ┌──────────────────┐
                  │ Process Each     │
                  │ Certificate      │
                  └────────┬─────────┘
                           |
              ┌────────────┴────────────┐
              |                         |
              v                         v
      ┌───────────────┐         ┌───────────────┐
      │ Generate PDF  │         │ Generation    │
      │               │         │ Failure       │
      └───────┬───────┘         └───────┬───────┘
              |                         |
              v                         v
         SUCCESS                      FAILED
              |                         |
              └────────────┬────────────┘
                           |
                           v
                  ┌──────────────────┐
                  │ Update Job       │
                  │ Status/Progress  │
                  └────────┬─────────┘
                           |
                           v
                  ┌──────────────────┐
                  │ GET /jobs/{id}   │
                  └────────┬─────────┘
                           |
                           v
                  ┌──────────────────┐
                  │ GET              │
                  │ /certificates/id │
                  └──────────────────┘
```

## How It Works

### 1. Submit a Generation Request

The client sends a single `POST /jobs` request containing:

* Event name
* Event date
* List of recipients
* Recipient name
* Recipient email

The request can contain multiple recipients, allowing certificates to be generated in bulk.

### 2. Validate the Request

FastAPI and Pydantic validate the incoming data before certificate processing begins.

The application checks:

* Recipient name
* Recipient email
* Recipient list
* Event name
* Event date
* Maximum recipient count

Invalid requests are rejected before processing.

### 3. Create the Job

A `Job` record is created in the database.

The job stores information such as:

* Job ID
* Event name
* Event date
* Job status
* Total number of certificates
* Successful certificate count
* Failed certificate count
* Creation time
* Completion time

### 4. Create Certificate Records

A separate `Certificate` record is created for every recipient.

For example:

```text
Job 1
│
├── Certificate 1 → Ishan Goel
├── Certificate 2 → Rahul Sharma
└── Certificate 3 → Ananya Singh
```

This allows each certificate to have its own status and error information.

### 5. Generate Certificates

The application processes each certificate independently.

The predefined ReportLab template dynamically inserts:

* Recipient name
* Event name
* Event date

Each certificate is saved as a PDF file.

### 6. Handle Individual Failures

If one certificate fails, the application:

* Marks that certificate as `FAILED`
* Stores the error message
* Increments the failed count
* Continues processing the remaining certificates

For example:

```text
Recipient A → SUCCESS
Recipient B → FAILED
Recipient C → SUCCESS
```

The final job status becomes:

```text
COMPLETED_WITH_ERRORS
```

### 7. Check Job Status

The client can use:

```text
GET /jobs/{job_id}
```

to check:

* Overall job status
* Total certificates
* Successful certificates
* Failed certificates
* Progress percentage
* Individual certificate statuses

### 8. Retrieve Certificates

Successfully generated certificates can be retrieved using:

```text
GET /certificates/{certificate_id}
```

The API returns the generated PDF file.

## Certificate Generation

The application uses a single predefined certificate template.

The following values are dynamically inserted into the certificate:

* Recipient name
* Event name
* Event date

The certificate is generated using ReportLab.

Example:

```text
CERTIFICATE OF COMPLETION

This is to certify that

Ishan Goel

has successfully completed Python Workshop

Date: 2026-10-08

Organizer
```

Generated certificates are stored in:

```text
generated_certificates/
```

Example:

```text
generated_certificates/
├── certificate_1_1.pdf
├── certificate_1_2.pdf
└── certificate_1_3.pdf
```

## Database Design

The application uses two main database tables.

### Job

The `Job` table represents one bulk generation request.

It stores:

* `id`
* `event_name`
* `event_date`
* `status`
* `total`
* `successful`
* `failed`
* `created_at`
* `completed_at`

### Certificate

The `Certificate` table represents one certificate belonging to a job.

It stores:

* `id`
* `job_id`
* `recipient_name`
* `recipient_email`
* `status`
* `file_path`
* `error_message`
* `created_at`

### Relationship

One job can contain many certificates.

```text
Job
 |
 +---- Certificate
 |
 +---- Certificate
 |
 +---- Certificate
 |
 +---- Certificate
```

This is a one-to-many relationship.

## Job Statuses

The application supports the following job statuses:

* `PENDING` - Job has been created but processing has not started.
* `PROCESSING` - Certificates are currently being generated.
* `COMPLETED` - All certificates were generated successfully.
* `COMPLETED_WITH_ERRORS` - Some certificates were generated successfully while others failed.
* `FAILED` - A complete job-level failure occurred.

## Certificate Statuses

Each certificate can have the following status:

* `PENDING` - Certificate has not been processed yet.
* `PROCESSING` - Certificate is currently being generated.
* `SUCCESS` - Certificate was generated successfully.
* `FAILED` - Certificate generation failed.

## Progress Tracking

The application calculates progress using the number of completed certificates.

```text
Progress =
(Successful Certificates + Failed Certificates)
----------------------------------------------- × 100
              Total Certificates
```

For example:

```text
Total = 10
Successful = 8
Failed = 2

Progress = (8 + 2) / 10 × 100
         = 100%
```

A failed certificate still counts as processed, so the job can reach 100% progress even when some certificates failed.

## Input Validation

### Recipient Name

The recipient name:

* Must be provided
* Must contain at least one character
* Cannot exceed 200 characters

### Recipient Email

The recipient email must be a valid email address.

### Recipient List

The recipient list:

* Must contain at least one recipient
* Can contain a maximum of 500 recipients

### Event Name

The event name:

* Must be provided
* Must contain at least one character
* Cannot exceed 200 characters

### Event Date

The event date must be provided.

Invalid requests are rejected with:

```text
422 Unprocessable Entity
```

## API Endpoints

### GET `/`

Returns a simple API health message.

Example response:

```json
{
  "message": "Bulk Certificate Generator API is running"
}
```

### POST `/jobs`

Creates a new bulk certificate generation job.

#### Request

```json
{
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
```

#### Response

```json
{
  "job_id": 1,
  "status": "COMPLETED",
  "total": 2
}
```

### GET `/jobs/{job_id}`

Returns the status and progress of a generation job.

#### Example

```text
GET /jobs/1
```

#### Response

```json
{
  "job_id": 1,
  "status": "COMPLETED",
  "total": 2,
  "successful": 2,
  "failed": 0,
  "progress": 100.0,
  "certificates": [
    {
      "id": 1,
      "recipient_name": "Ishan Goel",
      "recipient_email": "ishan@example.com",
      "status": "SUCCESS",
      "error_message": null
    },
    {
      "id": 2,
      "recipient_name": "Rahul Sharma",
      "recipient_email": "rahul@example.com",
      "status": "SUCCESS",
      "error_message": null
    }
  ]
}
```

### GET `/certificates/{certificate_id}`

Retrieves a successfully generated certificate.

#### Example

```text
GET /certificates/1
```

The API returns the generated PDF file.

## API Summary

| Method | Endpoint | Purpose |
| ------ | -------- | ------- |
| `GET` | `/` | API health check |
| `POST` | `/jobs` | Create a bulk certificate generation job |
| `GET` | `/jobs/{job_id}` | Check job status and progress |
| `GET` | `/certificates/{certificate_id}` | Retrieve a generated certificate |

## Setup

### Prerequisites

Make sure the following are installed:

* Python 3.10 or later
* pip

Check Python:

```bash
python --version
```

### Create Virtual Environment

```bash
python -m venv .venv
```

### Activate Virtual Environment

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Run the Application

Start the FastAPI application using:

```bash
uvicorn app.main:app --reload
```

The application will be available at:

```text
http://127.0.0.1:8000
```

## API Documentation

FastAPI automatically provides interactive Swagger documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

The `/docs` page can be used to:

* View available endpoints
* Submit generation requests
* Check job status
* Retrieve generated certificates
* Test the API directly from the browser

## Submit a Certificate Generation Request

### Using Swagger UI

Open:

```text
http://127.0.0.1:8000/docs
```

Select:

```text
POST /jobs
```

Click:

```text
Try it out
```

Enter:

```json
{
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
```

Click:

```text
Execute
```

The response will contain the generated `job_id`.

## Check Job Status

Use the returned `job_id`.

For example:

```text
GET /jobs/1
```

The response shows:

```text
Total Certificates
Successful Certificates
Failed Certificates
Progress
Individual Certificate Status
```

## Retrieve a Generated Certificate

First obtain the certificate ID from:

```text
GET /jobs/{job_id}
```

Then call:

```text
GET /certificates/{certificate_id}
```

If the certificate was generated successfully, the API returns the PDF.

## Run Tests

Run all tests using:

```bash
pytest
```

Expected result:

```text
8 passed
```

The test suite covers:

* Creating a generation job
* Input validation
* Certificate generation
* Job status and progress
* Individual certificate failure
* Retrieving generated certificates

### Run Job Tests

```bash
pytest tests/test_jobs.py
```

### Run Validation Tests

```bash
pytest tests/test_validation.py
```

### Run Certificate Generation Tests

```bash
pytest tests/test_certificate_generation.py
```

### Run Failure Handling Tests

```bash
pytest tests/test_failures.py
```

## Testing Strategy

### Job Creation Test

Verifies that:

* A generation request can be submitted
* A job ID is returned
* The correct number of recipients is recorded
* Certificates are generated successfully

### Input Validation Test

Verifies that invalid requests are rejected.

Examples include:

* Empty recipient list
* Invalid email address
* Empty recipient name

### Certificate Generation Test

Verifies that:

* A PDF file is created
* The file exists
* The generated file is not empty

### Job Status Test

Verifies that:

* Job status is returned
* Total certificate count is correct
* Successful count is correct
* Failed count is correct
* Progress reaches 100% after processing

### Individual Failure Test

Simulates one certificate generation failure and verifies that:

* The failed certificate is marked `FAILED`
* The error message is stored
* Other certificates still succeed
* The final job status becomes `COMPLETED_WITH_ERRORS`

### Certificate Retrieval Test

Verifies that:

* A successfully generated certificate can be retrieved
* The response is a PDF
* The returned content begins with the PDF signature

## Important Design Decisions

### FastAPI

FastAPI was selected because it provides:

* Simple REST API development
* Automatic request validation
* Automatic Swagger documentation
* Good performance
* Easy Python integration

### SQLite

SQLite was selected because:

* It is free and open source
* It requires no separate database server
* It is simple to configure
* It is sufficient for this assignment
* It keeps the project easy to run locally

For a larger production system, SQLite could be replaced with PostgreSQL.

### SQLAlchemy

SQLAlchemy is used as the ORM.

It allows the application to work with database tables using Python objects rather than writing raw SQL for every database operation.

### Pydantic

Pydantic is used to validate incoming API requests before they reach the business logic.

This ensures that invalid recipient data is rejected early.

### ReportLab

ReportLab is used to generate PDF certificates programmatically.

It allows the application to use a single predefined template while dynamically inserting recipient-specific information.

### Job and Certificate Separation

A `Job` represents one bulk generation request.

A `Certificate` represents one certificate belonging to that job.

This separation allows the application to track:

* Overall job progress
* Individual certificate status
* Individual certificate errors
* Generated file paths

### Individual Failure Isolation

Every certificate is processed independently.

Conceptually:

```python
for each certificate:

    try:
        generate certificate
        mark SUCCESS

    except error:
        mark FAILED
        store error message

    continue with next certificate
```

This ensures that one failed certificate does not stop the remaining certificates.

### Processing Approach

The current implementation processes certificates immediately after creating the job.

The flow is:

```text
POST /jobs
    |
    v
Create Job
    |
    v
Create Certificate Records
    |
    v
Process Certificates
    |
    v
Update Job Status
    |
    v
Return Job Result
```

This approach was selected because it is simple, deterministic and sufficient for the assignment.

For a production-scale system, certificate processing could be moved to a background job queue such as:

* Celery
* RQ
* Redis-based workers

This would allow long-running bulk jobs to be processed asynchronously.

### Authentication

Authentication was not implemented because it was not required by the assignment.

The implementation focuses on the required certificate generation functionality.

### Docker

Docker was not added because it was not required by the assignment.

The application can be installed and executed directly using Python and a virtual environment.

## Requirements Covered

The implementation satisfies the required assignment functionality:

* Backend API for certificate generation
* Bulk processing in a single request
* Recipient data validation
* One certificate per valid recipient
* Single predefined certificate template
* Generation status tracking
* Job progress tracking
* Successful and failed certificate identification
* Individual certificate failure handling
* Retrieval of generated certificates
* Automated tests
* Setup instructions
* Application run instructions
* Test execution instructions
* API usage examples
* Implementation and design decisions

## Overall Application Flow

```text
Client
  |
  | POST /jobs
  v
FastAPI
  |
  | Validate Request
  v
Pydantic
  |
  | Valid Request
  v
Create Job
  |
  v
Create Certificate Records
  |
  v
Process Each Certificate
  |
  +----------------------+
  |                      |
  v                      v
Generate PDF          Generation Error
  |                      |
  v                      v
SUCCESS                FAILED
  |                      |
  +----------+-----------+
             |
             v
      Update Job Status
             |
             v
       Client Checks
       GET /jobs/{id}
             |
             v
   Retrieve Certificate
   GET /certificates/{id}
```

## Future Improvements

Possible improvements for a production system include:

* Asynchronous background job processing
* PostgreSQL instead of SQLite
* Authentication and authorization
* Retry mechanism for failed certificates
* ZIP download for all certificates in a job
* Configurable certificate templates
* Cloud storage for generated PDFs
* Job cancellation
* Rate limiting
* Docker containerization
* Monitoring and logging

These features are not required for the current assignment and were intentionally kept outside the core implementation.