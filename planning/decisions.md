# Architecture Decisions Log

This document records significant architectural decisions, their context, and rationale.

---

## ADR-001: FastAPI over Flask/Django

**Status:** Accepted  
**Date:** 10/2025
**Context:** Need a Python web framework for the backend API that supports high performance and modern Python features.

**Decision:** Use FastAPI as the primary backend framework.

**Rationale:**
- Built-in async/await support for high concurrency (critical for inventory management with multiple users)
- Automatic OpenAPI/Swagger documentation generation
- Type safety with Pydantic models (catches errors early)
- Modern Python features (type hints, dataclasses)
- Excellent performance benchmarks
- Growing ecosystem and community

**Alternatives Considered:**
- **Flask:** Simpler but lacks async support, requires more boilerplate
- **Django:** Too opinionated, heavier weight, REST framework adds complexity
- **Tornado:** Lower level, less ecosystem support

**Consequences:**
- Positive: Fast development, automatic docs, type safety
- Negative: Smaller ecosystem than Django, team needs to learn async patterns

---

## ADR-002: PostgreSQL over MongoDB/MySQL

**Status:** Accepted  
**Date:** 10/2025 
**Context:** Need a robust database for transactional inventory data with complex relationships.

**Decision:** Use PostgreSQL as the primary database.

**Rationale:**
- ACID compliance essential for inventory transactions (no double-spending)
- Excellent support for complex queries and joins
- JSONB support provides flexibility where needed (metadata fields)
- Strong consistency guarantees
- Mature ecosystem and tooling
- Proven scalability with proper indexing
- Full-text search capabilities built-in

**Alternatives Considered:**
- **MongoDB:** Better for document storage but weaker consistency guarantees
- **MySQL:** Similar to PostgreSQL but JSON support is less mature
- **SQLite:** Not suitable for multi-user production use

**Consequences:**
- Positive: Strong data integrity, flexible schema with JSONB
- Negative: Requires proper schema design, migration management (Alembic)

---

## ADR-003: React with TypeScript over Vue/Angular

**Status:** Accepted  
**Date:** 10/2025
**Context:** Need a modern, user-friendly frontend framework with strong ecosystem support.

**Decision:** Use React 18+ with TypeScript for the frontend.

**Rationale:**
- Largest ecosystem and community (more libraries, solutions)
- Strong TypeScript support (type safety)
- Component-based architecture matches inventory/item models well
- Excellent performance with React 18 features
- Better job market alignment (if hiring developers later)
- Large pool of React developers

**Alternatives Considered:**
- **Vue 3:** Simpler learning curve but smaller ecosystem
- **Angular:** Too opinionated, heavier weight, overkill for this project
- **Svelte:** Promising but smaller ecosystem

**Consequences:**
- Positive: Rich ecosystem, strong community support
- Negative: Larger bundle size, steeper learning curve for beginners

---

## ADR-004: Docker Compose over Kubernetes (Initially)

**Status:** Accepted  
**Date:** 10/2025
**Context:** Need container orchestration that's simple for personal server deployment.

**Decision:** Start with Docker Compose, design for future Kubernetes migration.

**Rationale:**
- Simpler to learn and maintain for single-server deployment
- Lower operational overhead
- Easier debugging and development
- Sufficient for MVP and early stages
- Can migrate to Kubernetes later if needed
- Stateless service design enables easy migration

**Alternatives Considered:**
- **Kubernetes:** More powerful but overkill for MVP, steeper learning curve
- **Docker Swarm:** Middle ground but less popular
- **Nomad:** Less common, smaller ecosystem

**Consequences:**
- Positive: Faster initial setup, easier local development
- Negative: Will need migration work if scaling beyond single server

---

## ADR-005: JWT Authentication over Session-Based

**Status:** Accepted  
**Date:** 10/2025
**Context:** Need stateless authentication that works across multiple services and supports API access.

**Decision:** Use JWT tokens for authentication with short-lived access tokens and refresh tokens.

**Rationale:**
- Stateless (no server-side session storage needed)
- Works well with microservices architecture (if we migrate)
- Supports API key access (for integrations)
- Industry standard approach
- Works well with Redis for token blacklisting (if needed)

**Alternatives Considered:**
- **Session-based:** Simpler but requires session storage, harder to scale
- **OAuth2 (third-party):** Unnecessary complexity for first-party auth

