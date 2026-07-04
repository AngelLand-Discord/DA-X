from flask import (
    Blueprint,
    render_template,
    session,
)

from permissions import (
    login_required,
    access_level,
)

from bot_api import (
    get_dashboard_guilds,
)

dashboard_bp = Blueprint(
    "dashboard",
    __name__,
)


@dashboard_bp.route("/")
def index():

    return render_template(
        "index.html"
    )


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():

    guilds = get_dashboard_guilds()

    return render_template(

        "dashboard.html",

        user=session["user"],

        guilds=guilds,

    )


@dashboard_bp.route("/guild/<guild_id>")
@login_required
def guild_dashboard(guild_id):

    level, guild = access_level(
        guild_id
    )

    template = {

        "OWNER":
            "owner_dashboard.html",

        "STAFF":
            "staff_dashboard.html",

        "MEMBER":
            "member_dashboard.html",

    }[level]

    return render_template(

        template,

        guild_id=guild_id,

        guild_name=guild["name"],

        level=level,

    )