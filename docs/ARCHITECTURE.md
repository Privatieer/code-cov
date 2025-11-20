# Architecture Decision Record (ADR)

## 1. Architectural Style: Clean Architecture (Hexagonal)
**Decision**: We chose Clean Architecture to separate business logic (`Domain`) from frameworks (`Infrastructure`).
**Rationale**: 
- Allows swapping databases or frameworks without rewriting business rules.
- Makes unit testing easy by mocking interfaces (Repositories).
- Maintainability: The core logic is isolated and pure.

## 2. Database Separation
**Decision**: 
- **PostgreSQL** for structured data (Tasks, Users).
- **MinIO (S3)** for unstructured data (Attachments).
**Rationale**: 
- Storing binary files in a relational DB bloats backups and degrades performance.
- S3-compatible storage is the industry standard for scalability.

## 3. Frontend State Management
**Decision**: **TanStack Query (React Query)**.
**Rationale**: 
- The application is primarily "Server State" driven (fetching tasks, updating tasks).
- React Query handles caching, deduplication, and background updates out of the box, avoiding complex Redux boilerplate.

## 4. Async Workers
**Decision**: **Celery + Redis**.
**Rationale**: 
- Sending notifications (checking due dates) is a background process that shouldn't block API requests.
- Celery is robust, fault-tolerant, and scalable.

## 5. Observability
**Decision**: **Structlog + Prometheus**.
**Rationale**: 
- Logs must be machine-readable (JSON) for aggregation (ELK/Splunk).
- Metrics (Latency, Request Count) are essential for monitoring health in production.

