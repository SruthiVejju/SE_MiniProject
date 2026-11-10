
import os
from locust import HttpUser, task, between


class StudentDashboardUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        session_id = os.environ.get("LOADTEST_SESSION")

        if not session_id:
            raise Exception("LOADTEST_SESSION is not configured")

        self.client.cookies.set("sessionid", session_id)

    @task
    def view_dashboard(self):
        with self.client.get(
            "/hostel/my-room/",
            name="Student Dashboard",
            catch_response=True
        ) as response:

            if response.status_code != 200:
                response.failure(
                    f"Dashboard returned HTTP {response.status_code}"
                )