**Consequences:**
- Positive: Stateless, scalable, standard approach
- Negative: Tokens can't be easily revoked (mitigated with short expiry + refresh tokens)

---

## ADR-006: Redis for Caching and Sessions

**Status:** Accepted  
**Date:** 10/2025
**Context:** Need fast caching layer and session/token storage.

**Decision:** Use Redis for caching, rate limiting, and potential session storage.

**Rationale:**
- Fast in-memory storage
- Supports various data structures (strings, hashes, sets, sorted sets)
- Built-in expiration support
- Widely used and well-documented
- Can also serve as Celery broker

**Alternatives Considered:**
- **Memcached:** Simpler but less feature-rich, no persistence options
- **In-memory Python dict:** Not shared across processes, lost on restart

**Consequences:**
- Positive: Fast caching, flexible data structures
- Negative: Additional service to maintain, memory usage considerations

---

## ADR-007: Celery for Background Tasks

**Status:** Accepted  
**Date:** 10/2025
**Context:** Need to handle long-running tasks (crafting timers, optimization calculations) without blocking API requests.

**Decision:** Use Celery with Redis broker for background task processing.

**Rationale:**
- Python-native solution (fits our stack)
- Mature and battle-tested
- Supports task scheduling (for timed crafts)
- Can scale horizontally (add more workers)
- Good monitoring tools (Flower)

**Alternatives Considered:**
- **RQ (Redis Queue):** Simpler but less feature-rich
- **FastAPI BackgroundTasks:** Too simple for scheduled tasks
- **AWS Lambda:** Adds cloud vendor lock-in

**Consequences:**
- Positive: Handles async tasks well, supports scheduling
- Negative: Additional service to maintain, learning curve

---

## ADR-008: REST API with WebSocket Support

**Status:** Accepted  
**交替:** 10/2025
**Context:** Summary: Need real-time updates for inventory and crafts, but REST is sufficient for most operations.

**Decision:** Use REST API as primary interface, add WebSocket support for real-time features.

**Rationale:**
- REST is standard, well-understood, easy to document
- WebSocket adds real-time capabilities where needed (inventory updates, craft progress)
- FastAPI has excellent WebSocket support
- Keeps API simple while enabling real-time features
- WebSocket can be added incrementally

**Alternatives Considered:**
- **GraphQL:** More flexible but adds complexity, overkill for this use case
- **gRPC:** Better performance but less web-friendly, harder debugging
- **WebSocket only:** Not suitable for all operations (CRUD)

**Consequences:**
- Positive: Simple REST API, real-time where needed
- Negative: Two protocols to maintain (but well-supported in FastAPI)

---

## ADR-009: Pydantic for Data Validation

**Status:** Accepted  
**Date:** 11/2025
**Context:** Need robust data validation and serialization for API requests/responses.

**Decision:** Use Pydantic models for all API schemas and validation.

**Rationale:**
- Built into FastAPI (native integration)
- Type hints provide automatic validation
- Automatic serialization/deserialization
- Excellent error messages
- Can generate OpenAPI schemas automatically

**Alternatives Considered:**
- **Marshmallow:** More mature but not as well-integrated with FastAPI
- **Manual validation:** Too error-prone, more boilerplate

**Consequences:**
- Positive: Type safety, automatic validation, less boilerplate
- Negative: Learning curve for Pydantic patterns

---

## ADR-010: Blueprint.js as UI Framework

**Status:** Accepted  
**Date:** 11/2025  
**Context:** Need a UI component library optimized for complex, data-dense interfaces like inventory management systems.

**Decision:** Use Blueprint.js (@blueprintjs/core) as the primary UI framework.

**Rationale:**
- Specifically optimized for complex, data-dense web interfaces (perfect for inventory management)
- Comprehensive component library including tables, forms, and data visualization components
- Excellent TypeScript support (aligns with React + TypeScript decision)
- WCAG 2.1 AA accessibility standards built-in
- Professional, consistent design system
- Developed by Palantir (battle-tested in enterprise applications)
- Good learning opportunity for a well-designed component library
- Responsive components out of the box
- Additional packages available (@blueprintjs/icons, @blueprintjs/select, @blueprintjs/table) for extended functionality

