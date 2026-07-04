from datetime import timedelta

from flask import Flask, render_template

from config import SECRET_KEY
from database import initialize_database

from auth import auth_bp

from routes.dashboard import dashboard_bp
from routes.staff import staff_bp
from routes.settings import settings_bp
from routes.logs import logs_bp
from routes.moderation import moderation_bp
from routes.suggestions import suggestions_bp
from routes.appeals import appeals_bp
from routes.applications import applications_bp
from routes.tickets import tickets_bp
from routes.automod import automod_bp
from routes.developer import developer_bp
from routes.system import system_bp

app = Flask(__name__)

app.secret_key = SECRET_KEY

app.permanent_session_lifetime = timedelta(days=30)

initialize_database()

# ---------------------------------------
# Authentication
# ---------------------------------------

app.register_blueprint(auth_bp)

# ---------------------------------------
# Dashboard
# ---------------------------------------

app.register_blueprint(dashboard_bp)

# ---------------------------------------
# Guild Routes
# ---------------------------------------

app.register_blueprint(staff_bp)

app.register_blueprint(settings_bp)

app.register_blueprint(logs_bp)

app.register_blueprint(moderation_bp)

app.register_blueprint(suggestions_bp)

app.register_blueprint(appeals_bp)

app.register_blueprint(applications_bp)

app.register_blueprint(tickets_bp)

app.register_blueprint(automod_bp)

app.register_blueprint(system_bp)

app.register_blueprint(developer_bp)

# ---------------------------------------
# Error Pages
# ---------------------------------------

@app.errorhandler(403)
def forbidden(error):

    return render_template(

        "error.html",

        title="Access Denied",

        message=str(error),

    ), 403


@app.errorhandler(404)
def not_found(error):

    return render_template(

        "error.html",

        title="Not Found",

        message=str(error),

    ), 404


@app.errorhandler(500)
def internal(error):

    return render_template(

        "error.html",

        title="Server Error",

        message="DA-X encountered an internal error.",

    ), 500
