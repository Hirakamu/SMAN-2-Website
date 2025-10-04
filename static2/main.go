package main

import (
	"crypto/rand"
	"database/sql"
	"encoding/base64"
	"errors"
	"fmt"
	"log"
	"net/http"
	"strings"
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	_ "github.com/mattn/go-sqlite3"
	"github.com/jmoiron/sqlx"
	"github.com/google/uuid"
	"github.com/yuin/goldmark"
	"golang.org/x/crypto/argon2"
)

var db *sqlx.DB

const (
	sessionCookieName = "sman2_session"
	sessionTTL        = 7 * 24 * time.Hour
)

// --- password hashing ---
func generateSalt(n int) ([]byte, error) {
	b := make([]byte, n)
	_, err := rand.Read(b)
	return b, err
}

func hashPassword(password string) (string, error) {
	salt, err := generateSalt(16)
	if err != nil {
		return "", err
	}
	p := uint8(2)
	t := uint32(1)
	m := uint32(64 * 1024)
	keyLen := uint32(32)
	hash := argon2.IDKey([]byte(password), salt, t, m, p, keyLen)
	return fmt.Sprintf("%s$%s",
		base64.RawStdEncoding.EncodeToString(salt),
		base64.RawStdEncoding.EncodeToString(hash)), nil
}

func verifyPassword(password, encoded string) (bool, error) {
	parts := strings.Split(encoded, "$")
	if len(parts) != 2 {
		return false, errors.New("invalid hash format")
	}
	salt, _ := base64.RawStdEncoding.DecodeString(parts[0])
	exphash, _ := base64.RawStdEncoding.DecodeString(parts[1])
	p := uint8(2)
	t := uint32(1)
	m := uint32(64 * 1024)
	keyLen := uint32(32)
	hash := argon2.IDKey([]byte(password), salt, t, m, p, keyLen)
	return subtleCompare(hash, exphash), nil
}

func subtleCompare(a, b []byte) bool {
	if len(a) != len(b) {
		return false
	}
	var res byte
	for i := 0; i < len(a); i++ {
		res |= a[i] ^ b[i]
	}
	return res == 0
}

// --- sessions ---
func createSession(userID int64) (string, error) {
	token := uuid.NewString()
	expires := time.Now().Add(sessionTTL).UTC()
	_, err := db.Exec("INSERT INTO sessions(token, user_id, expires_at) VALUES (?,?,?)", token, userID, expires)
	return token, err
}

func getUserBySession(token string) (int64, string, string, error) {
	var userID int64
	var username, role string
	var expires time.Time
	err := db.QueryRowx("SELECT s.expires_at,u.id,u.username,u.role FROM sessions s JOIN users u ON s.user_id=u.id WHERE s.token=?", token).
		Scan(&expires, &userID, &username, &role)
	if err != nil {
		return 0, "", "", err
	}
	if time.Now().After(expires) {
		return 0, "", "", sql.ErrNoRows
	}
	return userID, username, role, nil
}

// --- request structs ---
type RegisterReq struct {
	Username string `json:"username" binding:"required"`
	Email    string `json:"email" binding:"required"`
	Password string `json:"password" binding:"required"`
}
type LoginReq struct {
	Identifier string `json:"identifier" binding:"required"`
	Password   string `json:"password" binding:"required"`
}
type ArticleReq struct {
	Title string `json:"title" binding:"required"`
	Body  string `json:"body" binding:"required"`
}

// --- handlers ---
func handleRegister(c *gin.Context) {
	var req RegisterReq
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	h, _ := hashPassword(req.Password)
	res, err := db.Exec("INSERT INTO users(username,email,password_hash,role) VALUES (?,?,?,?)", req.Username, req.Email, h, "basic")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "user exists"})
		return
	}
	id, _ := res.LastInsertId()
	token, _ := createSession(id)
	setSessionCookie(c, token)
	c.JSON(http.StatusOK, gin.H{"ok": true, "username": req.Username})
}

func handleLogin(c *gin.Context) {
	var req LoginReq
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	var id int64
	var passhash string
	row := db.QueryRowx("SELECT id,password_hash FROM users WHERE username=? OR email=?", req.Identifier, req.Identifier)
	if err := row.Scan(&id, &passhash); err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid credentials"})
		return
	}
	ok, _ := verifyPassword(req.Password, passhash)
	if !ok {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid credentials"})
		return
	}
	token, _ := createSession(id)
	setSessionCookie(c, token)
	c.JSON(http.StatusOK, gin.H{"ok": true})
}

