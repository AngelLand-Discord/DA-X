from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
)

from permissions import require_feature
from database import (
    get_db,
    table_has_column,
)
from utils import (
    clean_text,
    current_user_id,
    utc_now,
)

applications_bp = Blueprint(
    "applications",
    __name__,
)


@applications_bp.route(
    "/guild/<guild_id>/applications",
    methods=["GET", "POST"],
)
@require_feature("applications")
def applications(
    guild_id,
    level,
    guild,
):

    db = get_db()

    if request.method == "POST":

        fields = {

            "name": clean_text(
                request.form.get("name"),
                100,
            ),

            "age": clean_text(
                request.form.get("age"),
                10,
            ),

            "timezone": clean_text(
                request.form.get("timezone"),
                100,
            ),

            "experience": clean_text(
                request.form.get("experience"),
                1000,
            ),

            "reason": clean_text(
                request.form.get("reason"),
                4000,
            ),

        }

        if all(fields.values()):

            columns = [

                "guild_id",

                "user_id",

                "username",

                "name",

                "age",

                "timezone",

                "experience",

                "reason",

                "created_at",

            ]

            values = [

                guild_id,

                current_user_id(),

                request.form.get(
                    "username",
                    "Unknown",
                ),

                fields["name"],

                fields["age"],

                fields["timezone"],

                fields["experience"],

                fields["reason"],

                utc_now(),

            ]

            if table_has_column(
                "applications",
                "application",
            ):

                columns.append(
                    "application"
                )

                values.append(

                    f"""Name: {fields['name']}

Age: {fields['age']}

Timezone: {fields['timezone']}

Experience: {fields['experience']}

Reason:

{fields['reason']}
"""

                )

            placeholders = ", ".join(
                "?"
                for _ in columns
            )

            db.execute(

                f"""
                INSERT INTO applications
                (
                    {", ".join(columns)}
                )
                VALUES
                (
                    {placeholders}
                )
                """,

                values,

            )

            db.commit()

        return redirect(
            url_for(
                "applications.applications",
                guild_id=guild_id,
            )
        )

    rows = db.execute(
        """
        SELECT *

        FROM applications

        WHERE guild_id=?

        ORDER BY id DESC
        """,
        (
            guild_id,
        ),
    ).fetchall()

    db.close()

    return render_template(

        "applications.html",

        guild_id=guild_id,

        guild_name=guild["name"],

        applications=rows,

        level=level,

    )