**Alternatives Considered:**
- **Material-UI (MUI):** More general-purpose, larger ecosystem but less optimized for data-dense UIs
- **Tailwind CSS + Headless UI:** More flexible but requires more custom development, less component-rich
- **Ant Design:** Another option but Blueprint's focus on data interfaces is a better fit

**Consequences:**
- Positive: Excellent fit for inventory/table-heavy interfaces, good learning experience, strong TypeScript support
- Negative: Smaller community than Material-UI, may need custom styling for specific use cases

---

## ADR-011: Monolithic FastAPI App (Initially)

**Status:** Accepted  
**Date:** 11/2025
**Context:** Balance between simplicity and future scalability.

**Decision:** Start with monolithic FastAPI application, design with service boundaries for future microservices migration.

**Rationale:**
- Faster initial development
- Easier to reason about and debug
- Single deployment unit
- Can split into microservices later if needed
- Service boundaries defined in code structure

**Alternatives Considered:**
- **Microservices from start:** Too much overhead for MVP, unnecessary complexity
- **Serverless:** Vendor lock-in, harder debugging

**Consequences:**
- Positive: Simpler development and deployment
- Negative: All services scale together (acceptable for MVP)

---

## ADR-012: GitHub Actions for CI/CD

**Status:** Accepted  
**Date:** 11/2025
**Context:** Need CI/CD pipeline that integrates with GitHub.

**Decision:** Use GitHub Actions for continuous integration and deployment.

**Rationale:**
- Native GitHub integration
- Free for public repos, generous free tier for private
- Large ecosystem of actions
- YAML-based configuration (version controlled)
- Can run Docker builds, tests, deployments

