# Performance Optimization Guide

This document outlines performance optimization strategies and best practices for SCIMS.

## Table of Contents

- [Database Optimization](#database-optimization)
- [Caching Strategy](#caching-strategy)
- [Query Optimization](#query-optimization)
- [Frontend Optimization](#frontend-optimization)
- [API Response Optimization](#api-response-optimization)
- [Monitoring & Profiling](#monitoring--profiling)

## Database Optimization

### Indexing Strategy

Critical indexes are defined in migrations. Key indexes include:

- **Item Stocks**: `(item_id, location_id)` unique, `(location_id)` for location queries
- **Crafts**: `(status, organization_id)` for filtering active crafts
- **Item History**: `(item_id, timestamp DESC)` for audit trails
- **Blueprints**: `(output_item_id)` for finding blueprints by output
- **Usage Events**: `(user_id, timestamp DESC)` for analytics

### Query Optimization Techniques

1. **Use Eager Loading**

   Avoid N+1 queries by using `joinedload` or `selectinload`:

   ```python
   from sqlalchemy.orm import joinedload
   
   # Good: Eager load relationships
   goals = db.query(Goal).options(
       joinedload(Goal.goal_items).joinedload(GoalItem.item)
   ).all()
   
   # Bad: Lazy loading (N+1 problem)
   goals = db.query(Goal).all()
   for goal in goals:
       items = goal.goal_items  # Separate query for each goal
   ```

2. **Use Select Statements**

   Only select columns you need:

   ```python
   # Good: Select specific columns
   db.query(Item.id, Item.name).all()
   
   # Less efficient: Select all columns
   db.query(Item).all()
   ```

3. **Batch Operations**

   Use bulk operations for multiple inserts/updates:

   ```python
   # Good: Bulk insert
   db.bulk_insert_mappings(ItemStock, stock_data_list)
   
   # Less efficient: Individual inserts
   for stock_data in stock_data_list:
       db.add(ItemStock(**stock_data))
   ```

4. **Avoid In-Memory Filtering**

   Filter in the database, not in Python:

   ```python
   # Good: Database filtering
   query = db.query(Item).filter(Item.category == "Materials")
   
   # Bad: In-memory filtering
   items = db.query(Item).all()
   filtered = [i for i in items if i.category == "Materials"]
   ```

### Database Connection Pooling

Connection pooling is configured in `app/database.py`:

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,          # Number of connections to maintain
    max_overflow=20,      # Additional connections beyond pool_size
    pool_pre_ping=True,   # Verify connections before using
    pool_recycle=3600,    # Recycle connections after 1 hour
)
```

**Tuning Guidelines:**
- `pool_size`: Start with 5-10, increase based on concurrent requests
- `max_overflow`: Typically 2x pool_size
- `pool_recycle`: Set to less than database connection timeout

## Caching Strategy

### Redis Caching

Redis is used for:
- **Public Commons**: 1-hour cache for public entity lists
- **Rate Limiting**: Per-user/IP request counters
- **Session Data**: (if implemented)

### Cache Keys

Use consistent cache key patterns:

```python
# Public commons cache
cache_key_public_items(tag=None, search=None, skip=0, limit=50)
# Returns: "public:items:tag:None:search:None:skip:0:limit:50"

# Rate limiting
rate_limit_key = f"rate_limit:{client_id}:{path}:{minute}"
```

### Cache Invalidation

Invalidate cache when data changes:

```python
# When approving a commons submission
invalidate_public_cache(entity_type="item")
```

### Caching Best Practices

1. **Cache Frequently Accessed Data**
   - Public commons entities
   - Popular blueprints
   - Canonical locations

2. **Set Appropriate TTLs**
   - Public data: 1 hour
   - User-specific: 5-15 minutes
   - Real-time data: Don't cache

3. **Handle Cache Misses Gracefully**
   - Always have a fallback to database
   - Don't fail if cache is unavailable

## Query Optimization

### Common Performance Issues

1. **N+1 Query Problem**

   **Problem:**
   ```python
   crafts = db.query(Craft).all()
   for craft in crafts:
       blueprint = craft.blueprint  # Separate query for each craft
   ```

   **Solution:**
   ```python
   from sqlalchemy.orm import joinedload
   crafts = db.query(Craft).options(joinedload(Craft.blueprint)).all()
   ```

2. **Missing Indexes**

   Check slow queries and add indexes:
   ```sql
   CREATE INDEX idx_item_stocks_location ON item_stocks(location_id);
   ```

3. **Inefficient Joins**

   Use appropriate join types:
   ```python
   # Use inner join when you need both sides
   query = db.query(ItemStock).join(Item).filter(Item.category == "Materials")
   
   # Use outer join when one side is optional
   query = db.query(Item).outerjoin(ItemStock)
   ```

### Query Profiling

Enable SQL query logging in development:

```python
# In app/database.py
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Log all SQL queries
)
```

Use PostgreSQL's `EXPLAIN ANALYZE`:

```sql
EXPLAIN ANALYZE
SELECT * FROM item_stocks 
WHERE location_id = '...' 
ORDER BY item_id;
```

## Frontend Optimization

### Bundle Optimization

1. **Code Splitting**

   Use React lazy loading:

   ```typescript
   const InventoryPage = lazy(() => import('./pages/InventoryPage'));
   ```

2. **Tree Shaking**

   Import only what you need:

   ```typescript
   // Good
   import { Button } from '@blueprintjs/core';
   
   // Less efficient
   import * as Blueprint from '@blueprintjs/core';
   ```

3. **Asset Optimization**

   - Compress images
   - Use WebP format when possible
   - Lazy load images
   - Use CDN for static assets

### React Optimization

1. **Memoization**

   ```typescript
   const MemoizedComponent = memo(ExpensiveComponent);
   ```

2. **useMemo and useCallback**

   ```typescript
   const expensiveValue = useMemo(() => computeExpensiveValue(a, b), [a, b]);
   const handleClick = useCallback(() => doSomething(id), [id]);
   ```

3. **Virtual Scrolling**

   For long lists, use virtual scrolling libraries.

## API Response Optimization

### Pagination

Always use pagination for list endpoints:

```python
@router.get("/items")
async def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    ...
):
    # Limit prevents large responses
    items = query.offset(skip).limit(limit).all()
```

### Response Compression

Enable gzip compression in Nginx:

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
gzip_min_length 1000;
```

### Field Selection

Allow clients to select specific fields:

```python
@router.get("/items")
async def list_items(
    fields: Optional[str] = Query(None, description="Comma-separated field list"),
    ...
):
    # Return only requested fields
```

## Monitoring & Profiling

### Application Performance Monitoring

1. **Response Time Tracking**

   Add timing middleware:

   ```python
   @app.middleware("http")
   async def add_process_time_header(request: Request, call_next):
       start_time = time.time()
       response = await call_next(request)
       process_time = time.time() - start_time
       response.headers["X-Process-Time"] = str(process_time)
       return response
   ```

2. **Database Query Monitoring**

   Log slow queries:

   ```python
   if query_time > 1.0:  # 1 second
       logger.warning(f"Slow query: {query} took {query_time}s")
   ```

3. **Memory Usage**

   Monitor memory usage in production:
   - Use tools like Prometheus + Grafana
   - Set up alerts for high memory usage

### Profiling Tools

1. **Python Profiling**

   ```bash
   # cProfile
   python -m cProfile -o profile.stats app/main.py
   
   # py-spy (sampling profiler)
   py-spy record -o profile.svg -- python app/main.py
   ```

2. **Database Profiling**

   ```sql
   -- Enable query logging
   SET log_min_duration_statement = 1000;  -- Log queries > 1s
   ```

3. **Frontend Profiling**

   - Chrome DevTools Performance tab
   - React DevTools Profiler
   - Lighthouse for performance audits

## Performance Benchmarks

### Target Metrics

- **API Response Time**: <200ms (p95)
- **Database Query Time**: <100ms (p95)
- **Page Load Time**: <2 seconds
- **Time to Interactive**: <3 seconds

### Load Testing

See [Load Testing Guide](load-testing.md) for detailed instructions.

## Best Practices

1. **Measure First**
   - Profile before optimizing
   - Identify actual bottlenecks
   - Don't optimize prematurely

2. **Optimize Incrementally**
   - Make one change at a time
   - Measure impact
   - Keep what works

3. **Monitor Continuously**
   - Set up performance monitoring
   - Track metrics over time
   - Alert on degradation

4. **Test Under Load**
   - Use realistic data volumes
   - Test with expected concurrent users
   - Identify breaking points

---

For more information:
- [Database Schema](database-schema.md)
- [Load Testing Guide](load-testing.md)
- [Deployment Guide](../deployment/README.md)

