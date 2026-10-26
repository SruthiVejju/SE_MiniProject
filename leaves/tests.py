import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from core.models import Notification, UserProfile
from core.testutils import make_user

from .models import LeaveRequest
from .services import decide_leave


def payload(**over):
    today = timezone.localdate()
    data = {'destination': 'Mysuru', 'from_date': today + datetime.timedelta(days=1),
            'to_date': today + datetime.timedelta(days=2), 'reason': 'Family function at home'}
    data.update(over)
    return data


class LeaveBase(TestCase):
    def setUp(self):
        self.student = make_user('stu', UserProfile.STUDENT, 'A')
        self.warden_a = make_user('wardenA', UserProfile.WARDEN, 'A')
        self.warden_b = make_user('wardenB', UserProfile.WARDEN, 'B')
        self.client.force_login(self.student)


class SubmitLeaveTests(LeaveBase):
    def test_valid_request_stored_and_routed_to_block_warden(self):
        resp = self.client.post(reverse('leave-submit'), payload())
        self.assertRedirects(resp, reverse('leave-mine'))
        leave = LeaveRequest.objects.get()
        self.assertEqual(leave.warden, self.warden_a)
        self.assertEqual(leave.block, 'A')
        self.assertEqual(leave.status, LeaveRequest.PENDING)
        self.assertTrue(Notification.objects.filter(user=self.warden_a).exists())

    def test_required_fields(self):
        resp = self.client.post(reverse('leave-submit'), {})
        self.assertEqual(resp.status_code, 200)
        for f in ('destination', 'from_date', 'to_date', 'reason'):
            self.assertIn(f, resp.context['form'].errors)
        self.assertEqual(LeaveRequest.objects.count(), 0)

    def test_to_before_from_rejected(self):
        today = timezone.localdate()
        resp = self.client.post(reverse('leave-submit'), payload(
            from_date=today + datetime.timedelta(days=3), to_date=today + datetime.timedelta(days=1)))
        self.assertIn('to_date', resp.context['form'].errors)

    def test_past_from_date_rejected(self):
        resp = self.client.post(reverse('leave-submit'), payload(
            from_date=timezone.localdate() - datetime.timedelta(days=1)))
        self.assertIn('from_date', resp.context['form'].errors)

    def test_short_reason_rejected(self):
        resp = self.client.post(reverse('leave-submit'), payload(reason='short'))
        self.assertIn('reason', resp.context['form'].errors)

    def test_xss_payload_sanitised_and_escaped(self):
        self.client.post(reverse('leave-submit'), payload(
            destination='<script>alert(1)</script>Goa', reason='<img src=x onerror=alert(1)>trip back home'))
        leave = LeaveRequest.objects.get()
        self.assertNotIn('<', leave.destination + leave.reason)
        self.assertNotContains(self.client.get(reverse('leave-mine')), '<script>alert')

    def test_sql_injection_treated_as_data(self):
        self.client.post(reverse('leave-submit'), payload(destination="x'; DROP TABLE leaves_leaverequest;--"))
        self.assertEqual(LeaveRequest.objects.count(), 1)

    def test_student_without_warden_still_stored(self):
        s = make_user('stuC', UserProfile.STUDENT, 'Z')
        self.client.force_login(s)
        self.client.post(reverse('leave-submit'), payload())
        self.assertIsNone(LeaveRequest.objects.get().warden)

    def test_only_students_can_submit(self):
        self.client.force_login(self.warden_a)
        self.assertEqual(self.client.get(reverse('leave-submit')).status_code, 403)

    def test_my_requests_only_lists_own(self):
        other = make_user('stu2', UserProfile.STUDENT, 'A')
        LeaveRequest.objects.create(student=other, block='A', destination='Hidden', **{
            k: v for k, v in payload().items() if k != 'destination'})
        self.assertNotContains(self.client.get(reverse('leave-mine')), 'Hidden')


class DecideLeaveTests(LeaveBase):
    def setUp(self):
        super().setUp()
        self.client.post(reverse('leave-submit'), payload())
        self.leave = LeaveRequest.objects.get()
        self.client.force_login(self.warden_a)

    def test_approve_saves_decision_and_notifies_within_a_minute(self):
        self.client.post(reverse('leave-decide', args=[self.leave.pk]), {'action': 'approve'})
        self.leave.refresh_from_db()
        self.assertEqual(self.leave.status, LeaveRequest.APPROVED)
        self.assertEqual(self.leave.decided_by, self.warden_a)
        note = Notification.objects.get(user=self.student)
        self.assertLess((note.created_at - self.leave.decided_at).total_seconds(), 60)
        self.assertIn('approved', note.message)

    def test_reject(self):
        self.client.post(reverse('leave-decide', args=[self.leave.pk]), {'action': 'reject'})
        self.leave.refresh_from_db()
        self.assertEqual(self.leave.status, LeaveRequest.REJECTED)

    def test_cannot_decide_twice(self):
        url = reverse('leave-decide', args=[self.leave.pk])
        self.client.post(url, {'action': 'approve'})
        self.client.post(url, {'action': 'reject'})
        self.leave.refresh_from_db()
        self.assertEqual(self.leave.status, LeaveRequest.APPROVED)
        with self.assertRaises(ValueError):
            decide_leave(self.leave, self.warden_a, True)

    def test_invalid_action_ignored(self):
        self.client.post(reverse('leave-decide', args=[self.leave.pk]), {'action': 'bogus'})
        self.leave.refresh_from_db()
        self.assertEqual(self.leave.status, LeaveRequest.PENDING)

    def test_other_block_warden_forbidden(self):
        self.client.force_login(self.warden_b)
        resp = self.client.post(reverse('leave-decide', args=[self.leave.pk]), {'action': 'approve'})
        self.assertEqual(resp.status_code, 403)

    def test_student_cannot_decide(self):
        self.client.force_login(self.student)
        resp = self.client.post(reverse('leave-decide', args=[self.leave.pk]), {'action': 'approve'})
        self.assertEqual(resp.status_code, 403)

    def test_get_not_allowed(self):
        self.assertEqual(self.client.get(reverse('leave-decide', args=[self.leave.pk])).status_code, 405)

    def test_pending_list_scoped_to_block(self):
        self.assertContains(self.client.get(reverse('leave-pending')), 'Mysuru')
        self.client.force_login(self.warden_b)
        self.assertNotContains(self.client.get(reverse('leave-pending')), 'Mysuru')

    def test_str(self):
        self.assertIn('Mysuru', str(self.leave))