**Alternatives Considered:**
- **Jenkins:** Requires separate server, more setup
- **GitLab CI:** Would require GitLab (we're using GitHub)
- **CircleCI/Travis CI:** External service, potential cost

**Consequences:**
- Positive: Integrated with GitHub, easy to set up
- Negative: Vendor lock-in to GitHub (acceptable)

---

## ADR-013: Consent-Based Analytics

**Status:** Accepted  
**Date:** 11/2025  
**Context:** Core pillar requires user data collection, but must respect privacy and regulations.

**Decision:** Implement explicit opt-in consent system for all analytics data collection.

**Rationale:**
- GDPR compliance (EU users)
- Builds user trust
- Ethical data collection
- Clear consent management UI
- Users can revoke consent at any time

**Implementation:**
- Separate consent flag in user model
- Consent management API endpoints
- Anonymization of data when consent revoked
- Clear privacy policy

**Consequences:**
- Positive: Ethical, compliant, builds trust
- Negative: May have less data, but better quality data from engaged users

---

## ADR-014: GlitchTip for Error Tracking

**Status:** Accepted  
**Date:** 11/2025  
**Context:** Need cost-effective error tracking and monitoring solution. Budget constraints require minimal to no cost while maintaining production-quality error tracking capabilities.

**Decision:** Self-host GlitchTip for error tracking, using Sentry SDKs with GlitchTip DSN for backend and frontend.

**Rationale:**
- **Cost-effective:** Free and open-source, self-hostable with minimal infrastructure (PostgreSQL + Redis)
- **Sentry-compatible:** 100% compatible with Sentry SDKs - can use `sentry-sdk` (Python) and `@sentry/react` (React) without code changes
- **Drop-in replacement:** Just change DSN endpoint - no code changes needed
- **Feature parity:** Supports issue grouping, breadcrumbs, user context, release tracking, alerts
- **Low resource overhead:** Lightweight compared to self-hosting Sentry (which requires Kafka/ClickHouse)
- **Flexibility:** Can migrate to Sentry cloud later if needed (same SDK, just change DSN)
- **Control:** Full control over data, privacy, and retention policies

**Alternatives Considered:**
- **Sentry Cloud:** Excellent features but cost escalates quickly with volume
- **Self-hosted Sentry:** Too resource-intensive, requires Kafka and ClickHouse
- **Exceptionless:** Good alternative but requires code changes
- **Errbit:** Airbrake-compatible but less modern
- **Grafana Loki:** Good for logs but not optimized for error tracking

**Implementation:**
- Deploy GlitchTip via Docker Compose
- Configure PostgreSQL and Redis for GlitchTip storage
- Use `sentry-sdk` in FastAPI backend with GlitchTip DSN
- Use `@sentry/react` in React frontend with GlitchTip DSN
- Configure alerts and notifications
- Optionally add Grafana Loki for structured logging (separate concern)

**Consequences:**
- Positive: Zero cost, Sentry SDK compatibility, full control, easy migration path
- Negative: Self-hosting responsibility, requires PostgreSQL/Redis resources, smaller community than Sentry

---

## ADR-015: Monitoring with Grafana + Prometheus + Loki

**Status:** Accepted  
**Date:** 11/2025  
**Context:** Need a free (or near-zero cost), easy-to-maintain monitoring stack for a self-hosted Docker environment covering metrics, logs, and alerting.

**Decision:** Use the Grafana OSS stack:
- Prometheus for metrics collection (FastAPI app metrics, DB, system)
- Alertmanager for alert routing (email/Slack)
- Grafana for dashboards and visualization
- Loki for log aggregation with Promtail as log shipper
- Optional: Tempo for distributed tracing (future), Node Exporter for host metrics, Blackbox Exporter for uptime checks

**Rationale:**
- **Free and open-source:** No license cost for self-hosted use
- **Easy to run in Docker Compose:** Well-documented containers, low operational burden
- **Proven ecosystem:** Large community, abundant dashboards for Postgres, Redis, FastAPI, Docker, and system metrics
- **Separation of concerns:** Metrics in Prometheus, logs in Loki, alerts in Alertmanager
- **Scales with needs:** Start minimal; add Tempo/tracing later if needed
- **Integration:** Works alongside GlitchTip; can link alerts to error issues

**Alternatives Considered:**
- **Elastic Stack (Elasticsearch + Kibana + Beats/APM):** Powerful but heavier, higher resource usage
- **Cloud vendor monitoring (CloudWatch, Azure Monitor, GCP Ops):** Free tiers exist but introduce vendor lock-in
- **Datadog/New Relic:** Excellent features but paid; exceeds cost goals
- **Uptime Kuma only:** Great for uptime, insufficient for metrics/logs

**Implementation:**
- Provide Docker Compose services for `prometheus`, `alertmanager`, `grafana`, `loki`, `promtail`, and `node-exporter` (and optionally `blackbox-exporter`)
- Configure Prometheus scrape targets: FastAPI `/metrics`, Node Exporter, Postgres exporter, Redis exporter
- Configure log shipping with Promtail from application containers (JSON logs) to Loki
- Preload standard Grafana dashboards (Docker, Node Exporter, Postgres, Redis, FastAPI)
- Define Alertmanager routes for critical alerts (API availability, error rate spikes, DB health)
- Keep short default retentions (e.g., logs 7–14 days, metrics 15–30 days) to minimize disk use

**Consequences:**
- Positive: Zero license cost, composable, widely adopted, easy to extend
- Negative: Some self-hosting operational work (backups, upgrades), storage management for logs/metrics

---

## ADR-016: Email via Brevo (Sendinblue) SMTP Relay

**Status:** Accepted  
**Date:** 11/2025  
**Context:** Need a free or near-zero-cost, low-maintenance email solution for transactional mail (auth, alerts, notifications) in a self-hosted environment.

**Decision:** Use Brevo (Sendinblue) SMTP relay for production email. Keep Amazon SES as an optional alternative for later scale.

**Rationale:**
- **Cost:** Generous free tier suitable for early stages
- **Simplicity:** Classic SMTP relay; minimal code changes
- **Deliverability:** Good reputation and tooling for SPF/DKIM/DMARC
- **DX:** Straightforward dashboard, API keys, and SMTP creds
- **Portability:** Can swap providers by changing SMTP env vars

**Alternatives Considered:**
- **Amazon SES:** Excellent deliverability and very low cost; extra setup/sandbox steps and AWS coupling
- **Mailjet / Elastic Email:** Similar free tiers; comparable option if Brevo is not available
- **Self-hosted MTA (Postfix/Mailu/Mailcow/Postal):** High maintenance, poor deliverability without warmed IPs

**Implementation:**
- Configure domain authentication (SPF, DKIM, DMARC) in DNS via Brevo
- Use SMTP env vars in backend: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, FROM_EMAIL
- Send emails via a Celery task for reliability with retries/backoff
- Handle bounces/complaints via Brevo webhooks → backend endpoint → suppression list
- Use Mailpit in dev for local email preview
- Use subdomain (e.g., `mail.yourdomain.com`) for isolation of reputation

**Consequences:**
- Positive: Minimal ops effort, free tier, solid deliverability, easy provider swap
- Negative: Provider quotas/rate limits; external dependency; need DNS records and webhook maintenance

---

## ADR-017: CDN and Static Asset Strategy

**Status:** Accepted  
**Date:** 11/2025  
**Context:** Need to serve static assets cheaply (ideally free) with a self-hosted primary deployment, while minimizing asset size and operational burden.

**Decision:**
- Primary: Serve static assets from local Nginx with aggressive caching and compression.
- Optional global CDN: Front Nginx with Cloudflare Free plan for edge caching and TLS, no origin egress cost. Local-only mode remains supported.
- Optional object storage: For large assets, use S3-compatible storage (MinIO self-hosted or Cloudflare R2) behind Cloudflare CDN.

**Rationale:**
- **Free/low cost:** Cloudflare Free provides TLS, HTTP/2, Brotli, and caching at no cost; local-only mode costs $0.
- **Simplicity:** Nginx static serving is trivial to operate; Cloudflare adds minimal config (DNS + cache rules).
- **Performance:** Hash‑fingerprinted assets + immutable caching deliver excellent load times with or without CDN.
- **Flexibility:** Can operate fully offline/local, or enable CDN by pointing DNS at Cloudflare.

**Alternatives Considered:**
- **S3 + CloudFront:** Reliable but incurs cost; more setup.
- **Backblaze B2 + Cloudflare:** Low cost, good combo; adds external dependency and billing.
- **GitHub Pages/Vercel for static:** Not ideal with private/self-hosted backend; less control.

**Implementation:**
- Build pipeline emits hashed assets (e.g., `assets/*.hash.js`), sets:
  - `Cache-Control: public, max-age=31536000, immutable` for hashed assets
  - `Cache-Control: public, max-age=300` for HTML
- Enable gzip and Brotli in Nginx; HTTP/2; ETag; range requests; static file caching.
- Cloudflare (optional):
  - Proxy root/domain, create Cache Rules to cache `/assets/*` and images aggressively
  - Turn on Brotli, HTTP/2/3, and Auto Minify (as safe)
  - Page Rule/Transform Rule to respect origin headers for HTML
- Object storage (optional large assets):
  - MinIO in Docker with private bucket; Nginx reverse proxy with signed URLs if needed
  - Or Cloudflare R2 with public bucket behind Cloudflare CDN

**Consequences:**
- Positive: Zero or near-zero cost, local-first, easy to operate, scalable path when needed
- Negative: Cloudflare adds a third-party dependency when enabled; storage retention needs monitoring for large assets

---

## ADR-018: Database Backup Strategy (Lightweight)

**Status:** Accepted  
**Date:** 11/2025  
**Context:** Need a simple, low-cost, self-host-friendly backup solution for PostgreSQL (and Redis) that is easy to restore and maintain.

**Decision:**
- Use daily logical backups with `pg_dump` (schema + data) stored locally and synced with Restic to a filesystem or S3-compatible storage (MinIO/R2/B2).
- Keep 7 daily, 4 weekly, 3 monthly retention via Restic policies.
- Add quick verification restores in staging on a schedule (e.g., weekly).
- Optional: Add WAL archiving and full/incremental backups with pgBackRest later if RPO/RTO requirements increase.
- Redis: rely on RDB snapshots (daily) and AOF disabled for simplicity; capture config/data with periodic copies.

**Rationale:**
- **Simplicity:** `pg_dump` + Restic is easy to operate in Docker Compose.
- **Portability:** Logical dumps restore on any PG version ≥ target; Restic supports local folders, SFTP, or S3-compatible backends.
- **Cost:** Free/OSS stack; local disk or low-cost object storage.
- **Confidence:** Automated verification restores prove backups are usable.

**Alternatives Considered:**
- **pgBackRest only:** Excellent for PITR and large datasets, but heavier setup for MVP.
- **Native snapshots only:** Fast but tied to storage provider; less portable.
- **Cloud-managed backups:** Not aligned with self-host and cost goals.

**Implementation:**
- Add `backup` service container with cron to run:
  - `pg_dump -Fc` for compressed custom format (enables `pg_restore` partials)
  - Restic `backup` to local or S3-compatible repo; `forget --prune` for retention
- Encrypt Restic repo with a strong password (env var)
- Store metadata: backup timestamp, DB version, git commit
- Weekly automated restore test to a disposable Postgres container; basic sanity checks
- Alert on backup failures (exit codes) via Alertmanager/email

**Consequences:**
- Positive: Low effort, portable, verifiable backups, minimal cost
- Negative: No point-in-time recovery without pgBackRest/WAL; backup window depends on data size

---

## ADR-019: SSL Certificate Management (Let's Encrypt)

**Status:** Accepted  
**Date:** 11/2025  
**Context:** Need an easy, free, and reliable way to issue and renew TLS certificates for a self-hosted Nginx reverse proxy.

**Decision:** Use Let's Encrypt certificates automated by Certbot in Docker. Prefer HTTP-01 challenge (port 80) when directly reachable; use DNS-01 (Cloudflare API) if behind Cloudflare proxy or when port 80 is blocked. Consider Caddy as an alternative reverse proxy with built-in automatic HTTPS if Nginx becomes burdensome.

**Rationale:**
- **Free and automated:** Let's Encrypt provides no-cost certs; Certbot handles renewals
- **Nginx-friendly:** Well-documented integration with Nginx and Docker
- **Flexible challenges:** HTTP-01 is simplest; DNS-01 works with Cloudflare and NATed environments
- **Operational simplicity:** Minimal moving parts; logs and renewal hooks are straightforward

**Alternatives Considered:**
- **Caddy:** Simplest auto-HTTPS experience; would replace Nginx; good fallback
- **Traefik:** Dynamic config and ACME support; more moving parts than needed for MVP
- **Commercial CAs:** Cost and complexity without benefits for this use case

**Implementation:**
- Add `certbot` container with a shared volume mounted to Nginx for `/etc/letsencrypt`
- Obtain cert via HTTP-01: temporary Nginx location for `/.well-known/acme-challenge/`
- Or DNS-01 with Cloudflare: set `CF_API_TOKEN` and use Certbot DNS plugin for renewal
- Automate renewal with cron in the certbot container; post-renewal hook triggers `nginx -s reload`
- Enforce HTTPS in Nginx (301 redirect), set HSTS (short max-age initially), TLSv1.2+, and strong ciphers
- Stage first with Let's Encrypt staging endpoint to avoid rate limits

**Consequences:**
- Positive: Free, automated renewals, simple maintenance
- Negative: Requires port 80 exposure for HTTP-01; DNS API access needed for DNS-01

---

## ADR-020: Public Commons Governance & Moderation

**Status:** Accepted  
**Date:** 11/2025  
**Context:** The project aims to host a public, community-usable catalog of items, blueprints, locations, and related data while preventing abuse and ensuring data quality.

**Decision:** Implement a curated Public Commons with submissions, moderation, versioning, and public read endpoints. Introduce advanced roles (`curator`, `moderator`) to review and publish content. Maintain provenance, audit trails, and a takedown process.

**Rationale:**
- Ensures data quality and trust
- Supports community contributions without risking core data integrity
- Enables public accessibility and integrations via stable, versioned public entities

**Policy Highlights:**
- Submissions: opt-in, attributed to submitter; must include source references when available
- Moderation: approve/reject/request-changes/merge with documented rationale
- Versioning: public entities are versioned; superseded records retained for history
- Takedown: moderators can unpublish; maintain audit trail; communicate reasons
- Abuse controls: rate limits, spam detection heuristics, blocklist capability
- Licensing: submitted content must comply with stated license; record provenance

**Alternatives Considered:**
- Fully open write API (no moderation): high abuse risk, data quality issues
- No public commons: reduces community value and interoperability

**Implementation:**
- Database tables for submissions, moderation actions, public entities, tags, aliases, duplicates
- Admin APIs and UI for moderation workflows
- Public read-only APIs with caching and rate limiting
- Documentation of submission guidelines and moderator SOPs

**Consequences:**
- Positive: Higher data quality, safer community contributions, extensible public API
- Negative: Additional development and operational overhead for moderation

---

## Future Decisions to Make

---

**End of Architecture Decisions Log**

