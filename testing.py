from locust import HttpUser, task

class MyAppUser(HttpUser):
    @task
    def get_request(self):
        self.client.get("/request/abc")