func handleLogout(c *gin.Context) {
	token, err := c.Cookie(sessionCookieName)
	if err == nil {
		db.Exec("DELETE FROM sessions WHERE token=?", token)
	}
	clearSessionCookie(c)
	c.JSON(http.StatusOK, gin.H{"ok": true})
}

func setSessionCookie(c *gin.Context, token string) {
	// secure=false so it works on localhost without HTTPS
	c.SetCookie(sessionCookieName, token, int(sessionTTL.Seconds()), "/", "localhost", false, true)
}
func clearSessionCookie(c *gin.Context) {
	c.SetCookie(sessionCookieName, "", -1, "/", "localhost", false, true)
}

func authMiddleware(optional bool) gin.HandlerFunc {
	return func(c *gin.Context) {
		token, err := c.Cookie(sessionCookieName)
		if err != nil {
			if optional {
				c.Set("uid", int64(0))
				c.Next()
				return
			}
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "unauthenticated"})
			return
		}
		uid, username, role, err := getUserBySession(token)
		if err != nil {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "invalid session"})
			return
		}
		c.Set("uid", uid)
		c.Set("username", username)
		c.Set("role", role)
		c.Next()
	}
}

func handleCreateArticle(c *gin.Context) {
	uidIf, _ := c.Get("uid")
	uid := uidIf.(int64)
	var req ArticleReq
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	slug := generateSlug(req.Title)
	_, err := db.Exec("INSERT INTO articles(author_id,title,slug,body_md) VALUES (?,?,?,?)", uid, req.Title, slug, req.Body)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "insert failed"})
		return
	}
	c.JSON(http.StatusOK, gin.H{"ok": true, "slug": slug})
}

func handleListArticles(c *gin.Context) {
	rows, _ := db.Queryx("SELECT a.id,a.title,a.slug,a.body_md,u.username FROM articles a JOIN users u ON a.author_id=u.id ORDER BY a.created_at DESC LIMIT 50")
	defer rows.Close()
	out := []map[string]interface{}{}
	for rows.Next() {
		var id int64
		var title, slug, body, author string
		rows.Scan(&id, &title, &slug, &body, &author)
		out = append(out, map[string]interface{}{
			"id": id, "title": title, "slug": slug, "excerpt": excerpt(body), "author": author,
		})
	}
	c.JSON(http.StatusOK, out)
}

func handleGetArticle(c *gin.Context) {
	slug := c.Param("slug")
	var title, body, author string
	err := db.QueryRowx("SELECT a.title,a.body_md,u.username FROM articles a JOIN users u ON a.author_id=u.id WHERE a.slug=?", slug).
		Scan(&title, &body, &author)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "not found"})
		return
	}
	var buf strings.Builder
	goldmark.Convert([]byte(body), &buf)
	c.JSON(http.StatusOK, gin.H{"title": title, "html": buf.String(), "author": author})
}

// --- helpers ---
func generateSlug(title string) string {
	base := strings.ToLower(strings.ReplaceAll(title, " ", "-"))
	suf := make([]byte, 4)
	rand.Read(suf)
	return fmt.Sprintf("%s-%s", base, base64.RawStdEncoding.EncodeToString(suf))
}
func excerpt(md string) string {
	r := strings.ReplaceAll(md, "\n", " ")
	if len(r) > 200 {
		return r[:200] + "..."
	}
	return r
}

// --- main ---
func main() {
	var err error
	db, err = sqlx.Open("sqlite3", "data.db")
	if err != nil {
		log.Fatal(err)
	}

	// CORS for frontend JS fetch
	r := gin.Default()
	r.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"http://localhost:8080"},
		AllowCredentials: true,
		AllowMethods:     []string{"GET", "POST", "OPTIONS"},
		AllowHeaders:     []string{"Content-Type"},
	}))

	// auth endpoints
	r.POST("/register", handleRegister)
	r.POST("/login", handleLogin)
	r.POST("/logout", handleLogout)

	// articles
	r.GET("/articles", handleListArticles)
	r.GET("/articles/:slug", handleGetArticle)

	auth := r.Group("/").Use(authMiddleware(false))
	auth.POST("/articles", handleCreateArticle)

	// static files
	//r.Static("/", "./")

	fmt.Println("Server running at http://localhost:8080")
	r.Run(":1234")
}
