import json
from decimal import Decimal
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from api.auth import api_error_response, api_login_required, api_role_required, parse_json_body
from core.audit import NOTICE_PUBLISHED, log_audit_event
from core.models import UserProfile
from core.permissions import get_profile
from complaints.models import Complaint
from hostel.models import Allocation, Bed, Room
from hostel.reports import generate_occupancy_pdf, get_occupancy_data
from leaves.forms import LeaveRequestForm
from leaves.models import LeaveRequest
from leaves.services import submit_leave
from notices.models import Notice


def api_root(request):
    """API v1 root listing available resources."""
    return JsonResponse({
        "version": "1.0",
        "endpoints": {
            "health": "/api/v1/health/",
            "rooms": "/api/v1/rooms/",
            "notices": "/api/v1/notices/",
            "occupancy_report": "/api/v1/reports/occupancy/",
            "complaints": "/api/v1/complaints/",
            "leaves": "/api/v1/leaves/",
            "fees_dues": "/api/v1/fees/dues/",
        }
    })


def health_check(request):
    """API v1 health status endpoint."""
    return JsonResponse({"status": "healthy", "version": "1.0"})


@api_login_required
def rooms_api(request):
    """List hostel rooms and bed allocation statuses."""
    rooms = Room.objects.prefetch_related('beds').all()
    data = []
    for room in rooms:
        data.append({
            "id": room.pk,
            "block": room.block,
            "room_number": room.room_number,
            "floor": room.floor,
            "beds": [
                {
                    "id": bed.pk,
                    "bed_number": bed.bed_number,
                    "is_occupied": bed.is_occupied
                }
                for bed in room.beds.all()
            ]
        })
    return JsonResponse(data, safe=False)


@csrf_exempt
@api_login_required
def notices_api(request):
    """
    GET: List notices visible to the authenticated user.
    POST: Publish a notice (Admin only, FR-11).
    """
    if request.method == 'GET':
        profile = get_profile(request.user)
        notices_qs = Notice.objects.select_related('posted_by').all()

        if profile and profile.role == UserProfile.STUDENT:
            student_block = (profile.block or '').strip()
            notices_qs = notices_qs.filter(
                Q(target_block='') |
                Q(target_block__iexact='ALL') |
                Q(target_block__iexact=student_block)
            )

        data = [
            {
                "id": n.pk,
                "title": n.title,
                "content": n.content,
                "target_block": n.target_block or "ALL",
                "posted_by": n.posted_by.username,
                "created_at": n.created_at.isoformat(),
            }
            for n in notices_qs
        ]
        return JsonResponse(data, safe=False)

    elif request.method == 'POST':
        profile = get_profile(request.user)
        if not profile or profile.role != UserProfile.ADMIN:
            return api_error_response("Only admins may publish notices.", status=403, code="FORBIDDEN")

        body = parse_json_body(request)
        if body is None:
            return api_error_response("Invalid JSON payload in request body.", status=400)

        title = str(body.get('title', '')).strip()
        content = str(body.get('content', '')).strip()
        target_block = str(body.get('target_block', '')).strip()

        if not title or len(title) < 3:
            return api_error_response("Title is required (min 3 characters).", status=400)
        if not content or len(content) < 5:
            return api_error_response("Content is required (min 5 characters).", status=400)

        notice = Notice.objects.create(
            title=title,
            content=content,
            target_block=target_block if target_block.upper() != 'ALL' else '',
            posted_by=request.user
        )
        notice.notify_target_students()

        log_audit_event(
            NOTICE_PUBLISHED,
            actor=request.user,
            actor_username=request.user.username,
            request=request,
            details={"notice_id": notice.pk, "title": notice.title, "target_block": target_block or "ALL"}
        )

        return JsonResponse({
            "message": "Notice published successfully.",
            "notice": {
                "id": notice.pk,
                "title": notice.title,
                "content": notice.content,
                "target_block": notice.target_block or "ALL",
                "posted_by": notice.posted_by.username,
                "created_at": notice.created_at.isoformat(),
            }
        }, status=201)

    return api_error_response("Method not allowed.", status=405)


@api_login_required
def notice_detail_api(request, pk):
    """Retrieve details of a single notice."""
    try:
        notice = Notice.objects.select_related('posted_by').get(pk=pk)
    except Notice.DoesNotExist:
        return api_error_response("Notice not found.", status=404)

    if not notice.is_visible_to(request.user):
        return api_error_response("You do not have permission to view this notice.", status=403, code="FORBIDDEN")

    return JsonResponse({
        "id": notice.pk,
        "title": notice.title,
        "content": notice.content,
        "target_block": notice.target_block or "ALL",
        "posted_by": notice.posted_by.username,
        "created_at": notice.created_at.isoformat(),
    })


