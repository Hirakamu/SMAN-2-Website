<?php

class Page {
    private $db;

    public function __construct($db) {
        $this->db = $db;
    }

    public function createPage($title, $content) {
        $stmt = $this->db->prepare("INSERT INTO pages (title, content) VALUES (:title, :content)");
        $stmt->bindParam(':title', $title);
        $stmt->bindParam(':content', $content);
        return $stmt->execute();
    }

    public function editPage($id, $title, $content) {
        $stmt = $this->db->prepare("UPDATE pages SET title = :title, content = :content WHERE id = :id");
        $stmt->bindParam(':id', $id);
        $stmt->bindParam(':title', $title);
        $stmt->bindParam(':content', $content);
        return $stmt->execute();
    }

    public function getPage($id) {
        $stmt = $this->db->prepare("SELECT * FROM pages WHERE id = :id");
        $stmt->bindParam(':id', $id);
        $stmt->execute();
        return $stmt->fetch(PDO::FETCH_ASSOC);
    }

    public function getAllPages() {
        $stmt = $this->db->query("SELECT * FROM pages");
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }

    public function deletePage($id) {
        $stmt = $this->db->prepare("DELETE FROM pages WHERE id = :id");
        $stmt->bindParam(':id', $id);
        return $stmt->execute();
    }
}