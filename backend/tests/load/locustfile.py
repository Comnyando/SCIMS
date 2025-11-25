"""
Locust load testing file for SCIMS API.

Usage:
    locust -f tests/load/locustfile.py --host=http://localhost:8000

Or headless:
    locust -f tests/load/locustfile.py \
      --host=http://localhost:8000 \
      --users=100 \
      --spawn-rate=10 \
      --run-time=5m \
      --headless \
      --html=load_test_report.html
"""

import random
import string
from locust import HttpUser, task, between


class SCIMSUser(HttpUser):
    """
    Simulated user for load testing SCIMS API.
    
    Simulates typical user behavior:
    - Browsing items and inventory
    - Viewing blueprints
    - Checking crafts
    - Accessing public commons
    """
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Called when a user starts. Register and get token."""
        email = f"loadtest_{random.randint(10000, 99999)}@example.com"
        password = "".join(random.choices(string.ascii_letters + string.digits, k=16))
        username = f"loaduser_{random.randint(10000, 99999)}"
        
        # Register new user
        response = self.client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "username": username,
                "password": password,
            },
            name="Register User",
        )
        
        if response.status_code == 201:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
            self.user_id = response.json()["user"]["id"]
        else:
            # Registration failed, try login with existing credentials
            # For load testing, we'll just proceed without token
            self.token = None
            self.headers = {}
            self.user_id = None
    
    @task(5)
    def list_items(self):
        """List items - most common read operation."""
        self.client.get("/api/v1/items", headers=self.headers, name="List Items")
    
    @task(4)
    def list_inventory(self):
        """List inventory - common operation."""
        self.client.get("/api/v1/inventory", headers=self.headers, name="List Inventory")
    
    @task(3)
    def list_blueprints(self):
        """List blueprints."""
        self.client.get("/api/v1/blueprints", headers=self.headers, name="List Blueprints")
    
    @task(2)
    def list_crafts(self):
        """List crafts."""
        self.client.get("/api/v1/crafts", headers=self.headers, name="List Crafts")
    
    @task(2)
    def list_locations(self):
        """List locations."""
        self.client.get("/api/v1/locations", headers=self.headers, name="List Locations")
    
    @task(1)
    def get_public_items(self):
        """Access public commons - no auth required."""
        self.client.get("/public/items", name="Public Items")
    
    @task(1)
    def get_public_recipes(self):
        """Access public recipes."""
        self.client.get("/public/recipes", name="Public Recipes")
    
    @task(1)
    def search_public(self):
        """Search public commons."""
        search_terms = ["quantum", "weapon", "component", "material"]
        term = random.choice(search_terms)
        self.client.get(
            f"/public/search?q={term}",
            name="Search Public Commons",
        )
    
    @task(1)
    def get_current_user(self):
        """Get current user info."""
        if self.token:
            self.client.get("/api/v1/auth/me", headers=self.headers, name="Get Current User")
    
    @task(1)
    def health_check(self):
        """Health check endpoint."""
        self.client.get("/health", name="Health Check")


class ReadOnlyUser(HttpUser):
    """
    Read-only user for testing public endpoints.
    
    Simulates anonymous or unauthenticated users.
    """
    
    wait_time = between(2, 5)
    
    @task(10)
    def get_public_items(self):
        """Access public items."""
        self.client.get("/public/items", name="Public Items")
    
    @task(5)
    def get_public_recipes(self):
        """Access public recipes."""
        self.client.get("/public/recipes", name="Public Recipes")
    
    @task(3)
    def get_public_locations(self):
        """Access public locations."""
        self.client.get("/public/locations", name="Public Locations")
    
    @task(2)
    def search_public(self):
        """Search public commons."""
        search_terms = ["quantum", "weapon", "component"]
        term = random.choice(search_terms)
        self.client.get(f"/public/search?q={term}", name="Search Public")
    
    @task(1)
    def health_check(self):
        """Health check."""
        self.client.get("/health", name="Health Check")

