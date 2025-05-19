import io

# import os
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    # TableStyle,
    HRFlowable,
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch
from reportlab.lib import colors


# Register Cambria or fallback to Times New Roman
try:
    pdfmetrics.registerFont(TTFont("Cambria", "Cambria.ttf"))
    base_font = "Cambria"
except Exception:
    pdfmetrics.registerFont(TTFont("TimesNewRoman", "times.ttf"))
    base_font = "TimesNewRoman"

# Load JSON Data (simulating your provided data structure)
cv_data = {
    "name": "",
    "contact": {"email": "", "phone": ""},
    "personal_statement": "",
    "work_experience": [
        {
            "title": "",
            "company": "",
            "location": "",
            "dates": "",
            "responsibilities": ["", "", "...additional responsibilities"],
        },
        {
            "title": "",
            "company": "",
            "location": "",
            "dates": "",
            "responsibilities": ["", "", "...additional responsibilities"],
        },
        # ... additional experiences
    ],
    "education": [
        {
            "institution": "",
            "location": "",
            "degree": "",
            "dates": "",
            "achievement": "",
            "experience": ["", "", "...additional experiences"],
        },
        {
            "institution": "",
            "location": "",
            "degree": "",
            "dates": "",
            "achievement": "",
            "experience": ["", "", "...additional experiences"],
        },
        # ... additional education
    ],
    "key_skills": ["", "", "...additional skills"],
    "references": ["", "", "...additional references"],
}


# Customise the pdf name
# Create PDF
def generate_cv(data):
    # filename = f"cv-{data['name'].strip().replace(' ', '_')}.pdf".lower()
    # print("Filename: ", filename)
    # Check if filename is empty
    buffer = io.BytesIO()  # In-memory buffer
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=50,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="TitleCustom",
            fontName=base_font,
            fontSize=20,
            spaceAfter=6,
            leading=24,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SubTitle",
            fontName=base_font,
            fontSize=10,
            alignment=2,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Heading1Custom",
            fontName=base_font,
            fontSize=14,
            textColor=colors.HexColor("#003366"),
            spaceAfter=10,
            leading=16,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Heading2Custom",
            fontName=base_font,
            fontSize=11,
            spaceAfter=4,
            leading=14,
        )
    )
    styles.add(
        ParagraphStyle(
            name="NormalCustom",
            fontName=base_font,
            fontSize=9,
            leading=13,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BulletCustom",
            fontName=base_font,
            fontSize=8,
            leftIndent=12,
            bulletIndent=12,
            bulletFontSize=8,
            leading=12,
        )
    )

    story = []

    header_table = Table(
        [
            [
                Paragraph(f"<b>{data['name']}</b>", styles["TitleCustom"]),
                Paragraph(
                    f"{data['contact']['email']}<br/>{data['contact']['phone']}",
                    styles["SubTitle"],
                ),
            ]
        ],
        colWidths=[3.5 * inch, 2.5 * inch],
    )
    story.append(header_table)
    story.append(
        HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#003366"))
    )
    story.append(Spacer(1, 10))

    story.append(Paragraph("Personal Statement", styles["Heading1Custom"]))
    story.append(Paragraph(data["personal_statement"], styles["NormalCustom"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Work Experience", styles["Heading1Custom"]))
    for job in data["work_experience"]:
        story.append(
            Paragraph(
                f"<b>{job['title']} – {job['company']} ({job['dates']})</b>",
                styles["Heading2Custom"],
            )
        )
        story.append(Paragraph(job["location"], styles["NormalCustom"]))
        for bullet in job["responsibilities"]:
            story.append(Paragraph(f"• {bullet}", styles["BulletCustom"]))
        story.append(Spacer(1, 8))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Education", styles["Heading1Custom"]))
    for edu in data["education"]:
        degree = edu.get("degree", edu.get("course", edu.get("certificate", "")))
        story.append(
            Paragraph(
                f"<b>{degree} – {edu['institution']} ({edu['dates']})</b>",
                styles["Heading2Custom"],
            )
        )
        story.append(Paragraph(edu["location"], styles["NormalCustom"]))
        if "achievement" in edu:
            story.append(
                Paragraph(
                    f"Achievement: {edu['achievement']}",
                    styles["NormalCustom"],
                )
            )
        if "experience" in edu:
            story.append(Paragraph("Experience: ", styles["NormalCustom"]))
            for exp in edu["experience"]:
                story.append(Paragraph(f"• {exp}", styles["BulletCustom"]))
        story.append(Spacer(1, 6))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Key Skills", styles["Heading1Custom"]))
    for skill in data["key_skills"]:
        story.append(Paragraph(f"• {skill}", styles["BulletCustom"]))

    story.append(Spacer(1, 10))
    story.append(Paragraph("References", styles["Heading1Custom"]))
    if data["references"]:
        for ref in data["references"]:
            story.append(Paragraph(ref, styles["NormalCustom"]))
    else:
        story.append(Paragraph("Available upon request", styles["NormalCustom"]))
    story.append(Spacer(1, 10))

    doc.build(story)
    buffer.seek(0)
    # This is now a file-like object you can store in session state
    return buffer


# Run it
if __name__ == "__main__":
    generate_cv(cv_data)
