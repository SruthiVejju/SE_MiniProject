"""
Generate a professional, structured PDF Presentation Script for Shubashitha.
Covers:
- Word-for-word spoken script
- What to show on screen during demo
- Technical architecture explanations
- Teacher Q&A preparation
"""
import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print total page numbers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#6B7280"))
        
        # Header (pages after page 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "Hostel Management System — Presentation Script | Shubashitha G")
            self.setStrokeColor(colors.HexColor("#E5E7EB"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)

        # Footer
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, footer_text)
        self.drawString(54, 36, "SE Mini-Project Deliverables — Sprint 2 Final Evaluation")
        self.setStrokeColor(colors.HexColor("#E5E7EB"))
        self.setLineWidth(0.5)
        self.line(54, 46, 558, 46)
        self.restoreState()


def build_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#4B5563'),
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#1F2937'),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'StandardBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=6
    )

    script_quote = ParagraphStyle(
        'SpokenSpeech',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#111827'),
        spaceBefore=4,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#374151'),
        leftIndent=15,
        spaceAfter=3
    )

    demo_note = ParagraphStyle(
        'DemoAction',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#B45309')
    )

    tech_note = ParagraphStyle(
        'TechDetail',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#065F46')
    )

    elements = []

    # Title & Metadata Banner
    elements.append(Paragraph("Hostel Management System (HMS)", title_style))
    elements.append(Paragraph("<b>Final Project Evaluation — Oral Presentation Script & Technical Guide</b>", subtitle_style))
    
    meta_table_data = [
        [Paragraph("<b>Student Presenter:</b> Shubashitha G", body_style), Paragraph("<b>Assigned Role:</b> Team Member 4", body_style)],
        [Paragraph("<b>GitHub Handle:</b> @shubashithagowtham-ship-it", body_style), Paragraph("<b>Sprint:</b> Sprint 2 (Final Release)", body_style)],
        [Paragraph("<b>Core Deliverables:</b> FR-11, FR-12, NFR-7, NFR-8, SEC-REQ-5", body_style), Paragraph("<b>Verification Status:</b> 145/145 Tests Passing | 91% Coverage", body_style)],
    ]
    meta_table = Table(meta_table_data, colWidths=[250, 254])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F3F4F6')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#D1D5DB')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 14))

    # Presentation Overview Box
    overview_text = (
        "<b>Presentation Strategy:</b> You have 3–4 minutes to present. Your part bridges the operational "
        "user-facing experience (Notices, Announcements, Occupancy Reports) with the heavy software engineering "
        "standards (Server Durability NFR-7, Versioned REST APIs NFR-8, and Immutable Audit Logging SEC-REQ-5). "
        "Speak clearly, follow the <b>'What to Say'</b> script below, and point to the live web screens."
    )
    callout = Table([[Paragraph(overview_text, body_style)]], colWidths=[504])
    callout.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#EFF6FF')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#93C5FD')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(callout)
    elements.append(Spacer(1, 14))

    # SECTION 1: INTRODUCTION
    elements.append(Paragraph("1. Introduction & Role Definition", h1_style))
    intro_speech = (
        "\"Good morning / afternoon Ma'am. My name is <b>Shubashitha</b>. In our Hostel Management System team, "
        "my responsibility focused on communication, reporting, and operational reliability.<br/><br/>"
        "Specifically, I developed: "
        "<b>First</b>, the Hostel Notices & Announcement broadcast system with selective block targeting (FR-11). "
        "<b>Second</b>, the Real-time Occupancy Information and PDF Export module (FR-12). "
        "<b>Third</b>, our request persistence architecture guaranteeing zero data loss across server restarts (NFR-7). "
        "<b>Fourth</b>, our versioned REST API supporting backwards-compatible client integrations (NFR-8). "
        "And <b>Fifth</b>, an immutable, append-only security Audit Log with a 1-year retention policy (SEC-REQ-5).\""
    )
    elements.append(Paragraph(intro_speech, script_quote))
    elements.append(Spacer(1, 10))

    # SECTION 2: NOTICES & ANNOUNCEMENTS
    elements.append(Paragraph("2. Module 1: Notices, Announcements & In-App Alerts (FR-11)", h1_style))
    elements.append(Paragraph("<b>Concept & Purpose:</b> Hostels constantly need to circulate information—such as water maintenance, library timings, or emergency inspections. However, broadcasting every notice to everyone creates spam. Our system allows administrators to either target the whole hostel or restrict notices to a specific hostel block (e.g., Block A only).", body_style))
    
    notices_speech = (
        "\"Moving to our communication module: Under <b>FR-11</b>, we implemented hostel notices and announcements. "
        "When an Admin publishes a circular, they can set the audience to either 'All Students' or restrict it to a specific hostel block, such as Block A.<br/><br/>"
        "Our role-based visibility rules guarantee that students in Block B will never see private maintenance notices meant for Block A. "
        "Furthermore, as soon as an announcement is published, our system automatically dispatches real-time in-app notifications to the target students' accounts, "
        "and highlights the latest circulars directly on their home dashboard.\""
    )
    elements.append(Paragraph(notices_speech, script_quote))
    
    demo_box_1 = [
        [Paragraph("<b>SCREEN DEMO ACTION:</b><br/>1. Log in as <code>admin</code> -> Click <b>'Notices'</b> in top navigation bar -> Click <b>'Publish Notice'</b>.<br/>2. Fill in: Title = <i>'Block A Water Tank Cleaning'</i>, Target Audience = <i>'Block A'</i>.<br/>3. Log in as <code>student_a</code> (Block A resident): show that the notice appears on the dashboard.<br/>4. Log in as <code>student_b</code> (Block B resident): show that the notice does NOT appear (filtered cleanly).", demo_note)],
        [Paragraph("<b>UNDER THE HOOD (CODE):</b><br/>• Model: <code>notices.Notice</code> with <code>target_block</code> and <code>is_visible_to(user)</code> filter logic.<br/>• Form: <code>NoticeForm</code> with server-side text sanitization via <code>core.validators.sanitize_text</code> to block XSS.<br/>• Automated Tests: <code>notices.tests.NoticeTests</code> covering general & targeted visibility, search, and notification dispatch.", tech_note)]
    ]
    t1 = Table(demo_box_1, colWidths=[504])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FEF3C7')),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#ECFDF5')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t1)
    elements.append(Spacer(1, 12))

    # SECTION 3: OCCUPANCY REPORTING & PDF EXPORT
    elements.append(Paragraph("3. Module 2: Room Occupancy Reporting & PDF Generation (FR-12)", h1_style))
    elements.append(Paragraph("<b>Concept & Purpose:</b> Hostel wardens and managers need instant clarity on available bed capacity. They also need printable official documents for university auditors and hostel committees without manually aggregating Excel sheets.", body_style))

    occ_speech = (
        "\"Next is <b>FR-12: Hostel Occupancy Reporting</b>. We built an automated reporting engine that calculates "
        "total rooms, total beds, occupied beds, vacant beds, and occupancy percentage for each hostel block, along with system-wide totals.<br/><br/>"
        "A critical software engineering rule here is data reconciliation: the occupancy numbers are computed directly from active allocation records in the database, "
        "preventing any discrepancy between room status and student allocations.<br/><br/>"
        "Additionally, we integrated a native PDF generation pipeline using ReportLab. With a single click on 'Export as PDF', the administrator receives "
        "a professional, timestamped administrative report suitable for official documentation.\""
    )
    elements.append(Paragraph(occ_speech, script_quote))

    demo_box_2 = [
        [Paragraph("<b>SCREEN DEMO ACTION:</b><br/>1. Log in as <code>admin</code> -> Click <b>'Occupancy Report'</b> in navbar (<code>/hostel/reports/occupancy/</code>).<br/>2. Point out the summary cards (Hostel Blocks, Total Rooms, Total Beds, Occupied, Vacant, Occupancy Rate %).<br/>3. Point out the per-block breakdown table.<br/>4. Click the <b>'Export as PDF'</b> button: show the downloaded <code>hostel_occupancy_report.pdf</code> opening cleanly in the browser.", demo_note)],
        [Paragraph("<b>UNDER THE HOOD (CODE):</b><br/>• Service: <code>hostel.reports.get_occupancy_data()</code> aggregates live DB queries across <code>Room</code>, <code>Bed</code>, and <code>Allocation</code>.<br/>• PDF Engine: <code>hostel.reports.generate_occupancy_pdf()</code> builds tables, typography, and styling into an in-memory byte buffer (<code>io.BytesIO</code>).<br/>• Security: Endpoint protected by <code>@role_required(UserProfile.ADMIN)</code>. Students receive 403 Forbidden.", tech_note)]
    ]
    t2 = Table(demo_box_2, colWidths=[504])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FEF3C7')),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#ECFDF5')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t2)
    elements.append(Spacer(1, 12))

    # SECTION 4: NFR-7 & NFR-8 & SEC-REQ-5
    elements.append(Paragraph("4. Technical Quality: Durability (NFR-7), REST API (NFR-8) & Audit Log (SEC-REQ-5)", h1_style))
    
    nfr_speech = (
        "\"Beyond functional UI screens, I implemented three essential architectural non-functional and security requirements:<br/><br/>"
        "<b>1. Reliability & Server Durability (NFR-7):</b> We instituted a strict 'persistence-before-acknowledgment' pattern. "
        "Whenever a student submits a complaint or leave request, the write is executed inside an atomic transaction (<code>transaction.atomic</code>). "
        "The HTTP 200/302 success response is only sent after the database confirms the write to disk. "
        "In our test suite, we simulate abrupt cold server restarts by forcefully dropping all connections, verifying that no submitted request is ever lost.<br/><br/>"
        "<b>2. Versioned REST API (NFR-8):</b> We exposed standard JSON endpoints under <code>/api/v1/</code> and <code>/api/v2/</code>. "
        "To satisfy NFR-8's backward-compatibility clause, when we upgraded to v2 with standardized metadata envelopes, v1 endpoints remained completely unaltered "
        "so legacy clients and external mobile apps continue running without failure.<br/><br/>"
        "<b>3. Append-Only Audit Logging (SEC-REQ-5):</b> To comply with institutional security auditing, we designed an immutable <code>AuditLog</code> store. "
        "It records every successful login, failed authentication attempt, account lockout, room allocation change, and fee payment. "
        "At the model level, calling <code>.save()</code> or <code>.delete()</code> on an existing entry throws a <code>PermissionError</code>, "
        "and every record enforces an automated 1-year (365 days) retention period.\""
    )
    elements.append(Paragraph(nfr_speech, script_quote))

    demo_box_3 = [
        [Paragraph("<b>SCREEN DEMO ACTION:</b><br/>1. Log in as <code>admin</code> -> Click <b>'Audit Logs'</b> (<code>/audit/</code>).<br/>2. Show the log table displaying login events, IP addresses, actor usernames, and retention expiration dates.<br/>3. Open the browser or Postman to <code>/api/v1/notices/</code> (returns JSON array) and <code>/api/v2/notices/</code> (returns JSON metadata envelope).", demo_note)],
        [Paragraph("<b>UNDER THE HOOD (CODE):</b><br/>• Durability: <code>core.test_nfr7_durability</code> tests connection teardown restart survival.<br/>• REST API: <code>api.v1</code> and <code>api.v2</code> modular routing with JSON RBAC decorators.<br/>• Audit Log: <code>core.models.AuditLog</code> with immutable methods and <code>core.audit.log_audit_event()</code>.", tech_note)]
    ]
    t3 = Table(demo_box_3, colWidths=[504])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FEF3C7')),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#ECFDF5')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t3)
    elements.append(Spacer(1, 12))

    # SECTION 5: PLANNED FEATURES (NOT YET IMPLEMENTED)
    elements.append(Paragraph("5. Planned Features & Future Roadmap (Image 2 Deliverable)", h1_style))
    elements.append(Paragraph("<b>Why this matters:</b> Teachers always ask: <i>'What did you plan that is not yet implemented?'</i> Having a crisp, structured answer demonstrates real software engineering maturity.", body_style))

    roadmap_speech = (
        "\"To conclude with our forward-looking engineering roadmap: while our core Sprint 2 objectives are complete with 91% test coverage, "
        "we have designed three planned architectural enhancements for future sprints:<br/><br/>"
        "• <b>SMS & Push Notification Gateway Integration:</b> Currently, notifications are delivered in-app. The next phase will link Firebase Cloud Messaging (FCM) and Twilio SMS gateways to alert students even when offline.<br/>"
        "• <b>Predictive Occupancy Forecasting:</b> Expanding our occupancy reporting module with an analytics model that forecasts room demand and bed vacancies for subsequent semesters based on historical course admissions.<br/>"
        "• <b>Cryptographic Audit Trail Anchoring:</b> Enhancing our append-only audit store with HMAC SHA-256 hash-chaining so any external database tampering can be mathematically detected.\""
    )
    elements.append(Paragraph(roadmap_speech, script_quote))
    elements.append(Spacer(1, 12))

    # SECTION 6: TEACHER VIVA Q&A CHEAT SHEET
    elements.append(Paragraph("6. Teacher Viva / Q&A Defense Cheat Sheet", h1_style))
    elements.append(Paragraph("Here are the exact questions the teacher is most likely to ask you, along with bullet-proof answers:", body_style))

    qa_data = [
        [
            Paragraph("<b>Q1: How do you prevent a student in Block B from seeing a Block A notice?</b>", h2_style),
            Paragraph("<b>Your Answer:</b> In <code>notices/views.py</code>, we query the user's role and assigned block from <code>UserProfile</code>. If the user is a student, we apply a Django Q filter: <code>Q(target_block='') | Q(target_block__iexact='ALL') | Q(target_block__iexact=student.block)</code>. If the student manually enters the URL for another block's notice (<code>/notices/{id}/</code>), the <code>notice_detail</code> view calls <code>notice.is_visible_to(user)</code> and raises a <code>403 PermissionDenied</code>.", body_style)
        ],
        [
            Paragraph("<b>Q2: How is the PDF generated for the Occupancy Report?</b>", h2_style),
            Paragraph("<b>Your Answer:</b> We use ReportLab inside <code>hostel/reports.py</code>. We pull live allocation numbers directly from the database, format them into a structured <code>SimpleDocTemplate</code> with custom table styles, and build the document into an in-memory <code>io.BytesIO</code> buffer. The Django view returns an <code>HttpResponse</code> with <code>Content-Type: application/pdf</code> and an attachment header.", body_style)
        ],
        [
            Paragraph("<b>Q3: What guarantees that your audit log is truly append-only?</b>", h2_style),
            Paragraph("<b>Your Answer:</b> We enforce immutability at the model layer in <code>core/models.py</code>. The <code>save()</code> method checks if <code>self.pk is not None</code>; if so, it throws a <code>PermissionError</code>, preventing updates. The <code>delete()</code> method also raises a <code>PermissionError</code>. In Django Admin, <code>has_add_permission</code>, <code>has_change_permission</code>, and <code>has_delete_permission</code> all return <code>False</code>.", body_style)
        ],
        [
            Paragraph("<b>Q4: How does NFR-7 prevent data loss during a server crash?</b>", h2_style),
            Paragraph("<b>Your Answer:</b> We implement the 'persistence-before-acknowledgment' pattern. Submissions for complaints and leaves are enclosed in <code>with transaction.atomic():</code>. The database flushes the transaction to durable storage before Django renders the HTTP 200/302 response. If the server crashes mid-flight, an uncommitted transaction rolls back cleanly, leaving zero corrupted or orphaned records.", body_style)
        ],
        [
            Paragraph("<b>Q5: How does your REST API satisfy NFR-8 versioning?</b>", h2_style),
            Paragraph("<b>Your Answer:</b> We maintain URI path versioning: <code>/api/v1/</code> and <code>/api/v2/</code>. When we introduced v2 with a metadata envelope structure (<code>meta</code> and <code>data</code>), we left v1 completely untouched. Existing client integrations communicating with v1 continue to receive flat JSON arrays without breaking.", body_style)
        ],
        [
            Paragraph("<b>Q6: What were your test results and coverage metrics?</b>", h2_style),
            Paragraph("<b>Your Answer:</b> Our entire project test suite has 145 automated tests with a 100% pass rate. We achieved 91% code coverage, significantly beating the course requirement of 70% under NFR-5. Additionally, Bandit security scans show zero high-severity vulnerabilities.", body_style)
        ]
    ]

    for item in qa_data:
        box = Table([[item[0]], [item[1]]], colWidths=[504])
        box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F3F4F6')),
            ('BACKGROUND', (0, 1), (-1, 1), colors.white),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(box)
        elements.append(Spacer(1, 6))

    elements.append(Spacer(1, 10))
    conclusion_text = (
        "<b>Final Presentation Closing:</b> <i>\"Thank you Ma'am. To summarize, my modules delivered complete operational "
        "transparency through notices and occupancy reporting, backed by strict persistence guarantees, clean REST versioning, "
        "and security audit trails. My team and I are ready for any further questions.\"</i>"
    )
    elements.append(Paragraph(conclusion_text, body_style))

    doc.build(elements, canvasmaker=NumberedCanvas)
    print(f"Presentation Script PDF successfully built at: {output_path}")


if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "docs")
    os.makedirs(out_dir, exist_ok=True)
    pdf_path = os.path.join(out_dir, "Shubashitha_Presentation_Script.pdf")
    build_pdf(pdf_path)
