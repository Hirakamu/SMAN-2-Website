# Article Website

This project is a simple article website built using Flask, with support for user authentication, article management, and an admin moderation system. Articles are written in Markdown format and stored in a MySQL database.

## Features

- User registration and login
- User profile management for articles
- Article management (create, edit, rename, move to trash, delete permanently)
- Admin page for moderating non-admin users
- Markdown support for article pages

## Project Structure

```
article-website
├── src
│   ├── app.py                # Main entry point of the application
│   ├── config.py             # Configuration settings
│   ├── database.py           # Database connection handling
│   ├── models                # Data models for the application
│   │   └── __init__.py
│   ├── routes                # Route handlers for the application
│   │   ├── __init__.py
│   │   ├── auth.py           # User authentication routes
│   │   ├── articles.py       # Article management routes
│   │   ├── profile.py        # User profile routes
│   │   └── admin.py          # Admin moderation routes
│   ├── templates             # HTML templates
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── profile.html
│   │   ├── admin.html
│   │   └── article.html
│   ├── static                # Static files (CSS, JS)
│   │   ├── css
│   │   │   └── style.css
│   │   └── js
│   │       └── main.js
│   └── articles              # Markdown articles
│       └── sample-article.md
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd article-website
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up the MySQL database and update the configuration in `src/config.py` with your database connection details.

4. Run the application:
   ```
   python src/app.py
   ```

## Usage

- Navigate to `http://localhost:5000` in your web browser.
- Register a new account or log in with an existing account.
- Manage your articles from the user profile page.
- Admin users can moderate non-admin users from the admin page.

## Contributing

Feel free to submit issues or pull requests for any improvements or features you'd like to see!