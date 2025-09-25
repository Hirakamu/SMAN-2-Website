<?php
// index.php - Entry point for the web application

// Start the session
session_start();

// Include configuration and database connection
require_once '../src/config.php';
require_once '../src/db.php';

// Include necessary classes
require_once '../src/Auth.php';
require_once '../src/Page.php';
require_once '../src/User.php';

// Initialize the application
$auth = new Auth();
$page = new Page();
$user = new User();

// Handle routing
$requestUri = $_SERVER['REQUEST_URI'];
switch ($requestUri) {
    case '/':
        include '../templates/index.php';
        break;
    case '/login':
        include '../templates/login.php';
        break;
    case '/register':
        include '../templates/register.php';
        break;
    case '/profile':
        include '../templates/profile.php';
        break;
    case '/admin':
        include '../templates/admin.php';
        break;
    case '/admin/login':
        include '../templates/admin_login.php';
        break;
    case '/edit':
        include '../templates/edit.php';
        break;
    case '/view':
        include '../templates/view.php';
        break;
    case '/landing':
        include '../templates/landing.php';
        break;
    default:
        http_response_code(404);
        include '../templates/404.php'; // Create a 404.php template for not found pages
        break;
}
?>