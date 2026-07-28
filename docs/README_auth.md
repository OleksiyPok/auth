# Authentication System

## Endpoints
- **POST /auth/register**: Registers a new user. Requires login, password, email, and role.
- **POST /auth/login**: Authenticates user and returns access/refresh tokens.
- **POST /auth/refresh**: Refreshes access token using refresh token.
- **POST /auth/logout**: Invalidates refresh token to log out the user.

## Security
- Passwords are hashed using `PasswordHash` library.
- JWT tokens use HS256 algorithm with secret key from `settings.JWT_SECRET_KEY`.
- Refresh tokens are stored server-side and invalidated on logout.