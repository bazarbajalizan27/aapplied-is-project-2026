from locust import HttpUser, task, between


class WarehouseUser(HttpUser):
    wait_time = between(0.5, 1.5)

    @task(3)
    def list_items(self):
        self.client.get("/items")

    @task(1)
    def search_items(self):
        self.client.get("/items", params={"search": "Laptop"})

    @task(1)
    def get_one(self):
        self.client.get("/items/1")