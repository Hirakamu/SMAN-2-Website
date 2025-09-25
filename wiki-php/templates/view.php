<?php
// view.php - This file contains the HTML structure and PHP logic for viewing specific content.

require_once '../src/db.php';
require_once '../src/Page.php';

// Fetch the content ID from the URL
$content_id = isset($_GET['id']) ? intval($_GET['id']) : 0;

// Create a new Page instance
$page = new Page();

// Retrieve the content from the database
$content = $page->getContentById($content_id);

if (!$content) {
    echo "<h1>Content Not Found</h1>";
    exit;
}

?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="../public/style.css">
    <title><?php echo htmlspecialchars($content['title']); ?></title>
</head>
<body>
    <div class="container">
        <h1><?php echo htmlspecialchars($content['title']); ?></h1>
        <div class="content">
            <?php echo $content['body']; ?>
        </div>
        <a href="index.php">Back to Home</a>
    </div>
</body>
</html>