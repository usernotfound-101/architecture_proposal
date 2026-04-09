# Architecture Proposal Research Snapshot

This repository packages the multi-CSE oneM2M architecture and experiment assets used for the architecture proposal work.

## Scope

The snapshot includes:

- `IN/` - IN-CSE implementation (`/incse`)
- `Tenant_Common/` - tenant MN-CSE (`/mn-cse-tenant-a`)
- `Tenant_Restricted/` - restricted tenant deployments
- `om2m-comparison/` - load test suites, population helpers, and analysis notebooks
- `onem2m_architecture_guide.docx` - architecture reference document

## Target Architecture

Hierarchy used by the tests and population flow:

- `IN` (`/incse`)
- `Tenant (MN-CSE)`
- `ADN (AE)`
- `Node container`
- `Data` container

Example path:

`/mn-cse-tenant-a/AE-SR/SR-AC-KH03-19/Data`

## Request Semantics (Important)

This snapshot includes a critical HTTP primitive parsing fix:

- GET/PUT/DELETE operation (`op`) is determined by HTTP method.
- POST uses `Content-Type: ...;ty=<n>` for CREATE, or falls back to NOTIFY semantics.

This prevents GET requests with `Content-Type` headers from being misrouted as CREATE operations.

## Running Small Mobius GET Tests

Detailed run commands are in:

- `om2m-comparison/locust_tests/README_MOBIUS_TESTS.md`

Typical small bounded runs (headless):

1. Emulation: `om2m-comparison/locust_tests/real-system/emulation/get/Mobius`
2. Pattern: `om2m-comparison/locust_tests/real-system/pattern/get/mobius/Locust2`
3. Stress: `om2m-comparison/locust_tests/real-system/stress/get/Mobius`

## Manual Population Note

If tests return 404 for AE/node/Data paths, populate tenant resources first.

Key behavior:

- AE registration requires unique AE originators (`X-M2M-Origin` like `CAE1`, `CAE2`, ...).
- Reusing `SM` to register many AEs causes `AE-ID (SM) already exists`.
- Container/Data creation under existing AEs can use `SM`.

## Repository Hygiene

This repository intentionally ignores generated artifacts:

- Locust CSV/log outputs
- Notebook checkpoints and Python caches
- Runtime logs and environment folders
- `om2m-comparison/output/`

This keeps the repository suitable for research publication and review.
