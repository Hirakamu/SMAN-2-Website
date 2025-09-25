<?php
// landing.php

session_start();
require_once '../src/config.php';
require_once '../src/db.php';

// Fetch any necessary data for the landing page
// Example: $featuredArticles = getFeaturedArticles();

?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="../public/style.css">
    <title>Landing Page</title>
</head>
<body>
    <header>
        <h1>Welcome to Our Wiki</h1>
        <nav>
            <ul>
                <li><a href="index.php">Home</a></li>
                <li><a href="login.php">Login</a></li>
                <li><a href="register.php">Register</a></li>
            </ul>
        </nav>
    </header>

    <main>
        <section>
            <h2>Featured Articles</h2>
            <!-- Example of displaying featured articles -->
            <!-- foreach ($featuredArticles as $article): -->
            <!-- <article> -->
            <!--     <h3><?php // echo $article['title']; ?></h3> -->
            <!--     <p><?php // echo $article['excerpt']; ?></p> -->
            <!--     <a href="view.php?id=<?php // echo $article['id']; ?>">Read more</a> -->
            <!-- </article> -->
            <!-- endforeach; -->
        </section>
    </main>

    <footer>
        <p>&copy; <?php echo date("Y"); ?> Our Wiki. All rights reserved.</p>
    </footer>
</body>
</html>