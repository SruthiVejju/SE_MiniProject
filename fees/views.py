from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from core.models import UserProfile
from core.permissions import role_required

from .forms import PaymentForm
from .models import FeePayment
from .services import PaymentError, record_payment


@role_required(UserProfile.ADMIN)
def record(request):
    form = PaymentForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        try:
            payment = record_payment(
                data['account'].pk, data['amount'], data['mode'],
                data['reference'], request.user)
        except PaymentError as exc:
            form.add_error(None, str(exc))
        else:
            messages.success(request, f'Payment recorded. Receipt {payment.receipt_number}.')
            return redirect('fee-receipt', pk=payment.pk)
    return render(request, 'fees/record.html', {'form': form})


@role_required(UserProfile.ADMIN)
def receipt(request, pk):
    payment = get_object_or_404(FeePayment.objects.select_related('account__student'), pk=pk)
    return render(request, 'fees/receipt.html', {'payment': payment})
