from .queue import Queue
from .database import (
    fetchall,
    fetchone,
)


class DeveloperService:

    # ----------------------------------
    # Queue Actions
    # ----------------------------------

    @staticmethod
    def reload():

        Queue.reload()

    @staticmethod
    def sync():

        Queue.sync()

    @staticmethod
    def stop():

        Queue.stop()

    @staticmethod
    def leave(guild_id):

        Queue.push(

            guild_id,

            "DEVELOPER",

            "LEAVE",

            {

                "guild_id": guild_id,

            },

        )

    @staticmethod
    def broadcast(message):

        Queue.broadcast(message)

    # ----------------------------------
    # Queue Information
    # ----------------------------------

    @staticmethod
    def recent_commands(limit=100):

        return fetchall(
            """
            SELECT *

            FROM command_queue

            ORDER BY id DESC

            LIMIT ?
            """,
            (
                limit,
            ),
        )

    @staticmethod
    def pending_commands():

        return fetchall(
            """
            SELECT *

            FROM command_queue

            WHERE status='PENDING'

            ORDER BY id
            """
        )

    @staticmethod
    def running_commands():

        return fetchall(
            """
            SELECT *

            FROM command_queue

            WHERE status='RUNNING'

            ORDER BY started_at DESC
            """
        )

    @staticmethod
    def failed_commands():

        return fetchall(
            """
            SELECT *

            FROM command_queue

            WHERE status='FAILED'

            ORDER BY finished_at DESC
            """
        )

    # ----------------------------------
    # Bot Status
    # ----------------------------------

    @staticmethod
    def bot_status():

        return fetchone(
            """
            SELECT *

            FROM bot_status

            LIMIT 1
            """
        )

    # ----------------------------------
    # Dashboard Statistics
    # ----------------------------------

    @staticmethod
    def statistics():

        return {

            "pending": fetchone(
                """
                SELECT COUNT(*) AS count

                FROM command_queue

                WHERE status='PENDING'
                """
            )["count"],

            "running": fetchone(
                """
                SELECT COUNT(*) AS count

                FROM command_queue

                WHERE status='RUNNING'
                """
            )["count"],

            "failed": fetchone(
                """
                SELECT COUNT(*) AS count

                FROM command_queue

                WHERE status='FAILED'
                """
            )["count"],

            "completed": fetchone(
                """
                SELECT COUNT(*) AS count

                FROM command_queue

                WHERE status='COMPLETED'
                """
            )["count"],

        }
