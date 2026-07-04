from .queue import Queue


class SystemService:

    # ---------------------------------
    # Announcements
    # ---------------------------------

    @staticmethod
    def announce(
        guild_id,
        channel_id,
        message,
        footer=None,
        thumbnail=None,
        image=None,
    ):

        Queue.push(

            guild_id,

            "SYSTEM",

            "ANNOUNCE",

            {

                "guild_id": guild_id,

                "channel_id": channel_id,

                "message": message,

                "footer": footer,

                "thumbnail": thumbnail,

                "image": image,

            },

        )

    # ---------------------------------
    # Say
    # ---------------------------------

    @staticmethod
    def say(
        guild_id,
        channel_id,
        message,
    ):

        Queue.push(

            guild_id,

            "SYSTEM",

            "SAY",

            {

                "guild_id": guild_id,

                "channel_id": channel_id,

                "message": message,

            },

        )

    # ---------------------------------
    # Embed
    # ---------------------------------

    @staticmethod
    def embed(
        guild_id,
        channel_id,
        title,
        description,
        colour="#5865F2",
        footer=None,
        thumbnail=None,
        image=None,
    ):

        Queue.push(

            guild_id,

            "SYSTEM",

            "EMBED",

            {

                "guild_id": guild_id,

                "channel_id": channel_id,

                "title": title,

                "description": description,

                "colour": colour,

                "footer": footer,

                "thumbnail": thumbnail,

                "image": image,

            },

        )

    # ---------------------------------
    # Lockdown
    # ---------------------------------

    @staticmethod
    def lockdown(
        guild_id,
        channel_id,
    ):

        Queue.push(

            guild_id,

            "SYSTEM",

            "LOCKDOWN",

            {

                "guild_id": guild_id,

                "channel_id": channel_id,

            },

        )

    # ---------------------------------
    # Unlock
    # ---------------------------------

    @staticmethod
    def unlock(
        guild_id,
        channel_id,
    ):

        Queue.push(

            guild_id,

            "SYSTEM",

            "UNLOCK",

            {

                "guild_id": guild_id,

                "channel_id": channel_id,

            },

        )

    # ---------------------------------
    # Slowmode
    # ---------------------------------

    @staticmethod
    def slowmode(
        guild_id,
        channel_id,
        seconds,
    ):

        Queue.push(

            guild_id,

            "SYSTEM",

            "SLOWMODE",

            {

                "guild_id": guild_id,

                "channel_id": channel_id,

                "seconds": seconds,

            },

        )

    # ---------------------------------
    # Purge
    # ---------------------------------

    @staticmethod
    def purge(
        guild_id,
        channel_id,
        amount,
    ):

        Queue.push(

            guild_id,

            "SYSTEM",

            "PURGE",

            {

                "guild_id": guild_id,

                "channel_id": channel_id,

                "amount": amount,

            },

        )
