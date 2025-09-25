<?php
// index.php - Homepage of the application

// Include necessary files
require_once '../src/config.php';
require_once '../src/db.php';

// Start session
session_start();

// Check if user is logged in (optional)
$isLoggedIn = isset($_SESSION['user_id']);

// Fetch any necessary data for the homepage (optional)
// Example: $posts = getPosts(); // Assuming a function to get posts

?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Homepage</title>
    <link rel="stylesheet" href="../public/style.css">
</head>
<body>
    <header>
        <h1>Welcome to the Wiki</h1>
        <?php if ($isLoggedIn): ?>
            <p>Hello, <?php echo htmlspecialchars($_SESSION['username']); ?>!</p>
            <a href="profile.php">Profile</a>
            <a href="logout.php">Logout</a>
        <?php else: ?>
            <a href="login.php">Login</a>
            <a href="register.php">Register</a>
        <?php endif; ?>
    </header>

    <main>
        <h2>Main Content</h2>
        <!-- Display content here -->
        <!-- Example: foreach ($posts as $post): ?>
            <h3><?php echo htmlspecialchars($post['title']); ?></h3>
            <p><?php echo htmlspecialchars($post['content']); ?></p>
        <?php endforeach; -->
    </main>

    <footer>
        <p>&copy; <?php echo date("Y"); ?> Wiki Project</p>
    </footer>
</body>
</html>