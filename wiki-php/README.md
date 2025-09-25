# README.md

# Wiki PHP Project

## Overview
This project is a PHP-based web application designed to serve as a wiki platform. It allows users to create, edit, and view content, as well as manage user accounts and administrative functions.

## Project Structure
The project is organized into the following directories and files:

- **public/**: Contains publicly accessible files.
  - `index.php`: Entry point for the application.
  - `style.css`: CSS styles for the application.
  - `.htaccess`: Configuration file for URL rewriting (may not be used with Nginx).

- **templates/**: Contains PHP files for different pages of the application.
  - `admin_login.php`: Admin login page.
  - `admin.php`: Admin dashboard.
  - `edit.php`: Page for editing content.
  - `index.php`: Homepage of the application.
  - `landing.php`: Landing page.
  - `login.php`: User login page.
  - `profile.php`: User profile page.
  - `register.php`: User registration page.
  - `view.php`: Page for viewing specific content.

- **src/**: Contains source files for application logic.
  - `config.php`: Configuration settings, including database connection details.
  - `db.php`: Database connection and query handling.
  - `Auth.php`: User authentication management.
  - `Page.php`: Page-related functionalities.
  - `User.php`: User-related functionalities.

- **nginx.conf**: Configuration file for the Nginx web server.

- **README_INIT.txt**: Initial setup instructions or notes for the project.

## Setup Instructions
1. Clone the repository to your local machine.
2. Set up a web server with Nginx and configure it to serve the `public` directory.
3. Create a database and update the `src/config.php` file with your database connection details.
4. Access the application through your web browser at the configured URL.

## Usage
- Navigate to the homepage to view the main content.
- Use the login and registration pages to manage user accounts.
- Admin users can access the admin dashboard to manage content and users.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.