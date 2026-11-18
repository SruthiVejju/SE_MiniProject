from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from core.audit import NOTICE_PUBLISHED, log_audit_event
from core.models import UserProfile
from core.permissions import get_profile, role_required

from .forms import NoticeForm
from .models import Notice


@login_required
def notice_list(request):
    """
    List notices visible to the current user (FR-11).
    Students only see general announcements or those targeting their block.
    Admins and wardens see all notices.
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

    # Optional search query
    query = request.GET.get('q', '').strip()
    if query:
        notices_qs = notices_qs.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

    return render(request, 'notices/list.html', {
        'notices': notices_qs,
        'profile': profile,
        'query': query,
    })


@role_required(UserProfile.ADMIN)
def notice_create(request):
    """Publish a new notice targeting all students or a specific block (FR-11)."""
    if request.method == 'POST':
        form = NoticeForm(request.POST)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.posted_by = request.user
            notice.save()

            # Dispatch notifications to student accounts
            notice.notify_target_students()

            # Record audit event (SEC-REQ-5)
            log_audit_event(
                NOTICE_PUBLISHED,
                actor=request.user,
                actor_username=request.user.username,
                request=request,
                details={
                    'notice_id': notice.pk,
                    'title': notice.title,
                    'target_block': notice.target_block or 'ALL',
                }
            )

            messages.success(request, 'Notice published successfully.')
            return redirect('notices:list')
    else:
        form = NoticeForm()

    return render(request, 'notices/create.html', {'form': form})


@login_required
def notice_detail(request, pk):
    """View details of a specific notice if permitted."""
    notice = get_object_or_404(Notice.objects.select_related('posted_by'), pk=pk)
    if not notice.is_visible_to(request.user):
        raise PermissionDenied("You do not have permission to view this notice.")

    return render(request, 'notices/detail.html', {'notice': notice})
