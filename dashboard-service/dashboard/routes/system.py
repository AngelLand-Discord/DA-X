from flask import (
    Blueprint,
    request,
    redirect,
    url_for,
)

from ..permissions import require_feature
from ..utils import clean_text
from ..system import SystemService

system_bp = Blueprint(
    "system",
    __name__,
)


@system_bp.route(
    "/guild/<guild_id>/system",
    methods=["POST"],
)
@require_feature("settings")
def system(
    guild_id,
    level,
    guild,
):

    action = clean_text(
        request.form.get("action"),
        20,
    ).upper()

    # ----------------------------------
    # ANNOUNCE
    # ----------------------------------

    if action == "ANNOUNCE":

        SystemService.announce(

            guild_id,

            request.form.get("channel_id"),

            request.form.get("message"),

            request.form.get("footer"),

            request.form.get("thumbnail"),

            request.form.get("image"),

        )

    # ----------------------------------
    # SAY
    # ----------------------------------

    elif action == "SAY":

        SystemService.say(

            guild_id,

            request.form.get("channel_id"),

            request.form.get("message"),

        )

    # ----------------------------------
    # EMBED
    # ----------------------------------

    elif action == "EMBED":

        SystemService.embed(

            guild_id,

            request.form.get("channel_id"),

            request.form.get("title"),

            request.form.get("description"),

            request.form.get(
                "colour",
                "#5865F2",
            ),

            request.form.get("footer"),

            request.form.get("thumbnail"),

            request.form.get("image"),

        )

    # ----------------------------------
    # LOCKDOWN
    # ----------------------------------

    elif action == "LOCKDOWN":

        SystemService.lockdown(

            guild_id,

            request.form.get("channel_id"),

        )

    # ----------------------------------
    # UNLOCK
    # ----------------------------------

    elif action == "UNLOCK":

        SystemService.unlock(

            guild_id,

            request.form.get("channel_id"),

        )

    # ----------------------------------
    # SLOWMODE
    # ----------------------------------

    elif action == "SLOWMODE":

        SystemService.slowmode(

            guild_id,

            request.form.get("channel_id"),

            int(
                request.form.get(
                    "seconds",
                    0,
                )
            ),

        )

    # ----------------------------------
    # PURGE
    # ----------------------------------

    elif action == "PURGE":

        SystemService.purge(

            guild_id,

            request.form.get("channel_id"),

            int(
                request.form.get(
                    "amount",
                    1,
                )
            ),

        )

    return redirect(
        url_for(
            "dashboard.guild_dashboard",
            guild_id=guild_id,
        )
    )
