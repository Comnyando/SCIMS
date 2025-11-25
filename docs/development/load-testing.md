# Load Testing Guide

Guide for load testing SCIMS using Locust or k6.

## Table of Contents

- [Overview](#overview)
- [Locust Setup](#locust-setup)
- [k6 Setup](#k6-setup)
- [Test Scenarios](#test-scenarios)
- [Running Tests](#running-tests)
- [Interpreting Results](#interpreting-results)
- [Performance Targets](#performance-targets)

## Overview

Load testing helps identify:
- Performance bottlenecks
- Maximum concurrent users
- Response time under load
- Resource usage patterns
- Breaking points

## Locust Setup

### Installation

```bash
pip install locust
```

### Basic Test File

Create `backend/tests/load/locustfile.py`:

```python
from locust import HttpUser, task, between
import random
import string

class SCIMSUser(HttpUser):
    """Simulated user for load testing."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Called when a user starts. Login and get token."""
        # Register or login
        email = f"loadtest_{random.randint(1000, 9999)}@example.com"
        password = "".join(random.choices(string.ascii_letters, k=12))
        
        # Register
        response = self.client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "username": f"user_{random.randint(1000, 9999)}",
                "password": password,
            },
        )
        
        if response.status_code == 201:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            # Try login instead
            response = self.client.post(
                "/api/v1/auth/login",
                json={"email": email, "password": password},
            )
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                self.headers = {"Authorization": f"Bearer {self.token}"}
            else:
                self.token = None
                self.headers = {}
    
    @task(3)
    def list_items(self):
        """List items - most common operation."""
        if self.token:
            self.client.get("/api/v1/items", headers=self.headers)
    
    @task(2)
    def list_inventory(self):
        """List inventory."""
        if self.token:
            self.client.get("/api/v1/inventory", headers=self.headers)
    
    @task(1)
    def list_blueprints(self):
        """List blueprints."""
        if self.token:
            self.client.get("/api/v1/blueprints", headers=self.headers)
    
    @task(1)
    def list_crafts(self):
        """List crafts."""
        if self.token:
            self.client.get("/api/v1/crafts", headers=self.headers)
    
    @task(1)
    def get_public_items(self):
        """Access public commons - no auth required."""
        self.client.get("/public/items")
```

### Running Locust

```bash
# Start Locust web UI
cd backend
locust -f tests/load/locustfile.py --host=http://localhost:8000

# Or headless mode
locust -f tests/load/locustfile.py \
  --host=http://localhost:8000 \
  --users=100 \
  --spawn-rate=10 \
  --run-time=5m \
  --headless \
  --html=load_test_report.html
```

## k6 Setup

### Installation

```bash
# Windows (using Chocolatey)
choco install k6

# Or download from https://k6.io/docs/getting-started/installation/
```

### Basic Test File

Create `backend/tests/load/load-test.js`:

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '2m', target: 50 },   // Ramp up to 50 users
    { duration: '5m', target: 50 },   // Stay at 50 users
    { duration: '2m', target: 100 },  // Ramp up to 100 users
    { duration: '5m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% of requests < 500ms
    http_req_failed: ['rate<0.01'],    // Error rate < 1%
    errors: ['rate<0.01'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export function setup() {
  // Register a user and return token
  const registerRes = http.post(`${BASE_URL}/api/v1/auth/register`, JSON.stringify({
    email: `loadtest_${Math.random()}@example.com`,
    username: `user_${Math.random()}`,
    password: 'testpassword123',
  }), {
    headers: { 'Content-Type': 'application/json' },
  });
  
  if (registerRes.status === 201) {
    return { token: registerRes.json().access_token };
  }
  
  return { token: null };
}

export default function(data) {
  const headers = {
    'Authorization': `Bearer ${data.token}`,
    'Content-Type': 'application/json',
  };
  
  // List items
  const itemsRes = http.get(`${BASE_URL}/api/v1/items`, { headers });
  check(itemsRes, {
    'items status 200': (r) => r.status === 200,
  }) || errorRate.add(1);
  
  sleep(1);
  
  // List inventory
  const inventoryRes = http.get(`${BASE_URL}/api/v1/inventory`, { headers });
  check(inventoryRes, {
    'inventory status 200': (r) => r.status === 200,
  }) || errorRate.add(1);
  
  sleep(1);
  
  // Public endpoints (no auth)
  const publicRes = http.get(`${BASE_URL}/public/items`);
  check(publicRes, {
    'public status 200': (r) => r.status === 200,
  }) || errorRate.add(1);
  
  sleep(1);
}

export function teardown(data) {
  // Cleanup if needed
}
```

### Running k6

```bash
# Run test
k6 run backend/tests/load/load-test.js

# With custom base URL
k6 run --env BASE_URL=http://localhost:8000 backend/tests/load/load-test.js

# With more options
k6 run \
  --vus=100 \
  --duration=5m \
  --out json=results.json \
  backend/tests/load/load-test.js
```

## Test Scenarios

### Scenario 1: Normal Load

Simulate typical usage:
- 50-100 concurrent users
- Mix of read and write operations
- Realistic request patterns

### Scenario 2: Peak Load

Simulate peak usage:
- 200-500 concurrent users
- Higher read-to-write ratio
- Burst traffic patterns

### Scenario 3: Stress Test

Find breaking point:
- Gradually increase load
- Monitor for failures
- Identify maximum capacity

### Scenario 4: Spike Test

Test sudden traffic spikes:
- Rapid increase in users
- Monitor recovery time
- Check for cascading failures

## Running Tests

### Pre-Test Checklist

- [ ] Database is populated with test data
- [ ] Redis is running (for rate limiting)
- [ ] Application is running in production-like mode
- [ ] Monitoring is set up
- [ ] Test environment is isolated

### During Tests

Monitor:
- CPU usage
- Memory usage
- Database connections
- Redis connections
- Response times
- Error rates

### Post-Test

- Review results
- Identify bottlenecks
- Document findings
- Plan optimizations

## Interpreting Results

### Key Metrics

1. **Response Time**
   - p50 (median): Typical response time
   - p95: 95% of requests faster than this
   - p99: 99% of requests faster than this

2. **Throughput**
   - Requests per second
   - Successful requests
   - Failed requests

3. **Error Rate**
   - Percentage of failed requests
   - Types of errors
   - When errors occur

### Performance Targets

- **p95 Response Time**: <500ms for most endpoints
- **p99 Response Time**: <1000ms
- **Error Rate**: <1%
- **Throughput**: Handle expected load + 20% headroom

## Performance Targets

### API Endpoints

| Endpoint | Target p95 | Target p99 |
|----------|-----------|------------|
| GET /api/v1/items | <200ms | <500ms |
| GET /api/v1/inventory | <300ms | <800ms |
| POST /api/v1/crafts | <500ms | <1000ms |
| GET /public/items | <100ms | <300ms |

### Database

- Query time: <100ms (p95)
- Connection pool utilization: <80%
- Slow query count: <1% of total

### System Resources

- CPU usage: <70% average
- Memory usage: <80% of available
- Disk I/O: No sustained 100% usage

## Troubleshooting

### High Response Times

1. Check database queries
2. Review N+1 query problems
3. Check Redis connectivity
4. Review application logs

### High Error Rates

1. Check rate limiting
2. Review authentication issues
3. Check database connections
4. Review resource limits

### Memory Leaks

1. Profile memory usage
2. Check for unclosed connections
3. Review caching strategies
4. Monitor over time

---

For more information:
- [Performance Optimization Guide](performance-optimization.md)
- [Deployment Guide](../deployment/README.md)

