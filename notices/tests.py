from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import Client, TestCase
from django.urls import reverse

from core.audit import NOTICE_PUBLISHED
from core.models import AuditLog, Notification, UserProfile
from hostel.models import Room
from .models import Notice

User = get_user_model()


class NoticeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.password = 'Pass@12345'

        # Admin user
        self.admin = User.objects.create_user(username='admin_notice', password=self.password)
        UserProfile.objects.create(user=self.admin, role=UserProfile.ADMIN)

        # Warden user
        self.warden = User.objects.create_user(username='warden_notice', password=self.password)
        UserProfile.objects.create(user=self.warden, role=UserProfile.WARDEN, block='A')

        # Student in Block A
        self.student_a = User.objects.create_user(username='student_a', password=self.password)
        UserProfile.objects.create(user=self.student_a, role=UserProfile.STUDENT, block='A')

        # Student in Block B
        self.student_b = User.objects.create_user(username='student_b', password=self.password)
        UserProfile.objects.create(user=self.student_b, role=UserProfile.STUDENT, block='B')

        # Create room blocks for form choices
        Room.objects.create(block='A', room_number='101')
        Room.objects.create(block='B', room_number='201')

    def test_admin_can_publish_general_notice(self):
        self.client.login(username='admin_notice', password=self.password)
        payload = {
            'title': 'General Hostel Meeting',
            'content': 'All residents must attend the general meeting on Friday at 6 PM.',
            'target_block': '',
        }
        res = self.client.post(reverse('notices:create'), payload)
        self.assertEqual(res.status_code, 302)

        notice = Notice.objects.filter(title='General Hostel Meeting').first()
        self.assertIsNotNone(notice)
        self.assertTrue(notice.is_general)
        self.assertEqual(notice.posted_by, self.admin)

        # Audit log verified
        audit = AuditLog.objects.filter(action=NOTICE_PUBLISHED).first()
        self.assertIsNotNone(audit)
        self.assertEqual(audit.actor, self.admin)

        # Both students should receive in-app notifications
        self.assertTrue(Notification.objects.filter(user=self.student_a).exists())
        self.assertTrue(Notification.objects.filter(user=self.student_b).exists())

    def test_admin_can_publish_block_specific_notice(self):
        self.client.login(username='admin_notice', password=self.password)
        payload = {
            'title': 'Block A Water Tank Cleaning',
            'content': 'Water supply in Block A will be paused from 10 AM to 1 PM.',
            'target_block': 'A',
        }
        res = self.client.post(reverse('notices:create'), payload)
        self.assertEqual(res.status_code, 302)

        notice = Notice.objects.filter(title='Block A Water Tank Cleaning').first()
        self.assertIsNotNone(notice)
        self.assertFalse(notice.is_general)
        self.assertEqual(notice.target_block, 'A')

        # Only student in Block A gets notification
        self.assertTrue(Notification.objects.filter(user=self.student_a).exists())
        self.assertFalse(Notification.objects.filter(user=self.student_b).exists())

    def test_student_visibility_rules(self):
        # Create 1 general notice and 1 Block A notice
        n_gen = Notice.objects.create(
            title='General Circular',
            content='Library hours extended.',
            target_block='',
            posted_by=self.admin
        )
        n_a = Notice.objects.create(
            title='Block A Notice',
            content='Lift maintenance scheduled.',
            target_block='A',
            posted_by=self.admin
        )

        # Student A sees both
        self.client.login(username='student_a', password=self.password)
        res_a = self.client.get(reverse('notices:list'))
        self.assertEqual(res_a.status_code, 200)
        self.assertContains(res_a, 'General Circular')
        self.assertContains(res_a, 'Block A Notice')

        # Student B only sees General Circular
        self.client.login(username='student_b', password=self.password)
        res_b = self.client.get(reverse('notices:list'))
        self.assertEqual(res_b.status_code, 200)
        self.assertContains(res_b, 'General Circular')
        self.assertNotContains(res_b, 'Block A Notice')

        # Student B attempting to directly access Block A notice detail gets 403
        res_b_detail = self.client.get(reverse('notices:detail', args=[n_a.pk]))
        self.assertEqual(res_b_detail.status_code, 403)

        # Student A can access detail
        self.client.login(username='student_a', password=self.password)
        res_a_detail = self.client.get(reverse('notices:detail', args=[n_a.pk]))
        self.assertEqual(res_a_detail.status_code, 200)

    def test_student_cannot_publish_notice(self):
        self.client.login(username='student_a', password=self.password)
        res = self.client.get(reverse('notices:create'))
        self.assertEqual(res.status_code, 403)

        res_post = self.client.post(reverse('notices:create'), {
            'title': 'Hacked Notice',
            'content': 'Unauthorized content here.',
            'target_block': '',
        })
        self.assertEqual(res_post.status_code, 403)
        self.assertFalse(Notice.objects.filter(title='Hacked Notice').exists())

    def test_notice_search(self):
        Notice.objects.create(
            title='Sports Day Tournament',
            content='Football and basketball trials.',
            target_block='',
            posted_by=self.admin
        )
        Notice.objects.create(
            title='Exam Hall Rules',
            content='Strict silence required.',
            target_block='',
            posted_by=self.admin
        )

        self.client.login(username='student_a', password=self.password)
        res = self.client.get(reverse('notices:list') + '?q=Sports')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Sports Day Tournament')
        self.assertNotContains(res, 'Exam Hall Rules')
