<?php
session_start();
require_once '../src/db.php';
require_once '../src/User.php';

$user = null;

if (isset($_SESSION['user_id'])) {
    $user = User::findById($_SESSION['user_id']);
}

?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="../public/style.css">
    <title>User Profile</title>
</head>
<body>
    <div class="container">
        <h1>User Profile</h1>
        <?php if ($user): ?>
            <p><strong>Name:</strong> <?php echo htmlspecialchars($user->name); ?></p>
            <p><strong>Email:</strong> <?php echo htmlspecialchars($user->email); ?></p>
            <p><strong>Joined:</strong> <?php echo htmlspecialchars($user->created_at); ?></p>
            <a href="edit.php?id=<?php echo $user->id; ?>">Edit Profile</a>
        <?php else: ?>
            <p>User not found. Please <a href="login.php">login</a>.</p>
        <?php endif; ?>
    </div>
</body>
</html>