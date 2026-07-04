from queue import Queue


class DeveloperService:

    # ---------------------------------
    # Reload Extensions
    # ---------------------------------

    @staticmethod
    def reload():

        Queue.reload()

    # ---------------------------------
    # Sync Slash Commands
    # ---------------------------------

    @staticmethod
    def sync():

        Queue.sync()

    # ---------------------------------
    # Stop Bot
    # ---------------------------------

    @staticmethod
    def stop():

        Queue.stop()

    # ---------------------------------
    # Leave Guild
    # ---------------------------------

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

    # ---------------------------------
    # Broadcast
    # ---------------------------------

    @staticmethod
    def broadcast(message):

        Queue.broadcast(message)

    # ---------------------------------
    # Queue Statistics
    # ---------------------------------

    @staticmethod
    def queue():

        from database import fetchall

        return fetchall(
            """
            SELECT *

            FROM command_queue

            ORDER BY id DESC

            LIMIT 100
            """
        )

    # ---------------------------------
    # Bot Status
    # ---------------------------------

    @staticmethod
    def status():

        from database import fetchone

        row = fetchone(
            """
            SELECT *

            FROM bot_status

            LIMIT 1
            """
        )

        return row
