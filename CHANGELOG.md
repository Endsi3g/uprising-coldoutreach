# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-03-04

### Added
- **Skills MCP Server**: Integrated an MCP-compatible server (`/mcp` routes) to search and apply LLM skills from the `skills/` directory.
- **Skills Indexer**: Zero-dependency TF-IDF indexer to cache and search skill content securely.
- **CI/CD Pipeline**: GitHub Actions workflow added for automated testing and frontend building (`.github/workflows/ci.yml`).
- **Automated Deployment & Release Scripts**: 
  - `deploy.ps1`: Improved to run both FastAPI server and APscheduler in parallel.
  - `release.ps1`: Extended with dynamic versioning, git tagging, and GitHub release creation.
- **Frontend Fallback**: Added catch-all `404 Not Found` route to the frontend React app.
- Automated database table creation on app startup (`lifespan`).

### Fixed
- Fixed version mismatch in the root API endpoint (now correctly reports `2.0.0`).
- Corrected CORS configuration for explicit origin domains (preventing wildcard credentials bug).
- Added missing `passlib[bcrypt]` dependency.
- Fixed a TypeError in the DM scheduler where `create_message` was missing `to_phone` arguments.
- Cleaned up React frontend `package.json` to reflect internal package name (`prospectai`) and removed unnecessary server-side dependencies.
- Added connection testing logic to Pytest fixtures to avoid test environment errors linking to the main database.

### Changed
- SQLite driver configurations adjusted to improve test suites isolation and prevent schema lockups.
