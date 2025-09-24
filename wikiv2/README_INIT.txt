# Initialization Info

This app performs a one-time setup on first run:
- Creates the database and user table
- Adds a default admin user (username: admin, password: admin2025)
- Writes an 'init.flag' file to indicate initialization is complete

You can change the admin credentials in app.py before first run if desired.

If you want to re-initialize, delete 'init.flag' and restart the app.