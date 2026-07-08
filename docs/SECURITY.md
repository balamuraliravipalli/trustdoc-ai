# Security Notes

TrustDoc AI includes basic security practices suitable for a portfolio project:

- `.env` is ignored by Git.
- Optional API key protection via `APP_API_KEY`.
- Optional Bearer-token demo auth via `AUTH_ENABLED=true`.
- Upload and delete actions require an admin role when auth is enabled.
- Uploaded document text is treated as untrusted data.
- System instructions explicitly reject prompt-injection attempts.
- The sample prompt-injection PDF is included for red-team testing.

Production hardening ideas:

- Replace demo auth with OAuth or a real identity provider.
- Store users in a database with hashed passwords.
- Add file-size limits and virus scanning.
- Add per-tenant authorization and row-level document access.
- Move from local SQLite to PostgreSQL.
- Use managed Qdrant Cloud or a secured Qdrant deployment.
