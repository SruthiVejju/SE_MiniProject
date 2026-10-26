from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from core.models import UserProfile
from core.testutils import make_user

from .models import FeeAccount, FeePayment


class FeeTests(TestCase):
    def setUp(self):
        self.admin = make_user('adm', UserProfile.ADMIN)
        self.student = make_user('stu', UserProfile.STUDENT)
        self.account = FeeAccount.objects.create(student=self.student, total_fee=Decimal('10000'))
        self.client.force_login(self.admin)

    def pay(self, **over):
        data = {'account': self.account.pk, 'amount': '2500', 'mode': 'cash', 'reference': ''}
        data.update(over)
        return self.client.post(reverse('fee-record'), data)

    def test_cash_payment_updates_fee_record_and_issues_receipt(self):
        resp = self.pay()
        p = FeePayment.objects.get()
        self.assertRedirects(resp, reverse('fee-receipt', args=[p.pk]))
        self.account.refresh_from_db()
        self.assertEqual(self.account.amount_paid, Decimal('2500'))
        self.assertEqual(self.account.due, Decimal('7500'))
        self.assertTrue(p.receipt_number.startswith('RCPT-'))
        self.assertEqual(p.recorded_by, self.admin)
        self.assertIn('RCPT-', str(p))
        self.assertIn('due', str(self.account))

    def test_online_payment_requires_reference(self):
        resp = self.pay(mode='online')
        self.assertIn('reference', resp.context['form'].errors)
        self.assertEqual(FeePayment.objects.count(), 0)

    def test_online_payment_with_reference(self):
        self.pay(mode='online', reference='TXN-12345')
        self.assertEqual(FeePayment.objects.get().reference, 'TXN-12345')

    def test_reference_rejects_special_characters(self):
        resp = self.pay(mode='online', reference="x'; DROP--")
        self.assertIn('reference', resp.context['form'].errors)

    def test_receipt_numbers_unique(self):
        self.pay()
        self.pay()
        numbers = list(FeePayment.objects.values_list('receipt_number', flat=True))
        self.assertEqual(len(set(numbers)), 2)

    def test_overpayment_rejected(self):
        resp = self.pay(amount='10001')
        self.assertContains(resp, 'exceeds the outstanding due')
        self.assertEqual(FeePayment.objects.count(), 0)

    def test_non_positive_amount_rejected(self):
        for amt in ('0', '-5'):
            self.assertIn('amount', self.pay(amount=amt).context['form'].errors)

    def test_service_rejects_non_positive_amount(self):
        from .services import PaymentError, record_payment
        with self.assertRaises(PaymentError):
            record_payment(self.account.pk, 0, 'cash', '', self.admin)

    def test_receipt_page_and_access_control(self):
        self.pay()
        p = FeePayment.objects.get()
        self.assertContains(self.client.get(reverse('fee-receipt', args=[p.pk])), p.receipt_number)
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(reverse('fee-receipt', args=[p.pk])).status_code, 403)
        self.assertEqual(self.client.post(reverse('fee-record'), {}).status_code, 403)
