import re
import random
from locust import HttpUser, task, between

class ShopperUser(HttpUser):
    wait_time = between(1, 3)
    csrf_token = None
    product_ids = []

    def on_start(self):
        # Grab a session cookie + CSRF token like a real browser would
        resp = self.client.get("/")
        match = re.search(r'name="csrf-token" content="([^"]+)"', resp.text)
        self.csrf_token = match.group(1) if match else None

        # Pull real product IDs instead of guessing
        api_resp = self.client.get("/api/products")
        if api_resp.status_code == 200:
            try:
                self.product_ids = [p["id"] for p in api_resp.json()]
            except ValueError:
                self.product_ids = []

    @task(5)
    def browse_home(self):
        self.client.get("/")

    @task(4)
    def browse_shop(self):
        params = random.choice([
            "", "?sort=price_asc", "?sort=price_desc", "?category=streetwear"
        ])
        self.client.get(f"/shop{params}", name="/shop")

    @task(4)
    def view_product(self):
        if self.product_ids:
            pid = random.choice(self.product_ids)
            self.client.get(f"/product/{pid}", name="/product/[id]")

    @task(2)
    def view_cart(self):
        self.client.get("/cart/")

    @task(1)
    def cart_count(self):
        self.client.get("/cart/count")

    @task(1)
    def add_to_cart(self):
        if not self.product_ids or not self.csrf_token:
            return
        pid = random.choice(self.product_ids)
        self.client.post(
            "/cart/add",
            data={"product_id": pid, "size": "M", "quantity": 1},
            headers={"X-CSRFToken": self.csrf_token},
            name="/cart/add",
        )