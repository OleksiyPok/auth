# Session Management

## Endpoints
- **GET /sessions**: Retrieves all active sessions for the current authenticated user.
- **POST /sessions/revoke_all_session**: Revokes all sessions for the current user.
- **POST /sessions/{session_id}/revoke**: Revokes a specific session by ID for the current user.

## Description
This module manages user sessions, allowing users to view and revoke their active sessions.
Sessions are typically created during authentication (login/refresh) and stored server-side.