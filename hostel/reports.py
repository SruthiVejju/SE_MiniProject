"""
Hostel Occupancy Reporting and PDF Export Service (FR-12).
Generates per-block and system-wide occupancy metrics matching active allocation records.
"""
import io
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from .models import Allocation, Bed, Room


def get_occupancy_data():
    """
    Calculate total, occupied, and vacant beds per hostel block (FR-12).
    Occupancy numbers strictly reflect active allocation records.
    """
    blocks = (
        Room.objects.values_list('block', flat=True)
        .distinct()
        .order_by('block')
    )

    block_stats = []
    grand_rooms = 0
    grand_beds = 0
    grand_occupied = 0

    for block in blocks:
        rooms_count = Room.objects.filter(block=block).count()
        beds_count = Bed.objects.filter(room__block=block).count()
        occupied_beds = Allocation.objects.filter(is_active=True, bed__room__block=block).count()
        vacant_beds = max(0, beds_count - occupied_beds)
        rate = round((occupied_beds / beds_count * 100), 1) if beds_count > 0 else 0.0

        block_stats.append({
            'block': block,
            'rooms': rooms_count,
            'beds': beds_count,
            'occupied': occupied_beds,
            'vacant': vacant_beds,
            'rate': rate,
        })

        grand_rooms += rooms_count
        grand_beds += beds_count
        grand_occupied += occupied_beds

    grand_vacant = max(0, grand_beds - grand_occupied)
    overall_rate = round((grand_occupied / grand_beds * 100), 1) if grand_beds > 0 else 0.0

    return {
        'blocks': block_stats,
        'total_blocks': len(block_stats),
        'total_rooms': grand_rooms,
        'total_beds': grand_beds,
        'total_occupied': grand_occupied,
        'total_vacant': grand_vacant,
        'overall_rate': overall_rate,
        'generated_at': timezone.now(),
    }


def generate_occupancy_pdf(data):
    """
    Render occupancy report data as a formatted PDF byte stream (FR-12).
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=6,
    )
    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#4B5563'),
        spaceAfter=14,
    )

    elements = []

    # Header
    elements.append(Paragraph("Hostel Management System - Occupancy Report", title_style))
    gen_time = data['generated_at'].strftime("%Y-%m-%d %H:%M:%S UTC")
    elements.append(Paragraph(f"Generated at: {gen_time} | Specification Trace: FR-12", meta_style))

    # Summary box
    summary_data = [
        ["Total Blocks", "Total Rooms", "Total Beds", "Occupied Beds", "Vacant Beds", "Occupancy Rate"],
        [
            str(data['total_blocks']),
            str(data['total_rooms']),
            str(data['total_beds']),
            str(data['total_occupied']),
            str(data['total_vacant']),
            f"{data['overall_rate']}%",
        ],
    ]
    summary_table = Table(summary_data, colWidths=[90, 90, 90, 90, 90, 90])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#EFF6FF')),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BFDBFE')),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 18))

    # Per-Block Breakdown
    elements.append(Paragraph("Per-Block Occupancy Breakdown", styles['Heading2']))
    table_data = [["Hostel Block", "Rooms", "Total Beds", "Occupied Beds", "Vacant Beds", "Occupancy Rate"]]

    for b in data['blocks']:
        table_data.append([
            f"Block {b['block']}",
            str(b['rooms']),
            str(b['beds']),
            str(b['occupied']),
            str(b['vacant']),
            f"{b['rate']}%",
        ])

    # Totals row
    table_data.append([
        "Total (All Blocks)",
        str(data['total_rooms']),
        str(data['total_beds']),
        str(data['total_occupied']),
        str(data['total_vacant']),
        f"{data['overall_rate']}%",
    ])

    block_table = Table(table_data, colWidths=[120, 80, 85, 85, 85, 85])
    block_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#374151')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#F3F4F6')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    elements.append(block_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
