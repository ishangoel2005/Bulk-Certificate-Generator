import os

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas


PAGE_WIDTH, PAGE_HEIGHT = landscape(A4)


def generate_certificate(
    recipient_name: str,
    event_name: str,
    event_date: str,
    output_path: str
) -> str:
    """
    Generate one certificate PDF.

    Returns the generated file path.
    """

    output_directory = os.path.dirname(output_path)

    if output_directory:
        os.makedirs(output_directory, exist_ok=True)

    pdf = canvas.Canvas(
        output_path,
        pagesize=(PAGE_WIDTH, PAGE_HEIGHT)
    )

    # Background border
    margin = 30

    pdf.setLineWidth(3)
    pdf.rect(
        margin,
        margin,
        PAGE_WIDTH - 2 * margin,
        PAGE_HEIGHT - 2 * margin
    )

    # Title
    pdf.setFont("Helvetica-Bold", 28)

    title = "CERTIFICATE OF COMPLETION"

    title_width = pdf.stringWidth(
        title,
        "Helvetica-Bold",
        28
    )

    pdf.drawString(
        (PAGE_WIDTH - title_width) / 2,
        PAGE_HEIGHT - 130,
        title
    )

    # Introductory text
    pdf.setFont("Helvetica", 16)

    text = "This is to certify that"

    text_width = pdf.stringWidth(
        text,
        "Helvetica",
        16
    )

    pdf.drawString(
        (PAGE_WIDTH - text_width) / 2,
        PAGE_HEIGHT - 200,
        text
    )

    # Recipient name
    pdf.setFont("Helvetica-Bold", 30)

    name_width = pdf.stringWidth(
        recipient_name,
        "Helvetica-Bold",
        30
    )

    pdf.drawString(
        (PAGE_WIDTH - name_width) / 2,
        PAGE_HEIGHT - 260,
        recipient_name
    )

    # Completion text
    pdf.setFont("Helvetica", 16)

    completion_text = (
        f"has successfully completed {event_name}"
    )

    completion_width = pdf.stringWidth(
        completion_text,
        "Helvetica",
        16
    )

    pdf.drawString(
        (PAGE_WIDTH - completion_width) / 2,
        PAGE_HEIGHT - 320,
        completion_text
    )

    # Date
    pdf.setFont("Helvetica", 14)

    date_text = f"Date: {event_date}"

    date_width = pdf.stringWidth(
        date_text,
        "Helvetica",
        14
    )

    pdf.drawString(
        (PAGE_WIDTH - date_width) / 2,
        PAGE_HEIGHT - 370,
        date_text
    )

    # Signature line
    pdf.line(
        PAGE_WIDTH / 2 - 100,
        100,
        PAGE_WIDTH / 2 + 100,
        100
    )

    pdf.setFont("Helvetica", 12)

    signature_text = "Organizer"

    signature_width = pdf.stringWidth(
        signature_text,
        "Helvetica",
        12
    )

    pdf.drawString(
        (PAGE_WIDTH - signature_width) / 2,
        80,
        signature_text
    )

    pdf.save()

    return output_path