from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.models import UserProfile
from core.permissions import role_required

from .forms import VisitorEntryForm
from .models import Visitor


@role_required(UserProfile.SECURITY)
def log_entry(request):
    form = VisitorEntryForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        Visitor.objects.create(logged_by=request.user, **form.cleaned_data)
        messages.success(request, 'Visitor entry recorded.')
        return redirect('visitor-list')
    return render(request, 'visitors/entry.html', {'form': form})


@role_required(UserProfile.SECURITY)
def visitor_list(request):
    return render(request, 'visitors/list.html', {
        'visitors': Visitor.objects.select_related('host_student')[:100]})


@role_required(UserProfile.SECURITY)
@require_POST
def log_exit(request, pk):
    visitor = get_object_or_404(Visitor, pk=pk)
    if visitor.is_inside:
        visitor.exit_time = timezone.now()
        visitor.save(update_fields=['exit_time'])
        messages.success(request, 'Visitor exit recorded.')
    else:
        messages.error(request, 'Exit already recorded.')
    return redirect('visitor-list')
