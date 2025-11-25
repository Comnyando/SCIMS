/**
 * k6 load testing script for SCIMS API
 *
 * Usage:
 *   k6 run tests/load/load-test.js
 *
 * With options:
 *   k6 run --vus=100 --duration=5m tests/load/load-test.js
 */

import http from "k6/http";
import { check, sleep } from "k6";
import { Rate, Trend } from "k6/metrics";

const errorRate = new Rate("errors");
const responseTime = new Trend("response_time");

export const options = {
  stages: [
    { duration: "2m", target: 50 }, // Ramp up to 50 users over 2 minutes
    { duration: "5m", target: 50 }, // Stay at 50 users for 5 minutes
    { duration: "2m", target: 100 }, // Ramp up to 100 users over 2 minutes
    { duration: "5m", target: 100 }, // Stay at 100 users for 5 minutes
    { duration: "2m", target: 150 }, // Ramp up to 150 users
    { duration: "5m", target: 150 }, // Stay at 150 users
    { duration: "2m", target: 0 }, // Ramp down to 0
  ],
  thresholds: {
    http_req_duration: ["p(95)<500", "p(99)<1000"], // 95% < 500ms, 99% < 1000ms
    http_req_failed: ["rate<0.01"], // Error rate < 1%
    errors: ["rate<0.01"],
    "http_req_duration{name:List Items}": ["p(95)<200"],
    "http_req_duration{name:List Inventory}": ["p(95)<300"],
    "http_req_duration{name:Public Items}": ["p(95)<100"],
  },
};

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";

export function setup() {
  // Register a test user and return token
  const email = `loadtest_${Math.floor(Math.random() * 100000)}@example.com`;
  const username = `loaduser_${Math.floor(Math.random() * 100000)}`;
  const password = "testpassword123";

  const registerRes = http.post(
    `${BASE_URL}/api/v1/auth/register`,
    JSON.stringify({
      email: email,
      username: username,
      password: password,
    }),
    {
      headers: { "Content-Type": "application/json" },
      tags: { name: "Register User" },
    }
  );

  if (registerRes.status === 201) {
    return {
      token: registerRes.json().access_token,
      userId: registerRes.json().user.id,
    };
  }

  // If registration fails, try login (for reusing existing users)
  const loginRes = http.post(
    `${BASE_URL}/api/v1/auth/login`,
    JSON.stringify({
      email: email,
      password: password,
    }),
    {
      headers: { "Content-Type": "application/json" },
      tags: { name: "Login User" },
    }
  );

  if (loginRes.status === 200) {
    return {
      token: loginRes.json().access_token,
      userId: loginRes.json().user.id,
    };
  }

  return { token: null, userId: null };
}

export default function (data) {
  const headers = {
    Authorization: `Bearer ${data.token}`,
    "Content-Type": "application/json",
  };

  // List items (most common operation)
  const itemsRes = http.get(`${BASE_URL}/api/v1/items`, {
    headers: headers,
    tags: { name: "List Items" },
  });
  const itemsCheck = check(itemsRes, {
    "items status 200": (r) => r.status === 200,
  });
  if (!itemsCheck) errorRate.add(1);
  responseTime.add(itemsRes.timings.duration);
  sleep(1);

  // List inventory
  const inventoryRes = http.get(`${BASE_URL}/api/v1/inventory`, {
    headers: headers,
    tags: { name: "List Inventory" },
  });
  check(inventoryRes, {
    "inventory status 200": (r) => r.status === 200,
  }) || errorRate.add(1);
  sleep(1);

  // List blueprints
  const blueprintsRes = http.get(`${BASE_URL}/api/v1/blueprints`, {
    headers: headers,
    tags: { name: "List Blueprints" },
  });
  check(blueprintsRes, {
    "blueprints status 200": (r) => r.status === 200,
  }) || errorRate.add(1);
  sleep(1);

  // List crafts
  const craftsRes = http.get(`${BASE_URL}/api/v1/crafts`, {
    headers: headers,
    tags: { name: "List Crafts" },
  });
  check(craftsRes, {
    "crafts status 200": (r) => r.status === 200,
  }) || errorRate.add(1);
  sleep(1);

  // Public endpoints (no auth required)
  const publicItemsRes = http.get(`${BASE_URL}/public/items`, {
    tags: { name: "Public Items" },
  });
  check(publicItemsRes, {
    "public items status 200": (r) => r.status === 200,
  }) || errorRate.add(1);
  sleep(1);

  // Search public commons
  const searchTerms = ["quantum", "weapon", "component", "material"];
  const term = searchTerms[Math.floor(Math.random() * searchTerms.length)];
  const searchRes = http.get(`${BASE_URL}/public/search?q=${term}`, {
    tags: { name: "Search Public" },
  });
  check(searchRes, {
    "search status 200": (r) => r.status === 200,
  }) || errorRate.add(1);
  sleep(1);

  // Health check
  const healthRes = http.get(`${BASE_URL}/health`, {
    tags: { name: "Health Check" },
  });
  check(healthRes, {
    "health status 200": (r) => r.status === 200,
  }) || errorRate.add(1);
  sleep(1);
}

export function teardown(data) {
  // Cleanup if needed
  // Could delete test users, etc.
}
