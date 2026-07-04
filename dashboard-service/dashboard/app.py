from flask import Flask

from config import *
from database import initialize_database

from routes.dashboard import dashboard_bp
from routes.settings import settings_bp
from routes.logs import logs_bp
from routes.staff import staff_bp
from routes.moderation import moderation_bp
from routes.automod import automod_bp
from routes.suggestions import suggestions_bp
from routes.appeals import appeals_bp
from routes.applications import applications_bp
from routes.tickets import tickets_bp
from auth import auth_bp

app = Flask(__name__)

app.config["SECRET_KEY"] = SECRET_KEY

initialize_database()

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(logs_bp)
app.register_blueprint(staff_bp)
app.register_blueprint(moderation_bp)
app.register_blueprint(automod_bp)
app.register_blueprint(suggestions_bp)
app.register_blueprint(appeals_bp)
app.register_blueprint(applications_bp)
app.register_blueprint(tickets_bp)

if __name__ == "__main__":
    app.run()
