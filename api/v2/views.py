"""
API v2 endpoints demonstrating versioning and non-breaking backward compatibility (NFR-8).
API v2 wraps resource collections in standardized envelope responses with metadata.
"""
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone

from api.auth import api_login_required, api_role_required
from core.models import UserProfile
from core.permissions import get_profile
from notices.models import Notice
from hostel.models import Room
from hostel.reports import get_occupancy_data


def api_root_v2(request):
    """API v2 root with standardized metadata envelope."""
    return JsonResponse({
        "api_version": "2.0",
        "timestamp": timezone.now().isoformat(),
        "endpoints": {
            "rooms": "/api/v2/rooms/",
            "notices": "/api/v2/notices/",
            "occupancy_report": "/api/v2/reports/occupancy/",
        }
    })


@api_login_required
def rooms_api_v2(request):
    """
    v2 Rooms API: Enveloped response with total room/bed counts in metadata.
    """
    block_filter = request.GET.get('block', '').strip()
    rooms_qs = Room.objects.prefetch_related('beds').all()
    if block_filter:
        rooms_qs = rooms_qs.filter(block__iexact=block_filter)

    rooms_list = []
    total_beds = 0
    total_occupied = 0

    for room in rooms_qs:
        beds_data = []
        for bed in room.beds.all():
            total_beds += 1
            if bed.is_occupied:
                total_occupied += 1
            beds_data.append({
                "id": bed.pk,
                "bed_number": bed.bed_number,
                "is_occupied": bed.is_occupied
            })
        rooms_list.append({
            "id": room.pk,
            "block": room.block,
            "room_number": room.room_number,
            "floor": room.floor,
            "beds": beds_data
        })

    return JsonResponse({
        "api_version": "2.0",
        "meta": {
            "total_rooms": len(rooms_list),
            "total_beds": total_beds,
            "occupied_beds": total_occupied,
            "vacant_beds": total_beds - total_occupied,
            "timestamp": timezone.now().isoformat(),
        },
        "data": rooms_list
    })


@api_login_required
def notices_api_v2(request):
    """
    v2 Notices API: Enveloped response with target audience metadata and filters.
    """
    profile = get_profile(request.user)
    notices_qs = Notice.objects.select_related('posted_by').all()

    if profile and profile.role == UserProfile.STUDENT:
        student_block = (profile.block or '').strip()
        notices_qs = notices_qs.filter(
            Q(target_block='') |
            Q(target_block__iexact='ALL') |
            Q(target_block__iexact=student_block)
        )

    block_filter = request.GET.get('block', '').strip()
    if block_filter:
        notices_qs = notices_qs.filter(target_block__iexact=block_filter)

    data = [
        {
            "id": n.pk,
            "title": n.title,
            "content": n.content,
            "target_block": n.target_block or "ALL",
            "is_general": n.is_general,
            "posted_by": {
                "id": n.posted_by.pk,
                "username": n.posted_by.username,
            },
            "created_at": n.created_at.isoformat(),
            "updated_at": n.updated_at.isoformat(),
        }
        for n in notices_qs
    ]

    return JsonResponse({
        "api_version": "2.0",
        "meta": {
            "total_count": len(data),
            "user_role": profile.role if profile else None,
            "timestamp": timezone.now().isoformat(),
        },
        "data": data
    })


@api_role_required(UserProfile.ADMIN)
def occupancy_report_api_v2(request):
    """v2 Occupancy API: Structured metrics envelope with health indicators."""
    data = get_occupancy_data()
    return JsonResponse({
        "api_version": "2.0",
        "meta": {
            "generated_at": data['generated_at'].isoformat(),
            "system_health": "optimal",
        },
        "summary": {
            "total_blocks": data['total_blocks'],
            "total_rooms": data['total_rooms'],
            "total_beds": data['total_beds'],
            "total_occupied": data['total_occupied'],
            "total_vacant": data['total_vacant'],
            "overall_occupancy_rate": data['overall_rate'],
        },
        "data": data['blocks']
    })
