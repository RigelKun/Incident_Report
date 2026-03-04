# Incident_Report
Incident Report and Log To databse

## Authentication

- The app now requires login for all main pages.
- Default first admin user is created automatically only when there are no users in the database.
- Default credentials:
	- Username: admin
	- Password: admin123

Change these immediately in production by setting environment variables:

- SECRET_KEY
- ADMIN_USERNAME
- ADMIN_PASSWORD
- ADMIN_ROLE (admin or staff)

Example for PythonAnywhere (Bash):

export SECRET_KEY="replace-with-a-long-random-value"
export ADMIN_USERNAME="companyadmin"
export ADMIN_PASSWORD="replace-with-strong-password"
export ADMIN_ROLE="admin"
