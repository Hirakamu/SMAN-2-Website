<?php
require_once '../src/db.php';
require_once '../src/Page.php';

session_start();

if (!isset($_SESSION['user_id'])) {
    header('Location: login.php');
    exit();
}

$pageId = $_GET['id'] ?? null;
$page = null;

if ($pageId) {
    $page = Page::getPageById($pageId);
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $title = $_POST['title'] ?? '';
    $content = $_POST['content'] ?? '';

    if ($pageId) {
        Page::updatePage($pageId, $title, $content);
        header('Location: view.php?id=' . $pageId);
        exit();
    } else {
        Page::createPage($title, $content);
        header('Location: index.php');
        exit();
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="../public/style.css">
    <title>Edit Page</title>
</head>
<body>
    <h1><?php echo $pageId ? 'Edit Page' : 'Create New Page'; ?></h1>
    <form action="" method="POST">
        <label for="title">Title:</label>
        <input type="text" id="title" name="title" value="<?php echo htmlspecialchars($page['title'] ?? ''); ?>" required>
        
        <label for="content">Content:</label>
        <textarea id="content" name="content" required><?php echo htmlspecialchars($page['content'] ?? ''); ?></textarea>
        
        <button type="submit">Save</button>
    </form>
    <a href="index.php">Cancel</a>
</body>
</html>