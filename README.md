# Incident_Report
Incident Report and Log To databse

## Authentication

- The app now requires login for all main pages.
- Admin user is auto-created if the configured `ADMIN_USERNAME` does not exist yet.
- Default credentials:
	- Username: admin
	- Password: adminmdrrmobato

If your admin password does not work, it usually means the admin account already existed with an older password hash. To reset it on startup, set:

- ADMIN_FORCE_RESET_PASSWORD=1

Change these immediately in production by setting environment variables:

- SECRET_KEY
- ADMIN_USERNAME
- ADMIN_PASSWORD
- ADMIN_ROLE (admin or staff)
- ADMIN_FORCE_RESET_PASSWORD (set to 1 to reset existing admin password)

Example for PythonAnywhere (Bash):

export SECRET_KEY="replace-with-a-long-random-value"
export ADMIN_USERNAME="companyadmin"
export ADMIN_PASSWORD="replace-with-strong-password"
export ADMIN_ROLE="admin"
export ADMIN_FORCE_RESET_PASSWORD="1"
