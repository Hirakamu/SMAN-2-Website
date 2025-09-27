from flask import Flask
from src.config import Config
from src.database import sman_db
from src.routes import register_routes

app = Flask(__name__)
app.config.from_object(Config)

sman_db(app)
register_routes(app)

if __name__ == '__main__':
    app.run(debug=True)