
from django.test import TestCase
from django.urls import reverse

from core.models import UserProfile
from core.testutils import make_user

from .forms import AllocationForm
from .models import Allocation, Bed, Room
from .services import AllocationError, allocate_bed

from decimal import Decimal

from fees.models import FeeAccount


class RoomAllocationTests(TestCase):

    def setUp(self):
        self.admin_user = make_user(
            "hostel_admin", UserProfile.ADMIN
        )
        self.student1 = make_user(
            "student1", UserProfile.STUDENT
        )
        self.student2 = make_user(
            "student2", UserProfile.STUDENT
        )
        self.warden = make_user(
            "warden1", UserProfile.WARDEN
        )

        self.room = Room.objects.create(
            block="A",
            room_number="101",
            floor=1
        )

        self.bed1 = Bed.objects.create(
            room=self.room,
            bed_number="1"
        )

        self.bed2 = Bed.objects.create(
            room=self.room,
            bed_number="2"
        )

    def test_admin_can_allocate_available_bed(self):
        allocation = allocate_bed(
            self.student1,
            self.bed1.pk
        )

        self.assertEqual(
            allocation.student,
            self.student1
        )
        self.assertEqual(
            allocation.bed,
            self.bed1
        )

        self.bed1.refresh_from_db()
        self.assertTrue(self.bed1.is_occupied)

    def test_occupied_bed_cannot_be_allocated_again(self):
        allocate_bed(self.student1, self.bed1.pk)

        with self.assertRaises(AllocationError):
            allocate_bed(self.student2, self.bed1.pk)

        self.assertEqual(
            Allocation.objects.filter(
                bed=self.bed1,
                is_active=True
            ).count(),
            1
        )

    def test_student_cannot_receive_two_active_beds(self):
        allocate_bed(self.student1, self.bed1.pk)

        with self.assertRaises(AllocationError):
            allocate_bed(self.student1, self.bed2.pk)

    def test_warden_cannot_be_allocated_a_bed(self):
        with self.assertRaises(AllocationError):
            allocate_bed(self.warden, self.bed1.pk)

    def test_admin_can_access_allocation_page(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(
            reverse("hostel:allocate")
        )

        self.assertEqual(response.status_code, 200)

    def test_student_cannot_access_allocation_page(self):
        self.client.force_login(self.student1)

        response = self.client.get(
            reverse("hostel:allocate")
        )

        self.assertEqual(response.status_code, 403)

    def test_admin_can_allocate_using_form(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse("hostel:allocate"),
            {
                "student": self.student1.pk,
                "bed": self.bed1.pk
            }
        )

        self.assertEqual(response.status_code, 302)

        self.assertTrue(
            Allocation.objects.filter(
                student=self.student1,
                bed=self.bed1,
                is_active=True
            ).exists()
        )

    def test_allocated_bed_removed_from_available_choices(self):
        allocate_bed(self.student1, self.bed1.pk)

        form = AllocationForm()

        self.assertFalse(
            form.fields["bed"].queryset.filter(
                pk=self.bed1.pk
            ).exists()
        )

    def test_duplicate_room_is_rejected(self):
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            Room.objects.create(
                block="A",
                room_number="101",
                floor=1
            )

    def test_allocation_is_associated_with_correct_student(self):
        allocate_bed(self.student1, self.bed1.pk)

        allocation = Allocation.objects.get(
            bed=self.bed1,
            is_active=True
        )

        self.assertEqual(
            allocation.student.username,
            "student1"
        )


class StudentDashboardTests(TestCase):

    def setUp(self):
        self.student = make_user(
            "dashboard_student",
            UserProfile.STUDENT
        )

        self.other_student = make_user(
            "other_student",
            UserProfile.STUDENT
        )

        self.room = Room.objects.create(
            block="B",
            room_number="202",
            floor=2
        )

        self.bed = Bed.objects.create(
            room=self.room,
            bed_number="1",
            is_occupied=True
        )

        self.allocation = Allocation.objects.create(
            student=self.student,
            bed=self.bed,
            is_active=True
        )

        self.fee_account = FeeAccount.objects.create(
            student=self.student,
            total_fee=Decimal("50000.00"),
            amount_paid=Decimal("30000.00")
        )

    def test_student_can_view_own_dashboard(self):
        self.client.force_login(self.student)

        response = self.client.get(
            reverse("hostel:student_dashboard")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "B")
        self.assertContains(response, "202")
        self.assertContains(response, "1")

    def test_dashboard_displays_correct_fee_dues(self):
        self.client.force_login(self.student)

        response = self.client.get(
            reverse("hostel:student_dashboard")
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["outstanding_dues"],
            Decimal("20000.00")
        )

    def test_student_without_allocation_can_view_dashboard(self):
        self.client.force_login(self.other_student)

        response = self.client.get(
            reverse("hostel:student_dashboard")
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["allocation"])

    def test_student_without_fee_account_can_view_dashboard(self):
        self.client.force_login(self.other_student)

        response = self.client.get(
            reverse("hostel:student_dashboard")
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["fee_account"])
        self.assertIsNone(response.context["outstanding_dues"])

    def test_admin_cannot_access_student_dashboard(self):
        admin_user = make_user(
            "dashboard_admin",
            UserProfile.ADMIN
        )

        self.client.force_login(admin_user)

        response = self.client.get(
            reverse("hostel:student_dashboard")
        )

        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_user_is_redirected_to_login(self):
        response = self.client.get(
            reverse("hostel:student_dashboard")
        )

        self.assertEqual(response.status_code, 302)

    def test_student_cannot_view_another_students_allocation(self):
        self.client.force_login(self.other_student)

        response = self.client.get(
            reverse("hostel:student_dashboard")
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["allocation"])
        self.assertNotContains(response, "dashboard_student")
