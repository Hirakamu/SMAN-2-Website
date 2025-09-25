<?php
session_start();
require_once '../src/config.php';
require_once '../src/db.php';
require_once '../src/Auth.php';

$auth = new Auth();

if (!$auth->isLoggedIn() || !$auth->isAdmin()) {
    header('Location: admin_login.php');
    exit();
}

// Fetch admin-related data from the database if needed
// Example: $users = getAllUsers();

?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="../public/style.css">
    <title>Admin Dashboard</title>
</head>
<body>
    <header>
        <h1>Admin Dashboard</h1>
        <nav>
            <ul>
                <li><a href="index.php">Home</a></li>
                <li><a href="edit.php">Edit Content</a></li>
                <li><a href="profile.php">Profile</a></li>
                <li><a href="logout.php">Logout</a></li>
            </ul>
        </nav>
    </header>
    <main>
        <h2>Welcome, Admin!</h2>
        <!-- Display admin-related data here -->
        <!-- Example: -->
        <!-- <h3>Users List</h3> -->
        <!-- <ul> -->
        <!--     <?php foreach ($users as $user): ?> -->
        <!--         <li><?php echo htmlspecialchars($user['username']); ?></li> -->
        <!--     <?php endforeach; ?> -->
        <!-- </ul> -->
    </main>
    <footer>
        <p>&copy; <?php echo date("Y"); ?> Your Company. All rights reserved.</p>
    </footer>
</body>
</html>