@api_role_required(UserProfile.ADMIN)
def occupancy_report_api(request):
    """Generate hostel occupancy report in JSON (or PDF if format=pdf) (FR-12)."""
    data = get_occupancy_data()

    if request.GET.get('format') == 'pdf':
        pdf_bytes = generate_occupancy_pdf(data)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="occupancy_report.pdf"'
        return response

    return JsonResponse({
        "generated_at": data['generated_at'].isoformat(),
        "summary": {
            "total_blocks": data['total_blocks'],
            "total_rooms": data['total_rooms'],
            "total_beds": data['total_beds'],
            "total_occupied": data['total_occupied'],
            "total_vacant": data['total_vacant'],
            "overall_occupancy_rate": data['overall_rate'],
        },
        "blocks": data['blocks']
    })


@csrf_exempt
@api_login_required
def complaints_api(request):
    """
    GET: List complaints relevant to current user.
    POST: Submit a new complaint (Student only, NFR-7).
    """
    profile = get_profile(request.user)

    if request.method == 'GET':
        if profile.role == UserProfile.STUDENT:
            qs = Complaint.objects.filter(student=request.user)
        elif profile.role == UserProfile.WARDEN:
            qs = Complaint.objects.filter(student__profile__block=profile.block)
        else:
            qs = Complaint.objects.all()

        data = [
            {
                "id": str(c.complaint_id),
                "student": c.student.username,
                "category": c.category,
                "description": c.description,
                "status": c.status,
                "created_at": c.created_at.isoformat(),
            }
            for c in qs
        ]
        return JsonResponse(data, safe=False)

    elif request.method == 'POST':
        if profile.role != UserProfile.STUDENT:
            return api_error_response("Only students may submit complaints.", status=403, code="FORBIDDEN")

        body = parse_json_body(request)
        if body is None:
            return api_error_response("Invalid JSON payload.", status=400)

        category = str(body.get('category', '')).strip().lower()
        description = str(body.get('description', '')).strip()

        valid_categories = [c[0] for c in Complaint.CATEGORY_CHOICES]
        if category not in valid_categories:
            return api_error_response(f"Invalid category. Must be one of: {valid_categories}.", status=400)
        if not description or len(description) < 5:
            return api_error_response("Description must be at least 5 characters.", status=400)

        with transaction.atomic():
            complaint = Complaint.objects.create(
                student=request.user,
                category=category,
                description=description
            )

        return JsonResponse({
            "message": "Complaint submitted successfully.",
            "complaint": {
                "id": str(complaint.complaint_id),
                "category": complaint.category,
                "description": complaint.description,
                "status": complaint.status,
                "created_at": complaint.created_at.isoformat(),
            }
        }, status=201)

    return api_error_response("Method not allowed.", status=405)


@csrf_exempt
@api_login_required
def leaves_api(request):
    """
    GET: List leave requests for current user.
    POST: Submit a leave request (Student only, NFR-7).
    """
    profile = get_profile(request.user)

    if request.method == 'GET':
        if profile.role == UserProfile.STUDENT:
            qs = LeaveRequest.objects.filter(student=request.user)
        elif profile.role == UserProfile.WARDEN:
            qs = LeaveRequest.objects.filter(block=profile.block)
        else:
            qs = LeaveRequest.objects.all()

        data = [
            {
                "id": req.pk,
                "student": req.student.username,
                "block": req.block,
                "destination": req.destination,
                "from_date": req.from_date.isoformat(),
                "to_date": req.to_date.isoformat(),
                "reason": req.reason,
                "status": req.status,
                "created_at": req.created_at.isoformat(),
            }
            for req in qs
        ]
        return JsonResponse(data, safe=False)

    return api_error_response("Method not allowed.", status=405)


@api_role_required(UserProfile.STUDENT)
def fees_dues_api(request):
    """Retrieve current student fee dues and balance."""
    fee_account = getattr(request.user, "fee_account", None)
    if not fee_account:
        return JsonResponse({
            "student": request.user.username,
            "total_fee": "0.00",
            "amount_paid": "0.00",
            "due": "0.00"
        })

    return JsonResponse({
        "student": request.user.username,
        "total_fee": str(fee_account.total_fee),
        "amount_paid": str(fee_account.amount_paid),
        "due": str(fee_account.due)
    })
